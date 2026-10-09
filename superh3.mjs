/** Node.js 20+ native fetch client. No dependencies; only user-authorized paid calls. */
import { randomUUID, createHash } from 'node:crypto';
import { open, link, unlink, readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const uuid = value => {
  if (!/^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(value ?? '')) throw new Error('Expected a UUID.');
  return value;
};
export class SuperH3 {
  constructor({ base = process.env.SUPERH3_BASE_URL || 'https://superh3.com/api/v1', key = process.env.SUPERH3_API_KEY || '', timeout = 30000 } = {}) {
    const url = new URL(base);
    if (url.username || url.password || url.search || url.hash || url.pathname.replace(/\/$/, '') !== '/api/v1' ||
      !(url.protocol === 'https:' || (url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)))) throw new Error('Use HTTPS /api/v1; HTTP is allowed only on localhost.');
    this.base = base.replace(/\/$/, ''); this.key = key; this.timeout = timeout;
  }
  async response(method, path, payload, isPublic = false) {
    if (!path.startsWith('/') || path.includes('..') || path.includes('?')) throw new Error('Invalid API path.');
    if (!isPublic && (!this.key || this.key.startsWith('YOUR_'))) throw new Error('Configure your own SUPERH3_API_KEY.');
    const headers = { Accept: 'application/json', 'User-Agent': 'superh3-agent-kit/2.0.0' };
    if (!isPublic) headers.Authorization = `Bearer ${this.key}`;
    if (payload !== undefined) headers['Content-Type'] = 'application/json';
    let res;
    try { res = await fetch(this.base + path, { method, headers, body: payload === undefined ? undefined : JSON.stringify(payload), redirect: 'error', signal: AbortSignal.timeout(this.timeout) }); }
    catch { throw new Error('Network/redirect failure; retain original request UUID and task ID.'); }
    if (!res.ok) {
      let detail = {}; try { detail = (await res.json()).error || {}; } catch { /* proxy HTML is not a success */ }
      const message = `${res.status} ${detail.code || 'http_error'}: ${detail.message || 'Request failed'}`;
      const error = new Error(this.key ? message.replaceAll(this.key, '[REDACTED]') : message);
      error.status = res.status; error.retryAfter = Math.max(3, Number(res.headers.get('Retry-After') || detail.retry_after || 5));
      throw error;
    }
    return res;
  }
  async request(method, path, payload, isPublic = false) { return (await this.response(method, path, payload, isPublic)).json(); }
  catalog() { return this.request('GET', '/catalog', undefined, true); }
  account() { return this.request('GET', '/me'); }
  estimate({ mode, resolution, seconds, card_id }) { return this.request('POST', '/quotes/estimate', { mode, resolution, seconds, ...(card_id ? { card_id } : {}) }); }
  async quote(request) {
    if (request.accepted_policy !== true) throw new Error('User must accept terms and input rights.');
    const quote = await this.request('POST', '/quotes', request);
    if (!Number.isSafeInteger(quote.cost) || quote.cost < 0 || quote.currency !== 'CNY' || !quote.quote_token) throw new Error('Invalid quote.');
    return quote;
  }
  submit(request, quote, { confirmedCostMicroyuan, confirmedCardUses = 0, userAuthorized }) {
    uuid(request.idempotency_key);
    if (userAuthorized !== true || request.accepted_policy !== true || !Number.isSafeInteger(confirmedCostMicroyuan) || confirmedCostMicroyuan < 0 || quote.cost !== confirmedCostMicroyuan || quote.currency !== 'CNY' || quote.card_uses !== confirmedCardUses || !quote.quote_token) throw new Error('User authorization and exact quoted payment required.');
    return this.request('POST', '/generations', { ...request, quote_token: quote.quote_token });
  }
  async status(id) {
    const result = await this.request('GET', '/generations/' + uuid(id));
    if (!result.data?.[0]) throw new Error('Task not found.');
    return result.data[0];
  }
  async wait(id, timeoutMs = 900000) {
    const end = Date.now() + timeoutMs;
    while (Date.now() < end) {
      let delay = 4000;
      try {
        const task = await this.status(id);
        if (task.state === 'completed') return task;
        if (!['queued', 'preparing', 'submit_intent', 'processing', 'submission_unknown'].includes(task.state)) throw new Error(`Task ${task.state}: ${task.error_code || ''}; no new task created.`);
        if (task.state === 'submission_unknown') delay = 15000;
      } catch (error) { if (error.status !== 429 && !(error.status >= 500)) throw error; delay = error.retryAfter * 1000; }
      await new Promise(resolve => setTimeout(resolve, Math.max(0, Math.min(delay, end - Date.now()))));
    }
    throw new Error('Wait timeout; resume the original task ID: ' + id);
  }
  async download(id, filename) {
    const task = await this.status(id);
    if (task.state !== 'completed' || task.result_available !== true) throw new Error('Video incomplete or unavailable.');
    const res = await this.response('GET', '/assets/' + uuid(task.result_asset_id) + '/file');
    if (!/^(video\/(mp4|webm|quicktime)|application\/octet-stream)(;|$)/.test(res.headers.get('Content-Type') || '')) throw new Error('Expected video data.');
    const partial = filename + '.part', file = await open(partial, 'wx'), hash = createHash('sha256');
    let bytes = 0;
    try { for await (const chunk of res.body) { await file.writeFile(chunk); hash.update(chunk); bytes += chunk.length; } }
    finally { await file.close(); }
    const length = res.headers.get('Content-Length');
    if (!bytes || (length && bytes !== Number(length))) throw new Error('Incomplete download retained as .part.');
    await link(partial, filename); await unlink(partial);
    return { path: filename, bytes, sha256: hash.digest('hex'), task_id: id, local_test: task.local_test === true };
  }
}

// Small CLI, with saved requests/quotes. No default paid generation.
async function main() {
  const [action, ...rest] = process.argv.slice(2), args = {};
  for (let i = 0; i < rest.length; i++) {
    if (!rest[i].startsWith('--')) throw new Error('Use --name value arguments.');
    const name = rest[i].slice(2); args[name] = rest[i + 1]?.startsWith('--') || i === rest.length - 1 ? true : rest[++i];
  }
  const client = new SuperH3(), filename = args.request || 'request.json';
  const digest = data => createHash('sha256').update(JSON.stringify(data)).digest('hex');
  let result;
  if (action === 'prepare') {
    if (typeof args.prompt !== 'string' || !args.prompt.trim()) throw new Error('--prompt required.');
    result = { mode: 'text', prompt: args.prompt, resolution: String(args.resolution || '480'), seconds: Number(args.seconds || 5), aspect: args.aspect || '16:9', accepted_policy: false, idempotency_key: randomUUID() };
    await writeFile(filename, JSON.stringify(result, null, 2), { flag: 'wx' });
  } else if (['estimate', 'quote', 'submit'].includes(action)) {
    const request = JSON.parse((await readFile(filename, 'utf8')).replace(/^\uFEFF/, ''));
    if (action === 'estimate') result = await client.estimate(request);
    else if (action === 'quote') {
      if (args['accept-policy'] === true) { request.accepted_policy = true; await writeFile(filename, JSON.stringify(request, null, 2)); }
      result = await client.quote(request);
      await writeFile(filename + '.quote.json', JSON.stringify({ base: client.base, fingerprint: digest(request), quote: result }, null, 2));
    } else {
      const saved = JSON.parse(await readFile(filename + '.quote.json', 'utf8'));
      if (saved.base !== client.base || saved.fingerprint !== digest(request)) throw new Error('Request/base changed; get a new quote.');
      result = await client.submit(request, saved.quote, { confirmedCostMicroyuan: Number(args['confirmed-cost-microyuan']), confirmedCardUses: Number(args['confirmed-card-uses'] || 0), userAuthorized: args['user-authorized'] === true });
      await writeFile(filename + '.task.json', JSON.stringify(result, null, 2));
    }
  } else if (action === 'catalog') result = await client.catalog();
  else if (action === 'account') result = await client.account();
  else if (action === 'status') result = await client.status(args.id);
  else if (action === 'wait') result = await client.wait(args.id, Number(args.timeout || 900) * 1000);
  else if (action === 'download') { if (!args.output) throw new Error('--output required.'); result = await client.download(args.id, args.output); }
  else throw new Error('Commands: prepare, catalog, account, estimate, quote, submit, status, wait, download');
  console.log(JSON.stringify(result, null, 2));
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main().catch(error => { console.error(error.message); process.exitCode = 1; });

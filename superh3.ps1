# PowerShell 7+. Native HTTP JSON handling avoids curl.exe quoting problems.
[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidateSet('Estimate','Quote','Submit','Status','Download')][string]$Action,
  [string]$RequestFile = 'request.json', [string]$TaskId,
  [switch]$AcceptPolicy, [switch]$UserAuthorized,
  [long]$ConfirmedCostMicroyuan = -1, [ValidateSet(0,1)][int]$ConfirmedCardUses = 0,
  [string]$OutputFile = 'result.mp4'
)
$ErrorActionPreference = 'Stop'
$apiBase = if ($env:SUPERH3_BASE_URL) { $env:SUPERH3_BASE_URL.TrimEnd('/') } else { 'https://superh3.com/api/v1' }
$baseUri = [uri]$apiBase
if ($baseUri.UserInfo -or $baseUri.Query -or $baseUri.Fragment -or $baseUri.AbsolutePath -ne '/api/v1' -or ($baseUri.Scheme -ne 'https' -and -not ($baseUri.Scheme -eq 'http' -and $baseUri.IsLoopback))) { throw 'Use HTTPS /api/v1 or explicit localhost.' }
if (-not $env:SUPERH3_API_KEY) { throw 'Configure your personal SUPERH3_API_KEY in the environment.' }
$headers = @{ Authorization = "Bearer $env:SUPERH3_API_KEY"; 'User-Agent' = 'superh3-agent-kit/2.0.0' }
function Invoke-SuperH3([string]$Method, [string]$Path, $Payload) {
  $options = @{ Uri = "$apiBase$Path"; Method = $Method; Headers = $headers; MaximumRedirection = 0; TimeoutSec = 30 }
  if ($null -ne $Payload) { $options.Body = [Text.Encoding]::UTF8.GetBytes(($Payload | ConvertTo-Json -Depth 30 -Compress)); $options.ContentType = 'application/json; charset=utf-8' }
  try { Invoke-RestMethod @options }
  catch { throw 'API call failed. Inspect account/status and keep the original UUID. No automatic resubmission was attempted.' }
}
function Save-Json($Path, $Value) { $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $Path -Encoding utf8 }
if ($Action -in @('Estimate','Quote','Submit')) {
  $request = Get-Content -LiteralPath $RequestFile -Raw | ConvertFrom-Json -AsHashtable
  [void][guid]::Parse($request.idempotency_key)
  if ($Action -eq 'Estimate') {
    $preview = @{ mode=$request.mode; resolution=$request.resolution; seconds=$request.seconds }
    if ($request.card_id) { $preview.card_id=$request.card_id }
    $result = Invoke-SuperH3 POST '/quotes/estimate' $preview
  } elseif ($Action -eq 'Quote') {
    if ($AcceptPolicy) { $request.accepted_policy = $true; Save-Json $RequestFile $request }
    if ($request.accepted_policy -cne $true) { throw 'Review terms and input rights, then pass -AcceptPolicy.' }
    $result = Invoke-SuperH3 POST '/quotes' $request
    Save-Json "$RequestFile.quote.ps.json" @{ base=$apiBase; request_hash=(Get-FileHash -LiteralPath $RequestFile -Algorithm SHA256).Hash; quote=$result }
  } else {
    $saved = Get-Content -LiteralPath "$RequestFile.quote.ps.json" -Raw | ConvertFrom-Json
    if (-not $UserAuthorized -or $ConfirmedCostMicroyuan -lt 0 -or $request.accepted_policy -cne $true -or $saved.base -ne $apiBase -or $saved.request_hash -ne (Get-FileHash -LiteralPath $RequestFile -Algorithm SHA256).Hash -or $saved.quote.currency -ne 'CNY' -or $saved.quote.cost -ne $ConfirmedCostMicroyuan -or $saved.quote.card_uses -ne $ConfirmedCardUses -or -not $saved.quote.quote_token) { throw 'Exact confirmed quote, unchanged request and user authorization required.' }
    $request.quote_token = $saved.quote.quote_token
    $result = Invoke-SuperH3 POST '/generations' $request
    Save-Json "$RequestFile.task.json" $result
  }
} else {
  [void][guid]::Parse($TaskId)
  $result = Invoke-SuperH3 GET "/generations/$TaskId" $null
  if ($Action -eq 'Download') {
    $task = $result.data[0]
    if ($task.state -ne 'completed' -or $task.result_available -cne $true) { throw 'Result is incomplete or unavailable.' }
    [void][guid]::Parse($task.result_asset_id)
    if ((Test-Path -LiteralPath $OutputFile) -or (Test-Path -LiteralPath "$OutputFile.part")) { throw 'Choose a new output filename.' }
    $response = Invoke-WebRequest -Uri "$apiBase/assets/$($task.result_asset_id)/file" -Headers $headers -MaximumRedirection 0 -TimeoutSec 180 -OutFile "$OutputFile.part" -PassThru
    if ($response.Headers['Content-Type'] -notmatch '^(video/|application/octet-stream)') { throw 'Expected video data; retained .part file.' }
    [IO.File]::Move([IO.Path]::GetFullPath("$OutputFile.part"), [IO.Path]::GetFullPath($OutputFile), $false)
    $result = @{ path=[IO.Path]::GetFullPath($OutputFile); sha256=(Get-FileHash -LiteralPath $OutputFile -Algorithm SHA256).Hash; local_test=$task.local_test }
  }
}
$result | ConvertTo-Json -Depth 30

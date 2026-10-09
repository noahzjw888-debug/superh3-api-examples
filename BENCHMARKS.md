# 样片与测速 / Samples and measurement

本包引用官网已有公开样片，见 samples.json。没有为宣传重新生成视频，没有公开用户私有任务。未取得历史费用和处理耗时，所以这两个字段为空。样片说明视觉效果，不证明目前套餐价格或处理速度。
This package references existing public showcase clips in samples.json, not private user jobs. Historical cost and processing time are unavailable and remain null. Clips illustrate appearance, not current price or processing latency.

运营方参考值：15秒输出在1080P/768P/480P约30/20/10秒，非独立压测。不要把文件下载速度、模拟 HTTP 测试或最短单次结果说成上游生成速度。
Operator reference estimates for 15s output are 30/20/10s at 1080P/768P/480P. These are not independent benchmarks. Download speed, mocked tests and the best single run are not evidence of upstream generation speed.

可复现测速应事先确认预算和公开授权，固定提示词、输入素材、时长、分辨率、账号等级，记录全部样本（含失败/超时）、日期和费用。分别报告提交到完成的总耗时、排队、素材准备、生成等待；上游没有提供的纯计算时间保持未知。至少报告样本数、完成率、median 和 P95，并明确样本量局限。未知任务继续查询原 ID，不重新扣费。
A reproducible paid benchmark needs budget and publication consent. Fix prompt, assets, duration, resolution and tier. Record every attempt, including failures/timeouts, dates and costs. Separate end-to-end latency, queue, preparation and generation waiting. Keep unavailable upstream compute time unknown. Report sample count, completion rate, median and P95 with sample-size limitations. Poll unknown tasks by their original IDs.

本轮没有完成新的真实上游测速；没有虚构速度、成功率、用户评价或竞争对手比较。
No new live upstream benchmark was performed in this release. No invented latency statistics, success rates, testimonials or competitor comparisons are published.

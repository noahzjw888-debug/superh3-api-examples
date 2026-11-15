# 样片与处理耗时 / Samples and processing latency

当前没有发布可复现的生成延迟基准。历史宣传速度估算已撤下，不能据此推断当前任务完成时间。输出时长与服务处理耗时是不同指标。

No current generation-latency benchmark is published. Historical promotional estimates have been withdrawn and should not be used to predict current completion times. Output duration is not processing latency.

`samples.json` 引用官网已有公开案例，不是本轮重新生成的视频，也不是私有用户任务。未知历史费用与耗时保持null。样片展示外观，不能证明当前费用、稳定性或处理速度。

Mock HTTP/client tests validate request, consent, price and recovery handling only. They do not measure upstream video generation. A paid benchmark needs explicit budget and publication permission, fixed prompt/reference/duration/quality, every attempt including failures, actual costs and separate queue/preparation/generation/download timing. Report sample size, completion rate, median and P95 with limitations. Unknown tasks must be recovered using their original ID.

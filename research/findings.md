# findings.md — 4x5090 (128GB VRAM) — v0 after round 1
Every claim cites its source inline. GAP = no direct measurement found yet (must fill or label in report).

## C1. 128GB 的三类甜蜜区模型（按参数量级）
- **125B MoE (Qwen3.8-Flash-Next)**: NVFP4 全入 VRAM，r10 配方 decode 319-331 t/s、prefill ~7.8K、393K ctx — https://github.com/abtraore/QWEN-PEDIA (recipes/qwen3.8-flash-next)
- **284B MoE (DeepSeek V4 Flash)**: 单5090+128GB RAM 实测 18 t/s decode / 112 pp（权重放 RAM）— https://www.reddit.com/r/LocalLLM/comments/1vlk9bi/ ；1M ctx 单卡 offload 800pp/15+tg — https://www.reddit.com/r/LocalLLaMA/comments/1vfbcgx/ ；4x5090 全显存配置 = 理论大跃升，**GAP: 无 4x5090 直接实测**
- **397B-A17B MoE (Qwen3.5)**: 单 5090 = 20 t/s tg / 700 pp — https://www.reddit.com/r/LocalLLaMA/comments/1s32orn/ ；4x PRO 6000(SM120) 调优后 282 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1rtrdsv/ ；Q2 级"shockingly useful" — https://www.reddit.com/r/LocalLLaMA/comments/1se4m16/ ；1M 上下文 — https://www.reddit.com/r/LocalLLaMA/comments/1r6qy55/ 。4x5090 Q2 档 (~124GB) 恰好全显存，**GAP: 无人发过 4x5090 跑 397B 的 tok/s**

## C2. SM120 NVFP4 生态坑（全部一手）
- CUTLASS Grouped GEMM 在 SM120 出乱码，FlashInfer patch 修 — https://www.reddit.com/r/LocalLLaMA/comments/1roqkw4/
- NVFP4 在 SM120 不比 FP8 快（Qwen3.6-27B 实测）— https://www.reddit.com/r/Vllm/comments/1uki6f8/
- vLLM v0.12.0 起支持 SM120 NVFP4 — https://www.reddit.com/r/LocalLLaMA/comments/1pe4xm4/ ；llama.cpp MMQ 已合并 — https://www.reddit.com/r/LocalLLaMA/comments/1syjflw/
- fp8 MTP 缺陷吃 40% 吞吐（PRO6000 TP2）— https://github.com/untcoder2/qwen38-flash-next-nvfp4-sm120-tp2

## C3. spec-decode/MTP 是 SM120 多卡的胜负手
397B 调优核心是 MTP 档位表（282 t/s 帖）；GLM-5.2 MTP mystery 帖 https://www.reddit.com/r/LocalLLaMA/comments/1um6pea/ ；反面：4xR9700 spec 无效 — https://www.reddit.com/r/LocalLLM/comments/1td57b2/

## C4. 多实例路线（吞吐/团队场景）
单 5090 跑 Qwen3.8-27B：144-256 t/s prose/code，双 slot 256-451 — https://www.reddit.com/r/LocalLLaMA/comments/1w2g5se/ ；NVFP4+spec 616 t/s c4 — https://www.reddit.com/r/Vllm/comments/1vy9cqt/ 。4x5090 = 4 个独立 27B 实例或 2 大 + 2 小混搭。团队 50 人 4x5090 整机案例 — https://www.reddit.com/r/LocalAIServers/comments/1wuvbe5/

## C5. 扩散/视频不走多卡 TP，走单卡满配
wan2.2 5090 64s/clip — https://www.reddit.com/r/StableDiffusion/comments/1uh0yk1/ ；LoRA 训练 16GB 即可 — https://www.reddit.com/r/StableDiffusion/comments/1lzilsv/ ；AMD 在 diffusion 落后 — https://www.reddit.com/r/StableDiffusion/comments/1mm4dzs/ （另见 skill 既有实测：双卡拆分反而更慢）

## C6. 对照路线：PRO 6000 与 AMD
5090x4 vs PRO6000x4 长期争论（带宽 vs 容量）— https://www.reddit.com/r/LocalLLaMA/comments/1oa4zsv/ + apxml calculator；4xR9700 384GB $10.7k 全 AMD 路线 — https://www.reddit.com/r/LocalLLaMA/comments/1x67qeu/

## C7. 方法论锚
社区数字不可比（引擎/条件不同）— https://www.reddit.com/r/LocalLLM/comments/1x99oeu/ （Oct 2026 引擎综述）；交叉引用审计发现 11/64 链接错误 — https://www.reddit.com/r/LocalLLM/comments/1vux9f6/ （报告必须逐链验证）

## C8. 真实 agent 并发曲线（一手运维数据）
2x5090 团队机（4x5090 半配）：短上下文 24 并发 52 t/s；100K 上下文 8 并发 4.3 t/s；25-50K agentic 15.3 t/s — https://www.reddit.com/r/LocalAIServers/comments/1wuvbe5/ （评论树已存档 comments/1wuvbe5.json）。结论：agent 负载并发瓶颈 = prefill + KV 带宽，不是权重放置。4x5090 的 2x prefill 直接买并发。
并发 staging 反例数据：8x5090 DSV4.1-Flash 128 并发时 TTFT 56.2s→3.6s（prefill staging），但每 token 时间 +62.6% — https://github.com/devin-lai/DeepSeek-V4.1-Flash-Accel

## C9. DSV4.1-Flash 在 5090 级硬件的实测锚（GAP 闭合）
- 8x5090 (256GB) 调优：单流 97.2 t/s，8 并发聚合 247.8 t/s，8K prefill 3145 t/s — https://github.com/devin-lai/DeepSeek-V4.1-Flash-Accel
- 1x5090+126GB RAM+NVMe expert streaming：新内容 5.12 t/s，驻留 21.27 t/s（502GB GGUF, llama.cpp dsv41-porte 分支）— https://github.com/JigSawPT/deepseek-v41-flash-on-5090
- AFD 异构：1x5090 coordinator + 4x DGX Spark experts：86.9 t/s decode，1M prefill 271.7s — https://github.com/hughmadden/ds41rt-rtx5090 （上游 tpurtell/ds41rt）
- 量化档：原生 MXFP4 ≈154GB > 128GB；AtomicChat 104GB 档 top-1 损失 ~4% — https://www.reddit.com/r/LocalLLaMA/comments/1vlurlv/ （评论树 comments/1vlurlv.json）→ 4x5090 全显存跑 DSV4.1 = 必须 104GB 档或 GSQ
- **4x5090 本机直接实测：社区不存在（GAP，已穷举搜索 "4x5090 deepseek" 等），只能按上述锚推算**

## C10. 397B-A17B 量化阶梯（决定 128GB 内放哪一档）
UD-Q8_K_XL 400GB → 18.6 t/s（双5090+512GB RAM offload）；MXFP4_MOE 202GB → 32 t/s（同机）— https://www.reddit.com/r/LocalLLaMA/comments/1s32orn/ 评论树 comments/1s32orn.json；DGX Spark 单卡 UD-IQ2_XXS：500pp/20tg；Q4_M 服务器 $12k：700pp/20tg。128GB 全显存对应 IQ2/Q2 档（"shockingly useful at Q2" — 1se4m16）。DDR 定律：8 通道 DDR4 > 高端双通道 DDR5（offload 场景）— 同帖评论。

## C11. SM120 kernel 级根因（不止现象）
'failed to initialize cutlass TMA WS' = CUTLASS K=64 tile 的 SMEM 假设超 SM120 上限；scale-layout patch 修，作者发 docker — https://www.reddit.com/r/LocalLLaMA/comments/1rtrdsv/ 评论树 comments/1rtrdsv.json + https://github.com/untcoder2/qwen38-flash-next-nvfp4-sm120-tp2
PCIe5 对 4xPRO6000 TP 是真瓶颈（原话），等效 5090 需 12 卡才同显存 — 同帖。

## C12. 引擎生态碎片化（Oct 2026）
NInfer ~600 forks、strata-nvfp4 fork 常见于 5090、ROCm paiton 700pp c8/275tg、Paddock 新引擎 — https://www.reddit.com/r/LocalLLM/comments/1x99oeu/ + comments/1x99oeu.json；4x5090 开源机箱设计 — https://github.com/autonomous-ai/autonomous-computer/tree/main/4x-5090

## C13. YaRN/CTX 档位：社区三派实证（round-4，语料 1074）
- 保守 serving 派：r10 factor 1.5 唯一深度验收档；8x3090 用户 261K 原生+关MTP "rock solid" — https://www.reddit.com/r/LocalLLaMA/comments/1w0xzxu/ ；LMStudio 微调用 --yarn-attn-factor 1.2 — https://www.reddit.com/r/LocalLLaMA/comments/1wdq136/
- 大上下文爱好者派（全部单机/dense 栈，无 vLLM NVFP4+TP4 深度验收）：Strix Halo 1M=38t/s+18min prefill — https://www.reddit.com/r/LocalLLaMA/comments/1wkyny9/ ；TensorFold Metal 1,048,576 YaRN×4 — https://github.com/ashhart/TensorFold/pull/1005 ；NInfer 双5090 1M 27B(dense) — https://www.reddit.com/r/LocalLLaMA/comments/1w1txyk/
- 共同雷区：vLLM 已知 bug YaRN 升档后 MTP drafter 仍按 262K 创建（target/draft 脱节，有 issue+PR）— 1w0xzxu 评论树；Ollama mlx runtime 静默忽略 YaRN — https://github.com/ollama/ollama/issues/19129 → https://github.com/ollama/ollama/pull/19134
- needle 验收协议（r10 NOTES 第3门）：最大上下文 50% 和 95% 深度各埋针，exact string 命中才算过；判读表：50过95丢=降档；全丢=rope override 未生效；needle 好但 acceptance=0.000=drafter 未 pin（速度问题非质量问题）。

## C14. 4x5090 显存预算（NVFP4 r10，全部一手数字）
- checkpoint 仓库 132.7 GB（HF usedStorage）；其中 PLE n-gram 表 47.68 GiB 走 host RAM mmap/UVA → GPU 驻留权重 ≈85 GB（含 bf16 豁免投影 4.2+1.23 GB）
- 可用 ~135 GB；默认 KV_BYTES 6e9 → 用量 103-108 GB，余量 ~20-25 GB
- KV 单价 8.15 KB/token（6.0e9/736,359，QSA/GDN 混合注意力压小 KV）：393K 会话=3.2 GB、1M=8.2 GB
- 余量最优用法=并发不是深度：KV_BYTES→18-20 GB ≈5-6 并发 393K 会话；vLLM util 0.9 墙 ≈115 GB，留 ≥8 GB 缓冲（NOTES 有 40 MiB 级 OOM 崩溃记录）
- Hermes 侧联动：max_concurrent_children 本机=2（config.yaml，旧版默认3，现默认10无硬顶）；parent+children=N+1 条会话，每条约 8.15KB/token，与 KV_BYTES 预算同盘棋

## C15. Hermes 子代理数量：能开几个、社区设几个（round-5，语料 1137）
- 代码实值（本机 main 源码 + 官方 issue 确认）：`tools/delegate_tool_config.py:17` `_DEFAULT_MAX_CONCURRENT_CHILDREN = 10`；floor=1、**无硬上限**；`max_spawn_depth` 默认 1（平面），floor 1 无上限；v32→v33 迁移把默认从 3 提到 10 — https://github.com/NousResearch/hermes-agent/issues/125131 （部分文档页/捆绑 skill 仍写 3，官方承认 docs drift — #125183）
- 官方两页 [Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation) / [Patterns](https://hermes-agent.nousresearch.com/docs/guides/delegation-patterns)：默认 10 并行、"children 烧掉一次 run 的大部分 token"、`delegation.model` 给 worker 挂便宜模型、每 child `max_iterations` 默认 250、leaf 屏蔽 delegate/clarify/memory/send_message/cronjob、delegate 不 durable（跨进程活=kanban/cron）
- 官方全部示例 = 3-5 任务/批。真实天花板是主机资源不是配置：官方 fanout benchmark 用 24 children 量 threads/RSS/fd/TCP/pyright 进程
- 社区实践（3 个 megathread 评论树全文挖掘，无人报具体数字，谈的是模式）：durable 用 Kanban 不用 delegate_task（对比表在帖内）；worker 挂便宜模型省钱实测（deepseek flash 当子代理 $2 vs 不 delegate $6.50）；特殊化用 profile；"subagent 仍带 Hermes 注入=上下文膨胀，重度场景转外部 harness" — https://www.reddit.com/r/hermesagent/comments/1ucmvi8/ + https://www.reddit.com/r/hermesagent/comments/1ud03si/ + https://www.reddit.com/r/hermesagent/comments/1wk2q5e/
- 本地模型用户（Harry 场景）的换算：每个子代理=一条独立会话（parent+children=N+1 条），上限实际由 KV 池决定：4x5090 r10 KV 18-20GB ≈ 5-6 条 393K 会话 → 建议 max_concurrent_children=4（本机现 config=2，历史默认 3，现默认 10）

## C16. SM120 fp8 MTP 缺陷：完整根因链（一手 docs/MTP.md）
官方 NVFP4 checkpoint 把 MTP draft MoE experts 存成 fp8 `FP8_PB_WO`（1,536 个 weight_scale_inv 全在 mtp.*）→ vLLM ModelOpt MoE 分支不认识该算法 → experts 未量化构建、fp8 权重无 scale 加载 → drafter 噪声、accept 1.50（应 ~3.0）、decode −40%（124.8 vs 214.8），全程静默；质量 20/20 不受影响（exact verification）。SM120 三条 runner 全断（Triton=illegal mem、DeepGEMM=CUDA719、flashinfer_cutlass 无实现）= 支持矩阵空格；两 runtime 独立复现。运行名字陷阱：FP8_PB_WO 运行时变 FP8_BLOCK_SCALES。修复：BF16 移植（accept 3.06）→ 2026-10-19 NVIDIA QAD FP4-Local 自带训好的 NVFP4 draft head（BF16 化后 accept 4.51、412.5 tok/s）成为正解。三症状对照：accept≈1.5=本缺陷；0.000@>原生=drafter length pin 丢失；2.5-3.0=健康。Strata 自带 kernel 不受影响。
链接：https://github.com/untcoder2/qwen38-flash-next-nvfp4-sm120-tp2 + /blob/main/docs/MTP.md

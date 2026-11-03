# 4×RTX 5090（128 GB VRAM）能干什么、部署什么模型 — 完整研究报告

Harry · 2026-10-19 · 证据库 1096 条去重来源（GitHub 718 / Reddit 238 / HuggingFace 模型卡 140，另有 11 个评论树存档），另有 5 个头部帖完整评论树存档于 `comments/`。全部来源索引见 `links.md`，原始记录见 `sources.jsonl`。

## 0. 方法与口径
- 每条结论附可点开链接；同一结论要求 ≥2 个独立来源，或 1 个一手实测（README/评论树里的原始数字）。
- 数字不可比是社区常态（引擎、量化、上下文、并发定义都不同）— 这正是有人审计出"60 个帖子里 11/64 个引用链接是错的"的原因（https://www.reddit.com/r/LocalLLM/comments/1vux9f6/）。本报告所有 tok/s 都注明量化档与配置。
- "GAP" = 全网穷举后仍不存在的直接实测，报告明说并给出最近锚点推算。

---

## 1. TL;DR
1. **128 GB 的第一用途不是"装下更大的单一模型"，而是同一模型的更高量化档 + 更长上下文 + 更高并发。** agent 负载（你的 Hermes 场景）瓶颈是 prefill 和 KV 带宽，4 卡 prefill ≈2×，直接换并发能力。
2. **你这台的最优主模型不变：Qwen3.8-Flash-Next NVFP4 + QWEN-PEDIA r10 + vLLM TP4+EP**，decode 319–331 t/s、prefill ~7.8K、393K ctx — https://github.com/abtraore/QWEN-PEDIA （recipes/qwen3.8-flash-next，r10 为当前最新，已复核 README）。
3. **第二大脑候选 = DeepSeek-V4.1-Flash**：长程 agentic coding 高一档，但全量放不进 128 GB——只有 104 GB 量化档（top-1 −4%）或 GSQ 档能全显存，代价是速度 — C3 节全部实测链接。
4. **Qwen3.5-397B-A17B（1M ctx）是 128 GB 能"全显存硬塞"的上限旗舰**：IQ2/Q2 档 ~120 GB，社区称 Q2 "shockingly useful"（https://www.reddit.com/r/LocalLLaMA/comments/1se4m16/ ），但 SM120 上 MoE 坑多、decode 参考锚只有 20–32 t/s，对 agent 用途不如前两者。
5. **非 LLM 负载（视频/图像/训练）在 4 卡机上走"每卡一个实例"，不走 TP。** 扩散模型多卡 TP 无收益甚至倒退（skill 既有双卡实测 + https://www.reddit.com/r/StableDiffusion/comments/1mm4dzs/ ）。
6. **SM120（5090 家族）是量化生态的一等公民但坑密**：CUTLASS tile bug、NVFP4≠加速、fp8 MTP −40%，全部有 kernel 级根因，见 C5。

---

## 2. 128 GB 显存的能力分层（装什么、跑多快）

### 2.1 舒适区：100–130B MoE，高量化 + 超长上下文 + 并发
| 模型 | 全显存档位 | 实测锚 |
|---|---|---|
| Qwen3.8-Flash-Next 125B | NVFP4 ~70 GB | 4×5090 配方 decode 319–331 t/s / prefill 7.8K / KV 池 736K tokens — QWEN-PEDIA r10（上链）；单 PRO6000 240 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1w39ojn/ ；vs 27B FP8 对比 — https://www.reddit.com/r/LocalLLaMA/comments/1w2z2zo/ |
| Qwen3.8-27B（dense） | 每卡一份，4 实例 | 单 5090：144–256 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1w2g5se/ ；NVFP4+NVFP4KV+DFlash2 spec：616 t/s @c4、262K — https://www.reddit.com/r/Vllm/comments/1vy9cqt/ ；真实 262K 无 spec：77/64.7 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1vvl7pc/ |
| Qwen3.5-122B-A10B | FP8/NVFP4 | 2×PRO6000 198 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1sh7yxa/ （4×5090 显存更宽裕） |

### 2.2 极限区：280–400B MoE（要选档、要换架构）
**DeepSeek-V4.1-Flash（552B 总/284B 激活级 MoE）** — 4×5090 可行但必须选边：
- 全显存唯一路：AtomicChat 104 GB 量化档（相对 154 GB MXFP4 档 top-1 损失 ~4%，作者原话"这 50 GB 是很多人能跑和不能跑的区别"）— https://www.reddit.com/r/LocalLLaMA/comments/1vlurlv/
- NVMe 流式档：单 5090 + 126 GB RAM 跑 502 GB GGUF：新内容 5.12 t/s / 驻留 21.27 t/s（llama.cpp `dsv41-porte`，llama.cpp#28766）— https://github.com/JigSawPT/deepseek-v41-flash-on-5090
- 8×5090 直接实测（不是 4 卡但同源硬件）：调优后单流 97.2 t/s、8 并发 247.8 t/s、8K prefill 3145 t/s — https://github.com/devin-lai/DeepSeek-V4.1-Flash-Accel
- AFD 异构：1×5090 coordinator + 4×DGX Spark experts：decode 86.9 t/s、1M prefill 271.7 s — https://github.com/hughmadden/ds41rt-rtx5090
- **GAP：4×5090 跑 DSV4.1 的直接 tok/s 全网不存在**（穷举 `"4x5090 deepseek"`、`deepseek v4 "4 gpu"` 等，仅 8 卡与 offload 锚）。按 8 卡锚/带宽推算，104 GB 档 TP4 全显存大概率 60–90 t/s 单流区间——标注为推算，非实测。
- 质量对照（已有结论）：同 harness Gauntlet 下 DSV4.1 GSQ 6.20 vs Flash-Next IQ3_XXS 5.50 vs API 6.41；差距集中在长程 agentic，thinking token 多 3–12×。

**Qwen3.5-397B-A17B（1M ctx）** — 128 GB 恰好卡在 IQ2/Q2 全显存线：
- 单 5090：20 t/s tg / 700 pp — https://www.reddit.com/r/LocalLLaMA/comments/1s32orn/ ；评论树给了完整阶梯：UD-Q8_K_XL 400 GB→18.6 t/s、MXFP4_MOE 202 GB→32 t/s（双5090+512GB offload，8ch DDR4）；DGX Spark UD-IQ2_XXS 500pp/20tg；`-ub` 调大 PP 可到 800+。
- 4×PRO6000（同为 SM120，384 GB）调优后 282 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1rtrdsv/ ；同作者 8 小时全后端 bakeoff 上限 50.5 t/s（未调优态）— https://www.reddit.com/r/LocalLLaMA/comments/1rrfqlu/
- Q2 可用性 — https://www.reddit.com/r/LocalLLaMA/comments/1se4m16/ ；NVFP4 变体 — https://www.reddit.com/r/LocalLLaMA/comments/1ri9enf/ ；1M ctx — https://www.reddit.com/r/LocalLLaMA/comments/1r6qy55/
- **GAP：4×5090 + 397B 的直接实测同样不存在。** 128 GB 只能装 IQ2 档，按 Spark 锚 ≈20 t/s tg / 500 pp，TP4 全显存的收益主要在 prefill 与 KV，不是 decode（带宽定律）。agent 用途上该档质量存疑——27B vs 397B 之争（1175 up）说明小模型+好 harness 常胜 — https://www.reddit.com/r/LocalLLaMA/comments/1st11lp/

### 2.3 4 实例并行区（吞吐/服务场景）
- 2×5090 团队机一手运维数据：短 ctx 24 并发 52 t/s；100K ctx 8 并发 4.3 t/s；25–50K agentic 15.3 t/s — https://www.reddit.com/r/LocalAIServers/comments/1wuvbe5/ （完整 120 条评论树已存档）。整条帖子就是 "4×5090 128GB 服务 50 人" 实建，机箱开源：https://github.com/autonomous-ai/autonomous-computer/tree/main/4x-5090
- 4×5090 的合理团队配方：TP4 跑 Flash-Next 主 brain + 弹性时切 2×(TP2×122B) 或 4×(27B)。并发第一约束是 prefill：staging 技巧可把 128 并发 TTFT 从 56.2 s 压到 3.6 s（8×5090 实测，代价 per-token +62.6%）— devin-lai（上链）。

---

## 3. 结论：这台机器部署什么（按用途）
1. **Hermes 主脑（agent，24/7）**：Qwen3.8-Flash-Next NVFP4，r10 配方，TP4+EP 单实例。显存余量全部换成 YaRN 393K + KV 池 + 并发。前提：125 GB host RAM（48 GB PLE 表 mlock）、Ubuntu、aikitoria P2P。MTP 必须 A/B（见 C5）。
2. **编码特化第二脑**：DSV4.1-Flash 104 GB 档（全显存）或等 4×5090 实测出现再调档。质量增益方向明确、速度税明确。
3. **吞吐服务**：4×Qwen3.8-27B NVFP4（每卡 1 实例 + spec decode），聚合吞吐最高、延迟最低。
4. **视频/图像/LoRA**：每卡一个 ComfyUI/wan2.2 实例；wan2.2 5090 单卡 64 s/clip — https://www.reddit.com/r/StableDiffusion/comments/1uh0yk1/ ；T2V LoRA 训练 16 GB 就能做 — https://www.reddit.com/r/StableDiffusion/comments/1lzilsv/ ；4 卡=4 条生产线，不是 1 条 4 倍快的线。

---

## 4. 对照路线（为什么不换别的）
- **4×RTX PRO 6000（96GB×4=384 GB）**：唯一优势是显存总量（能全显存跑 397B Q4/MXFP4 与 DSV4.1 原生档），带宽/GDDR7 与 5090 同级，价格贵 ~2×。社区长期争论点即"容量 vs 每 GB 成本" — https://www.reddit.com/r/LocalLLaMA/comments/1oa4zsv/ + apxml 计算器；"等效 5090 需要 12 张才同显存"是 PRO6000 用户的原话（1rtrdsv 评论树）。
- **全 AMD（4×R9700 384 GB，$10.7k 含 $127 二手 EPYC）**：容量便宜一半，但 diffusion/生态明显落后，SM120 的 kernel 坑换成 ROCm 坑 — https://www.reddit.com/r/LocalLLaMA/comments/1x67qeu/ ；spec decode 在 4×R9700 上无效应 — https://www.reddit.com/r/LocalLLM/comments/1td57b2/ ；397B 在 16×MI50 能跑 32 tg 但工程量荒谬 — https://www.reddit.com/r/LocalLLaMA/comments/1s9ivgl/
- **Mac Studio / DGX Spark / Strix Halo**：统一内存容量大、prefill 弱（397B 锚：M3U 512GB 与 dual Spark 对比 — https://www.reddit.com/r/LocalLLaMA/comments/1s4lmep/ ；Strix Halo 17–19 t/s — https://www.reddit.com/r/LocalLLaMA/comments/1s2rtux/ ）。对"24/7 agent + 高并发"组合，4×5090 的 prefill/带宽仍占优（https://www.reddit.com/r/better_claw/1wsaiiy/ 的功耗+tok/s 全账）。
- **DDR 定律（offload 路线）**：8 通道 DDR4 > 高端双通道 DDR5；Flash-Next 的 expert miss 对 RAM 延迟极敏感（Strata 作者观点，评论树）— 1x99oeu / 1s32orn 评论树。你现有 96 GB 非 ECC 只影响 offload 玩法，不影响 NVFP4 全显存路线。

---

## 5. SM120 坑典（全部一手，装机前必读）
1. **CUTLASS Grouped GEMM 在 SM120 出乱码**：根因 = K=64 tile 的 SMEM 假设超出 SM120 上限，报错 `failed to initialize cutlass TMA WS`；FlashInfer SM120 patch / scale-layout 修复 — https://www.reddit.com/r/LocalLLaMA/comments/1roqkw4/ + https://www.reddit.com/r/LocalLLaMA/comments/1rtrdsv/ 评论树。
2. **NVFP4 在 SM120 上并不比 FP8 快**（dense 27B 实测）— https://www.reddit.com/r/Vllm/comments/1uki6f8/ ；NVFP4 的价值 = 显存 + KV cache 量化 — https://www.reddit.com/r/LocalLLaMA/comments/1u95f3f/ ；支持线：vLLM v0.12+ — https://www.reddit.com/r/LocalLLaMA/comments/1pe4xm4/ ，llama.cpp MMQ 已合并 — https://www.reddit.com/r/LocalLLaMA/comments/1syjflw/
3. **fp8 MTP 缺陷可吃 40% 吞吐**（5090 同族 TP2 实测）— https://github.com/untcoder2/qwen38-flash-next-nvfp4-sm120-tp2 ；MTP 在 SM120 上时灵时不灵（GLM-5.2 四 Spark 悬案最终靠档位表解决 — https://www.reddit.com/r/LocalLLaMA/comments/1um6pea/ ）。**r10 部署必须 MTP on/off 各跑一遍 harness。**
4. **PCIe 是 TP 上限**：PCIe5 被 4×PRO6000 TP 用户点名是真瓶颈（1rtrdsv 评论树）；无 P2P 的 TP 惩罚实测 4–21%（MTP3 下更大）— https://www.reddit.com/r/LocalLLM/comments/1wpr2bk/ ；跨机器 TP 灾难 — https://www.reddit.com/r/LocalLLaMA/comments/1v7t7dn/ 。你的 PEX88096 全 PIX 拓扑正是对症。
5. **异构/混搭 TP 有成熟支线**（shvllm、htsglang、NInfer ~600 分支生态）— https://www.reddit.com/r/Vllm/1uuiixl/ + https://www.reddit.com/r/LocalLLM/1uwazz9/ + https://www.reddit.com/r/LocalLLM/comments/1x99oeu/

---

## 6. GAP 清单（穷举后仍无直接实测，报告中已按锚推算并标注）
1. 4×5090 跑 Qwen3.5-397B-A17B 的 tok/s（最近锚：4×PRO6000 282 t/s@384GB、单5090 20 t/s、Spark IQ2 20 t/s）。
2. 4×5090 跑 DSV4.1-Flash 的 tok/s（最近锚：8×5090 97/248 t/s、1×5090 AFD 86.9、NVMe 流 5–21）。
3. 4×5090 的 PEX88096 Gen4 岛 vs 原生 Gen5 x16 主板的 TP 吞吐差（社区无此拓扑，aikitoria 文档为最接近来源；已在 plan-lite 里列为 Phase-0 验证项）。

## 7. 对你的机器的行动建议（证据链收口）
- 部署顺序：Phase-0 零成本验证（plan-lite 既定）→ r10 NVFP4 起机 → MTP A/B → 记录 3 项 GAP 数据（你就是全网第一个 4×5090+PEX88096 数据源，发回 Reddit/GitHub 即补上这些 GAP）。
- 验收线不变：decode ≥290 t/s、prefill ~7.8K、并发按 2×5090 锚点 ×2 prefill 预估。

## 8. YaRN 档位与社区实践分布（round-4 补充，2026-10-19）
**结论：4×5090 用 CTX=393216（static YaRN factor 1.5）；官方原则"factor 按典型上下文设"（典型 524K 才设 2；1M 属 Qwen3.8-Flash 生产版，Next 在 NVFP4+vLLM 栈上无任何 1M 深度验收 = GAP）— [官方卡](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)。**
- 社区三派：保守 serving 派（r10 1.5× / 261K 原生+关MTP "rock solid" — [1w0xzxu](https://www.reddit.com/r/LocalLLaMA/comments/1w0xzxu/) / LMStudio 1.2×）；大上下文爱好者派（Strix Halo 1M 38 t/s — [1wkyny9](https://www.reddit.com/r/LocalLLaMA/comments/1wkyny9/)；[TensorFold YaRN×4 PR#1005](https://github.com/ashhart/TensorFold/pull/1005)；全部 dense/单机栈）；两派共同踩的坑：vLLM YaRN 升档后 MTP drafter 仍按 262K 创建（已知 bug 有 PR）、[Ollama mlx 静默忽略 YaRN](https://github.com/ollama/ollama/issues/19129)。
- **needle 验收协议**（换任何档位必跑）：草堆=扰动过的自然文本（防 prefix cache），针=唯一 KV；最大上下文 50% 和 95% 深度各一针，temp 0，**逐字命中才算过**；同时跑短上下文对照组（算术/tool-call/短QA）——static YaRN 伤短文本是官方明示。判读：50 过 95 丢=降档；全丢=override 没生效；needle 好但 `/metrics` acceptance=0.000=drafter 未 pin max_model_len（速度死了脑子没死）。

## 9. 显存预算与 KV 并发（一手数字）
仓库 132.7 GB（[HF](https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4)）中 47.68 GiB PLE 表住 host RAM → GPU 权重 ≈85 GB；135 GB 可用 − 权重 85 − 开销 10–12 − KV 6 = **余量 20–25 GB**。KV 单价 8.15 KB/token：393K 会话 3.2 GB / 1M 会话 8.2 GB。**1M 不是显存问题，是质量验收问题。** 余量花法：`KV_BYTES` 6→18–20 GB = 5–6 条并发 393K 会话（agent 场景最优兑换率），留 ≥8 GB 缓冲（util 0.9 墙 + 40 MiB OOM 前科）。Hermes 子代理（本机 cap=2）每开一个多一条会话——并发会话数、KV_BYTES、max_concurrent_children 三个数要同盘规划。

## 附录
- 全部 938 条来源索引：`links.md`（同目录）
- 原始 JSON：`sources.jsonl`（去重键 = URL）
- 评论树存档：`comments/1wuvbe5.json`（120 条）、`1rtrdsv.json`（89）、`1s32orn.json`（64）、`1vlurlv.json`（86）、`1x99oeu.json`（58）
- 采集器：`harvest_github.py`、`harvest_reddit_cdp.py`（登录镜像 Chrome CDP，只读）

*报告完 — Harry*

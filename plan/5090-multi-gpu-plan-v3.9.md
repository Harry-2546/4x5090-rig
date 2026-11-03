# 5090 多卡 LLM 部署方案 v3.9（4 卡优先，8 卡按需）

日期：2026-10-05 ｜ 基线：v3.6-cited-merged ｜ v3.7 结构重排 + 补漏；v3.8 按实际资产更正；v3.9 改为 Z790 纯 Ubuntu 服务器 + 多 PSU 安全设计（变更见附录 B）

---

## 0. 一页结论

**推荐路线：A2 = Z790-A D4 + i7-12700K + DDR4（4×32GB = 128GB）作为纯 Ubuntu 推理服务器 + PEX88096 matched kit + 4×RTX 5090。X870E 继续做 Windows 10 日常机。**

**为什么这样定：**

1. **职责分离。** 推理服务器 24/7 跑 Linux，日常机保持 Win10 不动，不用双启动。服务改为 LAN 监听即可。
2. **host 平台本身不是瓶颈。** GPU↔GPU P2P 在 switch 内部完成，host 只承担一条 Gen4 x16 上行（约 31.5 GB/s）。12700K + 双通道 DDR4-3200（约 51 GB/s）足够。
3. **唯一的短板是内存余量。** r10 配方要求约 125GB host RAM，其中 48GB PLE 表 mlock（[N03]）；Z790-A D4 最多 128GB。
   - 这能不能跑起来，**要在 G4 实测峰值内存后才能确定**。
   - 缓解措施见 §3.1：最小化 Ubuntu Server、swap / zram、检查 vLLM 的 CPU 侧缓冲。
   - 确实不够时，回退到 A1：X870E 插满 4×48GB 后双启动 Linux。调参步骤见附录 C。

**多 PSU 的结论（详见 §6）**：

- **"频率不齐"不会发生。** PCIe 参考时钟（REFCLK）由 host adapter 或 switch 板上的时钟芯片产生并分发，与 PSU 无关。
- **真正的风险有两个：**
  - **上电时序。** PCIe CEM 规范要求插卡的供电稳定后至少 100ms，PERST# 才能释放（T_PVPERL，[X05]）。GPU 那台 PSU 上电晚了，这张卡就会错过链路训练，表现为"有一张卡不识别"。
  - **12V 倒灌。** 同一张卡的 slot 12V 和 12V-2x6 来自不同 PSU 时，压差或一台断电会让电流从卡内部倒流。Level1Techs 上有人因此"cooked a pair of 3090s"（[X06]）。
- **对策：**
  - **每张卡的 slot 供电和 12V-2x6 必须来自同一台 PSU**，所以选每个槽有独立供电输入的 kit；
  - 所有 PSU 由同一个 PS_ON 信号同步开关，GPU 侧不能晚于 host 上电。

**接下来四步：**

| # | 动作 | 花费 | 产出 |
|---|---|---|---|
| 1 | 装上全新的 4×32GB DDR4 套装（同一套），开 XMP，跑 MemTest86；装 Ubuntu Server | $0 | A2 的 128GB 就绪 |
| 2 | **阶段 0 预验证**：在 X870E 上用临时 SSD 启动 Ubuntu（2×5090 已在这台、CPU 直连 x8/x8；Z790 只有 1 条 CPU x16，做不了这个测试），装 aikitoria 驱动，跑 P2P matrix 和 vLLM TP2 | $0 | 买 switch 前先确认 Blackwell P2P 驱动可用；不碰 Win10 系统盘 |
| 3 | 按 §3.4 清单询价，**重点问每个槽是否有独立供电输入** | — | 决定选一体背板还是分体 kit |
| 4 | 买 PSU 同步方案（同步线 / 继电器板），旧 1200W 先体检 | 约 $40–150 | 4 台 PSU 同时上电 |

**升级条件**：

- A2 在 G4 达不到 r10 基线的 90%，并且确认瓶颈在 host 路径（不是内存不足）→ 考虑 B1 / C。
- **内存不足** → 先回退 A1（X870E + 192GB，零成本），再考虑换平台。

---

## 1. 目标与约束

### 1.1 已有资产（不计入新增成本）

| 类别 | 资产 | 本方案用途 |
|---|---|---|
| GPU | 4×RTX 5090（目前 2 张装在 X870E 上） | 全部移到 Z790 + switch |
| 推理服务器 | ROG STRIX Z790-A GAMING WIFI D4 + i7-12700K（UHD 770 核显）+ 4×32GB DDR4 同一套装（全新未拆封）+ 其他 DDR4 | 纯 Ubuntu Server，4×32GB DDR4 |
| 日常机 | ROG CROSSHAIR X870E HERO + Ryzen 9 9950X3D + 4×48GB DDR5（两套芝奇 2×48GB DDR5-6000，时序不同） | 继续跑 Windows 10 LTSC；需要另配一张显卡做显示，或用 9950X3D 核显 |
| PSU | 1600W（2 根 12V-2x6）+ 1200W 新（有 12V-2x6）+ 1200W 旧（无 12V-2x6）+ 1000W（有 12V-2x6） | 分配见 §6 |
| 机箱 | 已有 | switch 机架方案见 §3.3 |

### 1.2 工作负载与性能目标

- 当前模型：`qwen3.8-flash-next-iq3_s` @ 127.0.0.1:8080，GGUF 格式，llama.cpp 单卡 + offload。
- **目标栈要换掉。** llama.cpp layer-split 在 4×5090 上实测只有 42–51 t/s，TP 路线单流能到 80–130 t/s（[M25], [M15], [M44]）。4 卡要兑现性能，需要换成 **vLLM TP4 + EP + NVFP4 checkpoint**（r10 配方，checkpoint 约占 135GB 磁盘，[N03]）。
- 部署后服务地址从 `127.0.0.1:8080` 改为 Z790 的 LAN 地址，客户端（X870E 上的工具）改连这个地址。
- **公开基线（QWEN-PEDIA r10，4×5090，PCIe，无 NVLink）**（[N03]）：
  - **r10 是什么**：GitHub 上 QWEN-PEDIA 项目里 Qwen3.8-Flash-Next 部署配方的**第 10 个修订版**（revision 10）。它不是一个新模型，而是一整套部署方案：NVFP4 量化权重 + vLLM overlay 补丁 + TP4 + EP 的启动参数。
  - 本文里的 125GB 内存要求、48GB PLE 表、`VLLM_CUSTOM_AR_ALLOW_PCIE` 都出自这个版本。配方以后更新到 r11 及之后，这些数字可能变化，部署时要固定使用的版本。
  - v3.6 及更早版本写作 "WEN-PEDIA"，是漏了字母 Q。

| 指标 | r10 基线 | 本项目验收门槛（≥90%） |
|---|---:|---:|
| engine steps/s | 105.7–106.0 | ≥ 95 |
| code decode tok/s | 319–331 | ≥ 290 |
| 36K / 100K prefill tok/s | 7,841 / 7,767 | ≥ 7,000 |
| host RAM | 125GB（48GB PLE mlock） | A2 只有 128GB，以 G4 实测峰值为准 |

> 待补：主要场景是单用户低延迟，还是多并发吞吐？这会决定后面选 TP4 单实例，还是 TP2×DP2 / 多实例。

### 1.3 硬门槛

1. **GPU 本地链路**：每张 GPU 到直接上游 switch/root port ≥ PCIe 4.0 x16 或 5.0 x8（约 31.5 GB/s 单向）。
2. **Fabric**：TP4 的 GPU↔GPU collective 必须走真实 CUDA P2P/NCCL 快路径。
3. **Host RAM**：r10 运行时**峰值实测值 + 8GB 余量**以内不能触发 OOM 或大量 swap（G4 检查）。
4. **供电**：每张 GPU 的所有 12V 输入来自同一台 PSU；所有 PSU 同步上电（§6）。
5. **Host 聚合带宽单独核算。** 4 张卡下行都是 x16，**不等于** host 有 4×31.5 GB/s。单 upstream 时，所有 host↔GPU 流量共用约 31.5 GB/s（[M02], [M01], [M05]）。
   - r10 的 PLE 是对 48GB 表做 UVA 小粒度随机读（[N03]），按量级估算远低于 31.5 GB/s，更可能受**延迟**影响，而不是被带宽卡住。switch 多出的一跳延迟要在应用层 A/B（§5 G4、G5）里实测，不靠推测下结论。

---

## 2. 方案比较

### 2.1 候选

| 代号 | 平台 | GPU 拓扑 | 内存 | 新增现金（不含 retimer） | 定位 |
|---|---|---|---|---:|---|
| **A2（推荐）** | Z790-A D4 + 12700K，纯 Ubuntu | PEX88096：1×Gen4 x16 上行 → 4×Gen4 x16 | 现有 DDR4 4×32GB = 128GB（板子上限） | **约 $0.68k–1.15k** | 服务器和日常机分离；内存余量要实测 |
| A1（回退） | X870E + 9950X3D，双启动 | 同上 | 现有 4×48GB DDR5 = 192GB | 约 $0.68k–1.15k | 内存余量足，但要双启动；A2 内存不够时用 |
| B1 | WRX80E-SAGE SE + 5955WX | 4×CPU 直连 Gen4 x16 | 现有 DDR4 UDIMM ×8（**必须同型**），最多 256GB | 约 $1.7k–2.9k | 性能确定性最高，内存余量也足。注意：有人报告 WRX80E-SAGE SE WiFi II 不支持嵌套 switch，还出现 AER storm（[X14]）；B1 是 CPU 直连、不用 switch，不受直接影响，但以后要在 WRX80 上挂 switch 就要先验证 |
| B2 | 同上 | 同上 | 新买 8×32GB RDIMM | 约 $2.4k–4.4k | 现有 DDR4 不够或不同型时 |
| C | EPYC 7002/7003 + H12SSL-i / ROMED8-2T | 4×CPU 直连 Gen4 x16，7 槽可扩 | **只支持 RDIMM**，必须新买 | 板+U 约 $1.1k–1.4k + RDIMM | 跟 B2 比价用 |

**不推荐（理由沿用 v3.6，并补了新证据）：**

- **消费板直拆四卡**：X870E 的 PEG 只有一组 x16（x16 / x8+x8 / x8+x4+x4），做不出 4×Gen5 x8（[N01], [M22], [M28]）。
- **Gen5 switch**：PM50100 €2,000 且缺货，PEX89048 超过 $1,500（[R08], [R09], [M14]）。
- **TRX50 / Threadripper 7000**：需要 DDR5 RDIMM，2026 年价格最不利。实建样本见 [M23]。

### 2.2 关键权衡

- **A 和 B/C 的本质区别**：A 的 GPU↔GPU 在 switch 内（PIX），host 共用一条 x16；B/C 每卡各有一条 CPU x16，GPU↔GPU 走 root complex（PHB），P2P 延迟和带宽要实测。
- TR Pro 5955WX 无 switch 直连，已复现 quad-5070 Ti switch 岛的成绩，结果 "pretty close"（[M04]）。**switch 买的是 lanes，不会提速。**
- **5090 锁 Gen4 是稳定性红利**：5090 在 Gen5 下黑屏、训练不稳是已知群体问题，社区建议降到 Gen4（[R07]）。A 路线天然工作在 Gen4，B/C 也是 Gen4 平台。
- **2026 年内存是最大的成本变量**。新 32GB DDR4-3200 RDIMM 报价接近 $400，翻新件约 $110–359（[X04]）。**能复用手上已有的内存，比 CPU 和主板的价差更能决定路线排序。**
- **A2 vs A1**：两者 switch 部分完全相同，区别只在 host。所以 kit、线材、PSU 方案可以直接在两台主机之间互换，回退成本只是把 host adapter 换个机器插。

### 2.3 决策树

```text
阶段 0（X870E 上 Live USB / 临时 SSD 启动 Ubuntu，现有 2×5090）
 ├─ aikitoria 驱动下 P2P 不可用 / vLLM TP2 报错 → 先解决驱动/BIOS，不采购
 └─ P2P 正常 → 询价并采购 kit（优先每槽独立供电输入，§3.4）
A2 上线后跑 §5 全部 Gate
 ├─ G1/G2 有卡不识别 → 先查 §6.2 上电时序，再查线材/固件
 ├─ G4 内存峰值超限（OOM / 大量 swap）
 │    → 先做 §3.1 的缓解措施；仍不够 → 回退 A1（X870E 双启动，192GB）
 ├─ G4 ≥ 90% 基线 → 定型，结束
 └─ G4 < 90%，且 G1–G3 正常、瓶颈确认在 host 路径
      ├─ 有 8 根同型 DDR4 UDIMM → B1（WRX80）
      └─ 否 → B2 与 C 同时询价，选总价低者
```

---

## 3. 推荐路线 A2 详细设计

### 3.1 拓扑、插槽与内存

```text
i7-12700K / Z790-A D4（Ubuntu Server，4×32GB DDR4 = 128GB）
        │ PCIEX16_1（CPU 直连 Gen5 x16 → 与 switch 协商 Gen4 x16）
matched host adapter ── matched cables（尽量短）
        │
┌───────────────────────┐
│  PEX88096 switch      │  1×x16 上行 + 4–5×x16 下行
└───────────────────────┘
   │     │     │     │
 5090  5090  5090  5090
```

**插槽与 M.2：**

- 只用 CPU 直连的 PCIEX16_1。另外两个物理 x16 槽来自芯片组，电气只有 x4/x4，不能用（[N10]）。
- 上机前在 N10 规格页确认：哪个 M.2 和 PCIEX16_1 共享通道，那个槽不插（X870E 上就有 M.2 抢 PEG lanes 掉到 x8 的案例，[M33]）。
- 系统盘和模型盘（r10 checkpoint 约 135GB）放在不共享通道的 M.2 上。
- 显示输出用 12700K 核显（UHD 770）；装好后可以完全 headless，用 SSH 管理。

**128GB 内存的缓解措施**（r10 标称 125GB，余量很小）：

1. 装 **Ubuntu Server 最小化**，不装桌面。系统常驻可以压到约 1–2GB。
2. 建一个 **32GB swapfile**（放 NVMe）或开 zram，只用来扛模型加载时的瞬时峰值。稳定运行后 `vmstat 1` 的 si/so 应接近 0。
3. **检查 vLLM 的 CPU 侧缓冲**：r10 配置里如有 CPU KV swap / offload 空间（按每张卡计算，TP4 会乘以 4），能关就关或调小。
4. checkpoint 加载走 page cache，这部分可以回收，不算常驻内存。真正常驻的是 48GB PLE（mlock）加上 4 个 worker 进程。
5. **G4 时记录峰值**：用 `free -g` 和 `smem`，或 `cat /sys/fs/cgroup/.../memory.peak`；同时 `dmesg | grep -i oom`。

如果做完这些仍然不够，就回退 A1：kit 和 host adapter 直接搬到 X870E，DDR5 混插调参见附录 C。

**其他：**

- 不依赖主板 bifurcation，kit 可以整体迁到任何 host（[M06]）。
- DDR4：4×32GB 是同一套装，厂商按 4 根一起验证过，可以直接开 XMP；MemTest86 不过就关掉 XMP，或降一档频率。

### 3.2 kit 选型：每个槽能否独立供电决定选哪种

- PEX88096 是 98-lane Gen4 switch，其中 2 条是 x1 管理口（[N02]）。社区已有 1×x16 上行 + 5×x16 下行的实际配置（[M03], [M04], [M05]）。
- **Blackwell 消费卡 + PEX88096 岛内 P2P 已有实证**：16×5060 Ti 分两个 88096 岛，vLLM NCCL 岛内 P2P 正常，TP8/PP2 跑到 130–150 t/s（[M03]）。
  - 修正 v3.6 措辞：5060 Ti 本来就是 x8 卡，并非被 switch "压到 x8"。这个案例证明的是 **Blackwell 架构 + 补丁驱动 + PEX88096** 这条组合可行，不涉及链路宽度同构。
- matched kit 优先：社区翻车大多出在第三方 SlimSAS 线材和转接板（85Ω 8i、sideband 不标准），switch 本身往往没坏（[R03]）。

**按 §6 的"同卡同源"原则，查证后的选型结论（2026-10-05）：**

| 形态 | 实际产品 | 供电 | 结论 |
|---|---|---|---|
| **分体 kit（推荐）** | PEX88096 **switch 卡插在 host 的 x16 槽里**，带 10 个 SFF-8654 8i 口，可配置成 5×x16（[M09]，约 $446，只是卡，不含线和转接板）；每张 GPU 用 2 根 8i 线接一块 x16 设备转接板 | switch 卡由 host 槽供电（加上卡上可能有的辅助口），归 host 的 PSU。**每块 GPU 转接板都有自己的 12V 输入**：c-payne SlimSAS x16 设备转接板写明 "mandatory Power connector to supply 12V"（[X09]）；同类 SFF-8654 x16 转接板普遍带 6-pin（[X10]） | **天然满足同卡同源**：转接板的 12V 和 GPU 的 12V-2x6 接同一台 PSU。卡厚也不受槽距限制，适合 3–3.5 槽的 AIB 5090 |
| 一体背板：ADT-Link 5-slot（[M11]，$715） | host 转接卡 → 2 根 8i 线 → 一块带 PEX88096 和 5 个 x16 槽的背板 | 新版 5 槽板去掉了旧 4 槽版的 24-pin，供电方式要问卖家；实物图上看不到每槽独立的供电口（[X11]） | **对 4×5090 不适用**：**槽距只有 40.6mm（双槽）**（[X11]），3 槽卡插不下相邻槽，FE 双槽卡贴在一起也散不了热；而且槽供电大概率共用 |
| 一体背板：c-payne PM40084 4×x16（€1,250，缺货） | Microchip Switchtec，5 槽宽间距（101.6mm） | 4 个 EPS（2 个必插）"to supply 12V to the Switch and GPUs"，没写明哪个 EPS 供哪个槽（[X12]） | 间距合适，但**页面写明 "Intel Mainstream as of now is not compatible"**（[X12]），与 Z790 冲突 |
| 一体背板：c-payne PM40100 5×x16（€1,550，缺货） | Microchip Switchtec，4 槽宽间距（81.28mm） | 3 个必插 EPS，同样没写明按槽分配（[X13]） | 同上，Intel 消费级平台不兼容 |

**两点要注意：**

- **Intel 消费级平台的兼容性是 A2 的新风险。** c-payne 明确写了他们的 Switchtec 板 "Intel Mainstream ... not compatible"，而 "AMD AM5 are usually OK"（[X12], [X13]）。PEX88096 是 Broadcom 的芯片，不一定有同样的问题，但社区的 88096 实建几乎都在 AM5 / EPYC / TR 上（[M03], [M04], [M05], [N11]），**还没找到 Z790 的成功案例**。
  - 询价时必须问 "Tested on Intel LGA1700/Z790?"（§3.4 第 10 条）。
  - 万一在 Z790 上枚举失败，退路是 A1：switch 卡插到 X870E 上，这个平台已经被验证过。
- 分体 kit 的线材和转接板**一定要和 switch 卡从同一个卖家买成套**。85Ω/100Ω 阻抗混用、sideband 不标准是 Gen2 降速的头号元凶（[R03]）。每张 GPU 用 2 根 8i 线，线尽量短（≤50cm）。

### 3.3 机械与散热

- **switch 芯片必须主动散热。** 88096 待机也耗电，芯片很热，被动散热片不够。社区做法是在 heatsink 上直接贴一把 80mm 风扇，例如 Arctic P8 Slim（[M04]）。
- **槽距和卡厚**：ADT-Link 5 槽背板的槽距只有 40.6mm（[X11]），4 张 5090 放不下。分体 kit 的每块转接板可以单独固定在矿架或测试台上，按卡厚留足间距（3 槽卡建议中心距 ≥ 80mm）。
- **switch 卡插在 host 里**：88096 在卡上自带风扇，但机箱内仍要有气流吹过它；10 个 8i 口出线集中，要规划好走线，不能硬折。
- 没有官方适配的机箱。实践中多用矿架、自制 4U 或测试台（[R05]）；N11 作者直接买了 kit 配套机箱（[N11]）。
- 4×400W 的 GPU 热量约 1.6kW，要考虑房间散热。

### 3.4 采购前必须让卖家书面确认

> I need the complete matched PEX88096 kit for one PCIe x16 host and four RTX 5090 GPUs. Please confirm:
>
> 1. The package includes the PEX88096 switch/backplane, PCIe x16 host adapter, and all required data cables.
> 2. Firmware / DIP configuration supports **1× PCIe Gen4 x16 upstream + 4–5× Gen4 x16 downstream simultaneously**, and all downstream ports negotiate Gen4 x16 at the same time.
> 3. No motherboard bifurcation is required.
> 4. Please provide the SBR / DIP-switch table, the firmware version, and whether the SPI flash is pre-programmed.
> 5. REFCLK, PERST# and presence detect are handled correctly by the matched host adapter. Is REFCLK generated on the switch board and distributed to each slot, or is SRIS used?
> 6. Included cable lengths and impedance (85Ω or 100Ω).
> 7. Slot pitch / maximum supported GPU thickness.
> 8. **Power inputs: does each x16 slot have its own 12V input connector (so slot power can come from the same PSU as that GPU's 12V-2x6), or do all slots share one input? Which connector types (24-pin / EPS / 6-pin / 8-pin) power the switch chip itself?**
> 9. **Power sequencing: what happens if a GPU's PSU turns on later than the switch board? Does the board delay PERST# to the slots, and is there a recommended multi-PSU power-on procedure?**
> 10. Tested on Intel LGA1700 (Z790) and/or AMD AM5? Tested with RTX 50-series / RTX 5090?
> 11. If available, provide `lspci -vv` or `nvidia-smi topo -m` output.

第 4 条针对克隆板常见问题：出厂 SPI flash 全是 FF（没有固件），以及 DIP 开关和丝印对不上（[M05]）。第 8、9 条决定 §6 的接线方式。

---

## 4. 软件栈

### 4.1 OS

**Z790 装 bare-metal Ubuntu Server LTS，不用 WSL。** WSL 由 Windows host 驱动提供 CUDA，没法装补丁版 kernel module（[N09]）。

- 服务监听 LAN 地址，用 `ufw` 限定只允许 X870E 等可信主机访问。
- 日常管理走 SSH。
- X870E 的 Win10 不做任何改动；阶段 0 只用临时 SSD 启动 Ubuntu。

### 4.2 BIOS

```text
通用：
  Above 4G Decoding      Enabled
  Resizable BAR          Enabled
  CSM                    Disabled（UEFI）
  ASPM                   Disabled（排障阶段）
Z790（Intel）：
  VT-d                   Enabled（kernel：intel_iommu=on iommu=pt）
  PCIEX16_1 速率         Auto（必要时强制 Gen4）
  可选：PCIe 链路训练失败时关闭 Native ASPM、关闭 PCIe 省电相关选项
X870E（AMD，回退 A1 时）：
  IOMMU                  Enabled（kernel：amd_iommu=on iommu=pt）
  MMIO High              R01 配方：Granularity 1024G / Base ~56T（[M03]）
```

### 4.3 驱动：aikitoria P2P 补丁

依据最新 README（[X01]，[M45]）：

- 当前版本基于 NVIDIA **610.57.04**，支持 RTX 30/40/50 系。**固定这个版本，并 hold 住发行版的 nvidia 包，防止自动升级把补丁覆盖掉。**
- **IOMMU 必须是 passthrough**：AMD 用 `amd_iommu=on iommu=pt`，Intel 用 `intel_iommu=on iommu=pt`。
  - 16×5060 Ti 实建用的是 `intel_iommu=off`（[M03]）。passthrough 下 P2P 不通时，可以退到 off；代价是失去 DMA 隔离。
- **BAR1 要能映射全部可用显存**。5090 是 32GB，所以应是 **32GiB BAR1**。
  - v3.6 写的 "16 GiB BAR1" 抄自 5060 Ti（16GB）的配方，**不适用于 5090**。
  - 验证：`nvidia-smi -q -d MEMORY | grep -A3 BAR1`。
- **跨代 P2P 已支持**：README 说明不同代 GPU 之间需要额外打 `libcuda` 补丁（[X01]）。
  - v3.6 的 R3（"3090↔4090 不能 peer"）对应的是旧版驱动，现已过时。
  - 但 TP 混卡仍会被最慢的那张卡拖累，岛内仍建议只放同型卡。

### 4.4 ACS：只关 switch 桥，并做成开机持久化

只对 PEX/PLX bridge 关 ACS，不要全局关闭（[M03]）。用 `setpci` 写的寄存器**重启后会丢失**，所以做成 systemd oneshot：

```bash
#!/usr/bin/env bash
# /usr/local/sbin/pex-acs-off.sh
# 用 `lspci -nn | grep -i bridge` 先确认 switch 的 vendor ID：Broadcom/LSI 为 1000，旧 PLX 为 10b5
set -euo pipefail
for vid in 1000 10b5; do
  for dev in $(lspci -D -d "${vid}:" | awk '/PCI bridge/ {print $1}'); do
    setpci -s "$dev" ECAP_ACS+0x6.w=0000 || true
  done
done
```

```ini
# /etc/systemd/system/pex-acs-off.service
[Unit]
Description=Disable ACS on PEX88096 bridges
Before=nvidia-persistenced.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/pex-acs-off.sh
[Install]
WantedBy=multi-user.target
```

- 验证：`sudo lspci -vvv | grep -i ACSCtl`，switch 桥上各项应全部显示为 `-`。
- README 提到的 `pcie_acs_override=` 内核参数，**只在打了 ACS override 补丁的内核里存在**（如部分 zen / Proxmox 内核）。主线内核用上面的 setpci 方案即可。
- `pci=realloc=on,hpmmioprefsize=512G` 是 R01 配方里的 kernel 参数（[M03]）。只在 BAR 分配失败时才加。

### 4.5 NCCL

- **不设置 `NCCL_P2P_LEVEL`**，让 NCCL 自动选择。必须手动约束时用 `PIX`，**不要用 `SYS`**：它的含义是"允许最远路径"，并不代表最快（[N06]）。
- NCCL 不会跨 switch 走 P2P，这是硬行为：`intraNodeP2pSupport 0`。强行跨岛要伪造 `NCCL_TOPO_FILE`，实测跨岛约 19.8 GB/s，岛内约 25 GB/s（[M05]）。

### 4.6 vLLM

- **上游 vLLM 在 PCIe-only 且多于 2 张 GPU 时会禁用 custom all-reduce**（[X02]）。r10 的成绩依赖它的 overlay，用 `VLLM_CUSTOM_AR_ALLOW_PCIE` 绕过了这个限制，在 TP4 小消息上用 one-shot IPC kernel 代替 NCCL ring（[N03]）。
- **所以验收必须用 r10 overlay 加它固定的 vLLM 版本。** 用上游 vLLM 跑出来的数字不能和基线比。

```bash
export VLLM_SKIP_P2P_CHECK=0          # 首次部署必须让 vLLM 做功能性 P2P 检查（[N07], [N08]）
export VLLM_CUSTOM_AR_ALLOW_PCIE=1    # 仅 r10 overlay 识别；P2P 验证通过后再开
# 不设置 NCCL_P2P_LEVEL
```

- "驱动报告 can-access-peer" 不等于 P2P 真能读写，补丁版 GeForce 环境尤其要做功能性测试（[N08]）。确认可读写之后，才根据固定版本的行为决定是否把 `VLLM_SKIP_P2P_CHECK` 改成 1。
- **mlock**：48GB PLE 表要 mlock。容器内需设 `--ulimit memlock=-1:-1`（[N03]）；裸机则要调 `/etc/security/limits.conf`。

---

## 5. 验收流程（逐级 Gate，前一级不过不进下一级）

| Gate | 测什么 | 命令 / 工具 | 通过标准 |
|---|---|---|---|
| **G-1 内存**（买前） | Z790 4×32GB DDR4 稳定性 | MemTest86 至少 1 轮 | 0 错误；`free -g` 显示约 125GB 以上 |
| **G0 阶段 0**（买前，X870E 2 卡） | Blackwell 补丁驱动 P2P | `p2pBandwidthLatencyTest`，vLLM TP2 | P2P 已启用，TP2 能稳定推理；记录基线 |
| **G1 链路** | 协商速率和宽度，链路错误 | `sudo lspci -vv`（LnkSta）、`nvidia-smi -q -d PCIE`、`dmesg \| grep -i aer` | 上行和 4 条下行都是 16GT/s x16；空载 1h 内 AER 计数不增长、replay 计数稳定；**连续冷启动 10 次，每次 4 张卡都能识别**（§6.3） |
| **G2 Peer** | P2P 拓扑、带宽、延迟 | `nvidia-smi topo -m`、`p2pBandwidthLatencyTest`（或 nvbandwidth） | 所有卡对之间为 PIX；单向 ≥ 24 GB/s，双向 ≥ 45 GB/s（社区实测 25–28 / 约 52，[M03], [M04], [M05], [M01]）；各卡之间无明显离群 |
| **G3 NCCL** | collective | `all_reduce_perf -b 8M -e 1G -f 2 -g 4` | 记录 busbw 曲线（经验阈值：1GB 时低于 15 GB/s 视为异常，首轮实测后校准） |
| **G4 应用** | r10 overlay，TP4 + EP | 固定 prompt、context、MTP 参数和**功率上限** | 达到 §1.2 门槛（基线的 90% 及以上）；同时记录 TTFT；**记录内存峰值**，无 OOM，稳定运行时 `vmstat` 的 si/so 接近 0（§3.1） |
| **G5 A/B** | P2P 实际收益 | 关闭 P2P（`NCCL_P2P_DISABLE=1` + 关 custom AR）重跑 G4 | 记录 pp 和 tg 的差值（参考：EPYC 4×5060 Ti 开 P2P 后 pp 提升 40%，[R06]） |
| **G6 稳定性** | 长时负载 | 24h serving soak；`dmesg \| grep -i xid`；红外测温 12V-2x6 接头 | 无 Xid、无掉卡、无降速，接头温度正常（[M47]） |

**出现以下任一情况，先查硬件链路，不要去调 vLLM：** 大消息单向只有 10–15 GB/s；某张卡明显比其他卡低；拓扑不是 PIX；链路掉到 Gen3/Gen2。

**PCIe 宽度参考（判断异常时用）：**

- 5090 在 Gen5 x8 下跑全显存场景，与 x16 同档；但做 expert offload 时会打满链路（[M36]）。x8/x8 同宽实建样本见 [M30], [M31], [M32], [M34]。
- 走芯片组 x4 路径时 P2P 会断，prefill 掉到约 1/3，decode 基本无损（[M41], [M42]）。x8 Gen4 P2P 可跑满 14.27 GB/s（[M43]）。
- 游戏测试里 x8 和 x16 的结论不能外推到 LLM（[M39], [M40]）。
- 限瓦单卡锚点：Flash-Next IQ3_S 150–200 t/s（[M38]）；27B 在 475W 下 208 tok/s（[M46]）；27B NVFP4 262K 上下文 77 tok/s（[M37]）。

**P2P 始终起不来时的降级方案**：TP2×PP2（只需同侧卡对 P2P）或 TP2×DP2；最低限度是 4 个单卡实例加路由。这些都只是临时方案，并且要触发 §2.3 的平台复审。

---

## 6. 供电：多 PSU 设计

### 6.1 多 PSU 混用 switch 安全吗？

**可以，但有前提。** 以下是查证结论：

| 担心的问题 | 实际情况 |
|---|---|
| 不同 PSU 导致"频率不齐" | **不存在。** PCIe 的 100MHz REFCLK 由 host adapter 或 switch 板上的时钟芯片产生并分发（或各端用 SRIS 独立时钟），与 12V 来自哪台 PSU 无关。时钟出问题是板子设计问题，见 §3.4 第 5 条。 |
| 有的 GPU 不识别 | **真实存在，原因是上电时序。** PCIe CEM 规范要求插卡电源稳定后至少 100ms 才能释放 PERST#（T_PVPERL；REFCLK 稳定后至少 100µs，[X05]）。GPU 那台 PSU 上电晚了、没上电，或中途掉电，这张卡就会错过链路训练 → 不识别或降速。N11 作者也遇到过 retimer 干扰自动上电时序，换成无源转接后解决（[N11]）。 |
| 损坏硬件 | **真实存在，原因是 12V 倒灌。** 同一张卡的 slot 12V 和辅助 12V 来自两台 PSU 时，两台之间的压差，或其中一台断电，都会让电流经卡内或主板走线倒流。Level1Techs 的帖子里，有人因此烧了两张 3090，楼主的主板也坏了（[X06]）。社区共识是"同一部件的所有供电来自同一台 PSU"（[X06], [X08]）。 |

**社区 PEX88096 实建都是多电源供电：**

> 核对状态（2026-10-06）：以下 4 条已对照用户粘贴的帖子全文逐条核对。Reddit 不允许本工具直接访问，原文由用户从浏览器复制提供。

- **16×5060 Ti + 2 块 PEX88096**（[M03]）：
  - 有人要求晒机器，OP 回复原话 "Powered by 3 Dell 1600w"（该回复 172 赞）。Dell 1600W 是服务器电源。
  - 这是 Intel 服务器平台（ASRock Rack SPC621D8U-2T + Xeon Gold 6330），每个岛 8 张卡。
- **Frankenserver**（r/LocalLLM，抓取时显示发帖于 21 小时前，约 2026-10-05，493 赞）（[X14]）：
  - OP 的电源描述："With 4 x 2000W PSUs I have 4 x 120V UPS units that will half the PSUs to ~4000W. This is just 2 x 20A circuits."
  - 也就是说，**4 台 2000W 电源在 120V 下只算约 4000W**，印证了 §6.4"服务器电源在 115V 下会降额"的判断。
  - 扩容计划："I am thinking 2 PEX88096 expansion boards should work off the supermicro…. And more power."
- **Quad 5070 Ti + Quad 5060 Ti，两块 PLX 88096**（[M04]）：
  - OP 原话："a few hundreds of $$ wasted on power adaptors / pci risers that are not suitable"。
  - "each of these nodes is self contained built up hardware"：每个 node 是独立的机箱加独立的 PSU（Node1 用 MSI MEG Ai1600T，Node2 用 DeepCool PN1200M，host 另用 850W）。
  - 这和下面"同卡同源"的原则一致：先划清楚供电域，再买转接件。
- **r/homelab "Help me understand these plx switches"**（4 个月前，9 赞）（[X15]）：
  - OP 原话是推测，不是定论："I also doubt I have enough molex power leads from my psu to power all the slots so I might need an extra power supply regardless"。
  - 回帖给出了原因：PCIe 规范要求每个槽能提供 75W，"5x75 and it's already 375W"，所以 "you will be not able to power it from motherboard"。
  - 同一位回帖人列的开销清单，第一项就是 "+ Separate PSU"，后面依次是 Cables、Adapters、Possible retimer。
  - 也就是说，switch 的槽供电要单独规划，不能指望 host 电源顺带供上。

**结论：多电源是常态，问题不在"能不能混用"，而在于怎么划分供电域、怎么同步上电。**

**设计原则（按优先级）：**

1. **同卡同源**：每张 GPU 的 slot 12V（背板对应槽的供电输入或转接板输入）和 12V-2x6 接同一台 PSU。前提是 kit 每个槽能单独供电（§3.2）。
2. **同步上电**：所有 PSU 由同一个 PS_ON 信号控制，GPU 侧不能晚于 host。
3. **共地**：所有 PSU 插在同一配电箱下的接地插座上，同步线同时把各台的地连在一起。
4. **不热插拔、不单独断电**：运行中任何一台 PSU 掉电都按故障处理，整机断电重启。

### 6.2 PSU 分配（kit 每槽独立供电的情况，推荐）

| PSU | 原生 12V-2x6 接口 | 带什么 | 负载@400W/卡 | 负载@575W/卡 |
|---|---|---|---|---|
| **PSU-H 1200W（旧）** | 无 | Z790 主机（24-pin + EPS）+ switch 芯片供电 + switch 风扇；**作为 PS_ON 主控** | ≈ 0.3–0.4kW（~30%） | 同左 |
| PSU-1 1600W | 2 根 | GPU0、GPU1 的 12V-2x6 + 槽 0、槽 1 的供电输入 | ≈ 0.8kW（~50%） | ≈ 1.15kW（~72%） |
| PSU-2 1200W（新） | 有 | GPU2 的 12V-2x6 + 槽 2 的供电输入 | ≈ 0.4kW（~33%） | ≈ 0.58kW（~48%） |
| PSU-3 1000W | 有 | GPU3 的 12V-2x6 + 槽 3 的供电输入 | ≈ 0.4kW（~40%） | ≈ 0.58kW（~58%） |

- 槽供电输入用各自 PSU 的 PCIe 6/8-pin 线，接口类型按卖家答复（§3.4 第 8 条）。
- **PSU-H 只带 host 和 switch 芯片，不带任何 GPU 的 12V。** 所以它没有 12V-2x6 也无所谓，GPU 功率上限怎么调都不影响它。
- PSU-1 不限瓦时负载约 72%，是四台里最高的。如果它不是 ATX 3.x，建议长期限到 ≤450W/卡（约 0.9kW，56%）。
- **4 台都要用上**：4 根 12V-2x6 分布在 3 台 PSU 上，host 和 switch 又占一台。

### 6.3 上电与断电时序

**开机：**

- **推荐：同步线 / 同步板。** 把 PSU-1、2、3 的 PS_ON 接到 PSU-H 的 PS_ON 上，按主机电源键时 4 台同时启动。
  - ATX 电源从 PS_ON 到 PWR_OK 通常在几百毫秒内。主机 BIOS 释放 PCIe PERST# 要更晚：POST 一般要几秒。所以同时启动时 GPU 的 12V 会远早于 PERST# 稳定，满足 100ms 要求。
- **继电器式（add2psu 一类）**：检测到主控 PSU 有电后再启动从机，延迟几十毫秒，同样满足要求。
  - 注意：有人报告过继电器板拉不起第二台 PSU（[X07]）。上线前要逐台确认能跟随启动。
- **最保守：先手动打开 GPU 侧 3 台 PSU（短接 PS_ON 或用开关），再按主机电源键。** 适合排障，不适合长期使用。

**关机：** 先让主机关机，再断 GPU 侧 PSU；同步线方案会同时断电，也可以。**不要在主机运行时单独关掉或重启任何一台 GPU 侧 PSU。**

**验收：** 加入 G1——**连续冷启动 10 次，每次 `nvidia-smi -L` 都看到 4 张卡，且 `lspci -vv` 每张都是 16GT/s x16。** 有任何一次少卡，就先查时序。

**少卡时的处理：**

1. 不要指望热重扫。`echo 1 | sudo tee /sys/bus/pci/rescan` 偶尔能找回晚上电的卡，但不可靠。
2. 正确做法是整机完全断电（所有 PSU），等 10 秒，再按上面的顺序重新上电。
3. 如果总是同一张卡缺失，就和其他卡交换 PSU / 线 / 槽位，判断问题跟着哪个部件走（也可能是线材或固件问题，[R03], [M05]）。
4. 运行中出现 `Xid 79`（GPU has fallen off the bus）：先查那台 PSU 是否触发了过流 / 过功率保护，再查接头。

### 6.4 退路：kit 所有槽共用一个供电输入时

- 4 张卡的 slot 12V 必然来自一台 PSU，而它们的 12V-2x6 来自另外 3 台，违反"同卡同源"。
- **严格遵守同卡同源，就意味着背板加 4 张卡全部由一台 PSU 供电，而现有库存做不到：**
  - 每卡限 400W 时，GPU 侧 12V 负载约 1.7kW（4×~380W 12V-2x6 + slot + switch），已经超过 1600W；
  - 在 115V 下，单台 ATX 电源一般最大 1600W，受 15A 插座限制；更高瓦数的型号通常要 230V 才能满额输出。
  - 所以这条路要么换成能分开供电的 kit，要么新购单一 12V 域的电源方案（见下面第 2 条）。
- 5090 从 slot 取电很少，同步上电后压差也小，实际出事概率不高。**但一旦某台 PSU 单独掉电，就有倒灌风险，后果是烧卡。**
- 可选做法（按推荐顺序）：
  1. **换成分体 kit**（每块转接板独立供电）。首选。
  2. **单一 12V 域**：用服务器 CRPS 电源加配电板，给背板和全部 4 张卡供电。Level1Techs 上的推荐做法就是 PDB（[X06]）。社区实建也多用服务器电源：3 台 Dell 1600W 带 16 张卡（[M03]）；4 台 2000W，但在 120V 下作者按约 4000W 计算，接在 2 条 20A 回路上（[X14]）。这需要新购，价格待询。注意：CRPS 在 115V 下通常会降额（标称 2000W+ 的型号在低压下输出明显更低），选型时按 115V 下的额定功率计算，并且可能需要多台并联。
  3. 接受风险：背板接 PSU-1（GPU0/1 同源，GPU2/3 跨源），严格同步上电，并在 G6 用功率计和日志监控掉电事件。**不推荐长期这样用。**

### 6.5 AC 回路（按 115V，PSU 效率约 92% 估算）

| 每卡功率 | 整机 AC | 回路 1：PSU-1 1600W + PSU-H 1200W（旧） | 回路 2：PSU-2 1200W（新）+ PSU-3 1000W |
|---|---|---|---|
| 400W | 约 2.1kW | 约 1.25kW / 11A：15A 回路可用 | 约 0.87kW / 7.6A |
| 575W | 约 2.9kW | 约 1.63kW / 14.2A：**必须是 20A 回路** | 约 1.25kW / 10.9A |

- 两条回路要接在不同的 breaker 上，但必须同属一个配电箱，保证共地。
- 先用功率计实测 AC 输入，再定长期功率上限。
- **旧 1200W 上机前先体检**：看使用年限和风扇噪声；接功率计带主机满载 CPU 压力测试 1h，同时观察 12V 电压。它是 PS_ON 主控，出故障会导致整机掉电。

### 6.6 通用要求

- 每张卡一根**原生 12V-2x6**，不用 4×8pin 转接，不用 Y 线。1600W 的两根必须是 PSU 端**两个独立接口**各出一根。插合到位和接头温度列入 G6 验收（[M47]）。
- 4 卡实建参考：7970X 平台 1600W + 2×2000W CRPS，峰值约 3.1kW（[M23]）；限 450W + 双 1600W（[M24]）；双 1600W 带 4 卡（[M27]）。
- "5090 最低只能限到 400W"不是通用规则：本机 `nvidia-smi` 验证 Min Power Limit = 400W，但不同 VBIOS/AIB 范围不同，以实际 `nvidia-smi -q` 为准（[M26]）。

---

## 7. 成本（2026-10，美国市场；不含已有资产）

### 7.1 路线 A（A1 / A2 共用部分）

| 项目 | 目标价 | 保守预算 | 备注 |
|---|---:|---:|---|
| PEX88096 matched kit（switch + host adapter + 线） | $575–650 | $700–850 | 实际成交样本 $577.50（[N11]，站点会间歇 404，备用入口 [R10b]）。AliExpress 挂牌参考：10-port 板 $237–603、裸板 $245、5-slot kit $715（[M08], [M10], [M11]），**裸板价不能当整套价** |
| switch 主动散热和风扇 | $60–120 | $150 | |
| 4 台 PSU 同步板 / 继电器和杂项线材 | $40–100 | $150 | PSU 本体用库存（1600 + 1200×2 + 1000） |
| **小计（不含 retimer）** | **约 $675–870** | **约 $1,150** | |
| Retimer（仅在链路不稳时买） | $0 | 约 $130/张 × 需要的链路数 = $130–660 | 单价见 [M12] |
| **最坏情况（含 retimer）** | — | **约 $1,280–1,810** | v3.6 写的 $1,600–1,900 算多了 |
| A2 内存 | **$0** | $0 | 现有 4×32GB DDR4 |
| Linux 系统盘 / 模型盘 | $0 | 视库存而定 | r10 checkpoint 约 135GB |
| 分体 kit 的额外转接板（如背板不能每槽独立供电） | $0 | 约 $20/块 × 4 | 参考 [M13]；以卖家整套报价为准 |

### 7.2 路线 B / C

| 项目 | 理想淘货价 | 当前现实预算 | 备注 |
|---|---:|---:|---|
| 5955WX | $600–800 | $850–1,000 | PassMark 价格只是弱锚点，以 eBay 已售为准（[N14], [N04]） |
| WRX80E-SAGE SE WiFi (II) | $850–1,000 | $1,000–1,150 | 已售样本 $999.95–1,125（[N12], [N13]） |
| sWRX8 散热器 / riser / 杂项 | $260–520 | $750 | |
| **B1 合计（复用 DDR4 UDIMM）** | **约 $1.7k–2.3k** | **约 $2.6k–2.9k** | 8 根必须同型（[R10a]），在官方支持范围内（[N05]） |
| **B2 合计（+ 8×32GB RDIMM）** | **约 $2.4k–3.3k** | **约 $3.65k–4.4k** | |
| C：EPYC 7532 + H12SSL-i 组合 | — | 单个挂牌约 $1,370（[X03]） | 样本只有一个，需多方比价 |
| C：8×32GB DDR4 RDIMM | 翻新约 $110/条 | 新品接近 $400/条 | [X04]，2026 涨价期 |

**结论：A2 ≈ $0.7k–1.15k（内存零新增，余量要实测）；回退 A1 时不需要新增成本；B1 ≈ $2–2.9k，B2 / C ≈ $2.4k–4.5k。**

---

## 8. 阶段 2：8 卡（按需，不提前买）

- **现在不买 8 卡 fabric**，当前 kit 定位为一个"高质量 4-GPU compute island"。
- **首选：两个独立的 TP4 岛 + DP 路由。** 岛内 Gen4 x16，没有跨 switch 的 all-reduce，适合多 agent、多模型和高并发服务（[M04]）。
  - X870E 要保持 Win10 日常机，所以**第二个岛需要新的 host**。候选是 B1 / C：WRX80 或 EPYC 有 7 条 x16，单台就能挂两套 kit，或者直接 8 卡 CPU 直连。
  - 也可以让 X870E 双启动作为第二岛，但这和"日常机不动"的前提冲突。
  - 供电：现有 4 台 PSU 已全部分给第一岛（§6），第二岛需要另购一组。
- 只有在必须单模型 TP8 时才重新评估：Gen5 大 switch、EPYC/TR Pro、8×x8 的 PEX88096 岛（16×5060 Ti 双岛每岛 8×x8 跑 TP8，130–150 t/s，[M03]）、PP2×TP4、以及届时 vLLM/SGLang 的 collective 实测。**跨岛 TP8 不可行**，理由见 §4.5。
- 8×5090 参考：
  - DeepSeek V4 Flash 聚合 2000+ t/s（50 并发），配置开源（[M15], [M17]）；
  - vLLM TP8 单流 80–130 t/s（[M16]）。
  - 供电和机架教训：[M18], [M19], [M20], [M21]。

---

## 9. 风险登记

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 5090 + 88096 岛内 P2P 不通 | 低–中 | 高 | G0 先在现有平台验证驱动；Blackwell + 88096 已有实证（[M03]）；ACS 持久化（§4.4） |
| 链路掉 Gen2 或部分卡训练失败 | 中 | 高 | matched kit + 短线；G1 逐槽核对；不行再加 retimer（[R03], [M12], [N18]） |
| 克隆板无固件或 DIP 与丝印不符 | 中 | 中 | §3.4 第 4 条要书面答复（[M05]） |
| switch 过热 | 高（不加风扇时） | 中 | 主动风扇（[M04]） |
| switch 在 Intel Z790 上枚举失败 | 未知（无 Z790 案例；c-payne Switchtec 明确不兼容 Intel 消费级平台） | 高 | 询价时问是否在 LGA1700 上测过；失败就把 switch 卡搬到 X870E（A1） |
| 买到拆机 / 翻新的 PEX88096 卡，行为不稳定 | 中 | 中 | 约 $500 的 PEX 卡多为拆机件（[X14]）；选出货量大、有退货保障的卖家，到货先跑 G1 |
| 便宜的 8i 线 / 转接板不正确支持 presence 信号 | 中 | 中 | 线材和转接板与 switch 卡同一卖家成套买（[X14], [R03]） |
| Z790 的 128GB 内存不够 r10 | 中 | 高 | §3.1 缓解措施；G4 实测峰值；不够就回退 A1（附录 C） |
| GPU 侧 PSU 上电晚 → 少卡 | 中 | 中 | 同步线 / 同步板；G1 冷启动 10 次（§6.3） |
| 12V 倒灌烧卡（slot 和 12V-2x6 跨 PSU） | 低（同卡同源时）/ 中（共用背板供电时） | 很高 | 选每槽独立供电或分体 kit；严禁单独断任何一台 PSU（§6.1、§6.4） |
| 旧 1200W 故障导致整机掉电 | 低–中 | 高 | 上机前体检和满载测试；只带 host 和 switch 芯片（§6.2） |
| 驱动或 vLLM 升级导致退化 | 中 | 中 | 固定驱动 610.57.04、r10 overlay 和 vLLM 版本；apt hold |
| 12V-2x6 过热或熔毁 | 低 | 很高 | 原生线，插到位，G6 测温，限功率（[M47]） |
| 跳闸 | 中（不限瓦时） | 高 | 两条回路；575W/卡时回路 1 必须是 20A；功率计实测（§6） |

---

## 10. 社区调研摘要（原 §0.5，按 v3.7 核验结果更新）

- **R1 Blackwell + 88096 岛内 P2P 成立**：16×5060 Ti 双岛 TP8/PP2（[M03]）。配方见 §4.2–4.4；**BAR1 大小要按 5090 改成 32GiB**。
- **R2 NCCL 不跨 switch 走 P2P**：结论是 TP 放岛内，PP 跨岛（[M05], [M03]）。
- **R3 混卡 P2P**：~~只在同架构之间成立~~ → 新版 aikitoria 支持跨代，但需要额外的 libcuda 补丁（[X01]）。TP 混卡仍会被最慢卡拖累。
- **R4 失败模式**：Gen2 回落多半是线材或转接板问题（[R03]）；克隆板无固件、DIP 与丝印不符（[M05]）；switch 过热（[M04]）；没有官方机箱（[R05]）。
- **R5 无 switch 的 TR Pro 对照组成绩接近**（[M04]）。
- **R6 开 P2P 后 prefill 提升 40%**（[R06]）。
- **R7 5090 降到 Gen4 有利于稳定**（[R07]）。
- **R8 Gen5 switch 性价比崩塌**（[R08], [R09], [M14]）。
- **R9 反方观点"PEX 不能岛内 P2P"**：出自嵌套在 PM50100 下游的拓扑，和独立单岛不同构，不采纳（[R09]）。
- **R10 引用质量**：N11 站点会间歇 404，备用入口 [R10b]；N14 是弱价格锚点；WRX80 的 8 根内存必须同型（[R10a]）。

---

## 附录 A：参考来源（去重后共 85 条，所有旧链接都保留）

v3.6 里同一个 URL 最多重复登记了三次（N/R/M 各一次），本版每个 URL 只保留一个 ID，旧编号写在"别名"列。新增来源记为 `Xnn`。

| ID | 别名 | 来源 | 要点 |
|---|---|---|---|
| **官方规格 / 文档** ||||
| [N01] | | ASUS X870E HERO 规格 | PEG x16/x8+x8/x8+x4+x4；M.2_2/3 共享 PEG lanes |
| [N02] | | Broadcom PEX88096 | 98 lanes，含 2 个 x1 管理口 |
| [N04] | | AMD TR PRO 5000 WX | 128 条 Gen4 lanes，8 通道 DDR4 |
| [N05] | | ASUS WRX80E-SAGE SE WiFi II | 7×Gen4 x16；支持 U/R/3DS/LR-DIMM |
| [N06] | | NCCL 环境变量文档 | `NCCL_P2P_LEVEL` 的定义 |
| [N07] | | vLLM `envs.py` | `VLLM_SKIP_P2P_CHECK` |
| [N08] | | vLLM P2P gating RFC | 功能性检查的历史 |
| [N09] | | NVIDIA CUDA on WSL | WSL 内不装 Linux 驱动 |
| [N10] | | ASUS Z790-A D4 规格 | 1×CPU Gen5 x16；芯片组槽电气 x4/x4 |
| [X01] | | aikitoria README（固定 commit） | 驱动 610.57.04；iommu=pt；BAR1 覆盖全部显存；跨代需打 libcuda 补丁；ACS 说明 |
| [X02] | | vLLM custom_all_reduce 文档 v0.23.0 | 多于 2 张 PCIe-only GPU 时禁用 custom AR |
| [M45] | N17 | aikitoria/open-gpu-kernel-modules 仓库 | P2P 补丁驱动 |
| **模型基线** ||||
| [N03] | | QWEN-PEDIA Qwen3.8-Flash-Next r10 | 4×5090 基线；125GB RAM / 48GB PLE mlock；`VLLM_CUSTOM_AR_ALLOW_PCIE` |
| **PEX88096 / switch 实建** ||||
| [M01] | N15 | LocalLLaMA：PLX/PEX 4.0 对 LLM 与 P2P 有帮助 | |
| [M02] | | homelab：PEX88096 上行带宽疑虑 | |
| [M03] | R01 | LocalLLaMA：16×5060 Ti 双 88096 岛（2026-10-06 核对：290 赞 / 174 评论） | BIOS/ACS/BAR 配方（驱动 610.43.02-p2p、`intel_iommu=off`、16GB 卡配 16,384 MiB BAR1）；OP 回复 "Powered by 3 Dell 1600w" |
| [M04] | R04 | LocalLLaMA：Dailychained 双 88096 岛（2026-10-06 核对） | 88096 加装 80mm 风扇；TR Pro 5955WX 无 switch 对照组 "Pretty close results"；"a few hundreds of $$ wasted on power adaptors / pci risers"；每个 node 独立机箱、独立 PSU；host 是 AM5（B850 + 9600X） |
| [M05] | N16, R02 | LocalLLaMA：AM5 7-GPU，Gen5/4 switch | NCCL 不跨 switch；克隆板问题 |
| [M06] | | homelab：PCIe switching 资源帖 | |
| [M07] | | LocalLLaMA：MCIO 线选型 | |
| [R03] | | LocalLLM：Frankenstein 4×3090 | 链路训练翻车画像 |
| [R05] | | homelab：PLX88096 机箱 | |
| [N18] | | Level1Techs switch/MCIO/retimer 长帖 | |
| [N11] | | Ovi's Tech Blog：PEX88096 AM5 实建 | $577.50 |
| [R10b] | | Ovi's Tech Blog tag 页 | N11 的备用入口 |
| **采购 / 价格** ||||
| [M08] | | AliExpress 10-port SFF-8654 板 | $237–603 |
| [M09] | | AliExpress 10×SFF-8654 扩展卡 | $445 |
| [M10] | | AliExpress 10-port 裸板 | $245 |
| [M11] | N19 | AliExpress 5-slot kit | $715 |
| [M12] | N20 | AliExpress retimer 卡 | $132 |
| [M13] | | AliExpress 8654 → 2×x16 拆分卡 | $19.35 |
| [M14] | | c-payne PM50100 | 约 €2,000 |
| [R08] | | c-payne Gen5 目录 | 缺货 |
| [R09] | | LocalLLaMA：Gen5 switch vs 新主板 | |
| [N12] | | eBay WRX80E-SAGE 已售 | $999.95 |
| [N13] | | eBay WRX80E-SAGE 已售 | $1,125 |
| [N14] | | PassMark 5955WX | 弱锚点 |
| [R10a] | | Kingston WRX80E 兼容表 | 内存不可混插 |
| [X03] | | eBay：EPYC 7532 + H12SSL-i 组合 | 约 $1,370 |
| [X04] | | pcserverandparts：2026 DDR4 服务器内存价格 | 32GB RDIMM 翻新 $110–359，新品接近 $400 |
| **多 PSU 供电** ||||
| [X05] | | Linux PCI j721e 补丁（引用 PCIe CEM 规范） | T_PVPERL：电源稳定后至少 100ms 才能释放 PERST#；REFCLK 稳定后至少 100µs |
| [X06] | | Level1Techs：ROMED8-2T 4×3090 双 PSU 安全 | 跨 PSU 倒灌烧卡；推荐 PDB / 带电 riser / 同卡同源 |
| [X07] | | Hiveon：add2psu 拉不起第二台 PSU | 继电器同步板的失败案例 |
| [X08] | | Level1Techs：Multiple power sources question | 同一部件的所有供电来自同一台 PSU |
| **switch kit 选型** ||||
| [X09] | | c-payne SlimSAS gen4 x8/x16 设备转接板 | 必须接 12V 供电，€40 |
| [X10] | | SFF-8654 8i×2 → PCIe 4.0 x16 转接板（ubbcentral） | 带 6-pin 12V 输入 |
| [X11] | | Level1Techs 长帖 #950：PLX88096 4 槽版停产，新 5 槽版 | 去掉了 24-pin；槽距 40.6mm |
| [X12] | | c-payne PM40084 4×x16 switch | 4 个 EPS（2 个必插）；"Intel Mainstream ... not compatible" |
| [X13] | | c-payne PM40100 5×x16 switch | 3 个必插 EPS；81.28mm 槽距；Intel 消费级平台有兼容问题 |
| [X14] | | r/LocalLLM：Frankenserver（约 2026-10-05，493 赞；2026-10-06 核对） | 4×2000W PSU 在 120V 下按约 4000W 计、2 条 20A 回路；计划再加 2 块 PEX88096 和更多电源；需要 retimer 才稳定；WRX80E-SAGE SE WiFi II 不支持嵌套 switch 且 AER storm；约 $500 的 PEX 卡"certainly salvaged units"；8i 线和转接板必须正确支持 presence 信号 |
| [X15] | | r/homelab：Help me understand these plx switches（4 个月前；2026-10-06 核对） | OP 怀疑 molex 不够给所有 slot 供电、"might need an extra power supply"；回帖：每槽 75W、5 槽 375W，主板供不起；开销清单第一项 "+ Separate PSU" |
| **P2P / 带宽实测** ||||
| [M44] | N21 | LocalLLaMA：P2P 补丁驱动多卡实测 | |
| [R06] | | LocalLLaMA：消费卡 P2P 收益 | pp 提升 40% |
| [M41] | | ROCm：7900XTX x4 TP | |
| [M42] | | ROCm：7900XTX x4 TP 续帖 | |
| [M43] | | ROCm：双 RX9070 x8 P2P | 14.27 GB/s |
| **4×5090 / 双 5090 实建** ||||
| [M22] | | 4×5090 选型帖 | |
| [M23] | | 7970X TRX50 水冷 4×5090 | |
| [M24] | | 商用 4×5090 | 限 450W + 双 1600W |
| [M25] | | 4×5090 只有 50 t/s（llama.cpp split） | |
| [M26] | | EPYC 4×5090 BOM | 400W 下限 |
| [M27] | | vast.ai 4×5090 | 双 1600W |
| [M28] | | 消费板 4×5090 讨论 | |
| [M29] | | ProArt X870E 双 5090 x8/x8 | |
| [M33] | | X870E HERO M.2 抢 lane | |
| [M34] | | 双 5090 x8/x8 + 1600W | |
| [M35] | | Taichi Lite 双 5090 掉 Gen1 | |
| [R07] | | nvidia：5090 黑屏，建议降 Gen4 | |
| **x8 / Gen / 单卡锚点** ||||
| [M30] | | X570 x8/x8 5090+3090 | |
| [M31] | | B850 AI TOP x8/x8 | |
| [M32] | | W790 双 5090 工作站 | |
| [M36] | | 5090 Gen5 x8 无惩罚；offload 会打满链路 | |
| [M37] | | 单 5090 27B NVFP4 262K | 77 tok/s |
| [M38] | | Flash-Next IQ3_S 限瓦 | 150–200 t/s |
| [M39] | | Gamers Nexus PCIe 缩放测试 | 游戏，不外推 |
| [M40] | | pcmasterrace x8 vs x16 | 游戏，不外推 |
| [M46] | | 5090 限 475W 27B | 208 tok/s |
| **8 卡** ||||
| [M15] | | DeepSeek V4 Flash 8×5090 | 2000+ t/s |
| [M16] | | AtomicChat 8×5090 量化基准 | |
| [M17] | | Unravl 配置 repo | |
| [M18] | | 8×RTX Pro 6000 | 炸电源案例 |
| [M19] | | 8×4090D | 4×2000W |
| [M20] | | H12SSL-i 8×3090 跑一年 | |
| [M21] | | ROMED8-2T riser 翻车 | |
| **供电风险** ||||
| [M47] | N22 | 12V-2x6 熔毁警示 | 只作风险警示 |

[N01]: https://rog.asus.com/motherboards/rog-crosshair/rog-crosshair-x870e-hero/spec/
[N02]: https://www.broadcom.com/products/pcie-switches-retimers/expressfabric/gen4/pex88096
[N03]: https://github.com/abtraore/QWEN-PEDIA/blob/main/recipes/qwen3.8-flash-next/README.md
[N04]: https://www.amd.com/en/newsroom/press-releases/2022-3-8-new-amd-ryzen-threadripper-pro-5000-wx-series-proc.html
[N05]: https://www.asus.com/us/motherboards-components/motherboards/workstation/pro-ws-wrx80e-sage-se-wifi-ii/
[N06]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
[N07]: https://github.com/vllm-project/vllm/blob/main/vllm/envs.py
[N08]: https://github.com/vllm-project/vllm/issues/51513
[N09]: https://docs.nvidia.com/cuda/wsl-user-guide/
[N10]: https://rog.asus.com/us/motherboards/rog-strix/rog-strix-z790-a-gaming-wifi-d4-model/spec/
[N11]: https://www.ovidiudan.com/2026/09/17/gpu-expansion-box-pcie-switch.html
[N12]: https://www.ebay.com/itm/287399256358
[N13]: https://www.ebay.com/itm/800401508435
[N14]: https://www.cpubenchmark.net/cpu.php?id=4767
[N18]: https://forum.level1techs.com/t/a-neverending-story-pcie-3-0-4-0-5-0-6-0-sci-fi-bifurcation-adapters-switches-hbas-cables-nvme-backplanes-risers-extensions-the-good-the-bad-the-ugly-will-there-be-a-final-solution/171428?page=46
[X01]: https://raw.githubusercontent.com/aikitoria/open-gpu-kernel-modules/461d638b7a91f73702001e343ec91b275a43ec35/README.md
[X02]: https://docs.vllm.ai/en/v0.23.0/api/vllm/distributed/device_communicators/custom_all_reduce/
[X03]: https://www.ebay.de/itm/155864653317
[X04]: https://pcserverandparts.com/news/refurbished-ddr4-server-memory-2026-server-ram-price-crisis/
[X05]: https://lists.infradead.org/pipermail/linux-arm-kernel/2023-July/850966.html
[X06]: https://forum.level1techs.com/t/dual-psu-safety-on-romed8-2t-with-4x-3090/246583
[X07]: https://hiveon.com/forum/t/unable-to-boot-the-2nd-psu-with-add2psu/59541
[X08]: https://forum.level1techs.com/t/multiple-power-sources-question/121422
[X09]: https://c-payne.com/products/slimsas-pcie-gen4-device-adapter-x8-x16
[X10]: https://ubbcentral.com/store/item/SlimSAS-8i-x2-to-PCIe4-0-x16-Slot-Adapter-SFF8654-Riser-Card-GEN4-for-Network_374904846028.html
[X11]: https://forum.level1techs.com/t/a-neverending-story-pcie-3-0-4-0-5-0-6-0-sci-fi-bifurcation-adapters-switches-hbas-cables-nvme-backplanes-risers-extensions-the-good-the-bad-the-ugly-will-there-be-a-final-solution/171428/950
[X12]: https://c-payne.com/products/pcie-gen4-switch-4x-x16-microchip-switchtec-pm40084
[X13]: https://c-payne.com/products/pcie-gen4-switch-5x-x16-microchip-switchtec-pm40100
[X14]: https://reddit.com/r/LocalLLM/comments/1wy1o7y/frankenserver_its_alive_its_alive/
[X15]: https://reddit.com/r/homelab/comments/1tyked9/help_me_understand_these_plx_switches/
[R03]: https://reddit.com/r/LocalLLM/comments/1wb7vxs/we_dont_judge_frankenstein_4x3090_testing_complete/
[R05]: https://reddit.com/r/homelab/comments/1vrcsle/chassis_for_plx88096_gpu_board/
[R06]: https://reddit.com/r/LocalLLaMA/comments/1vj7wey/enabling_pcie_p2p_for_consumer_nvidia_cards_will/
[R07]: https://reddit.com/r/nvidia/comments/1ihmwnu/troubleshooting_rtx_5090_black_screen_failures/
[R08]: https://c-payne.com/collections/pcie-packet-switch-adapters-gen5
[R09]: https://reddit.com/r/LocalLLaMA/comments/1tqvel3/pcie_gen5_switch_vs_new_mb/
[R10a]: https://www.kingston.com/en/memory/search/model/107082/asus-pro-ws-wrx80e-sage-se-wifi-ii
[R10b]: https://www.ovidiudan.com/tags/hardware/
[M01]: https://reddit.com/r/LocalLLaMA/comments/1pt0av6/plxpex_pcie_40_seems_to_help_for_llms_and_p2p_ie/
[M02]: https://www.reddit.com/r/homelab/comments/1vlk959/pex88096_for_pcie_expansion_doubt_about_upstream/
[M03]: https://reddit.com/r/LocalLLaMA/comments/1vthcwk/the_boring_way_to_run_deepseek_v4_flash0731/
[M04]: https://www.reddit.com/r/LocalLLaMA/comments/1wpczeb/dailychained_plx_88096_switches_quad_rtx_5070_ti/
[M05]: https://reddit.com/r/LocalLLaMA/comments/1qeimyi/7_gpus_at_x16_50_and_40_on_am5_with_gen54/
[M06]: https://www.reddit.com/r/homelab/comments/1pt0g6n/resource_for_pcie_switching_how_it_helps_on_llms/
[M07]: https://www.reddit.com/r/LocalLLaMA/comments/1pjjr02/pcie_to_mcio_no_more_dodgy_risers/
[M08]: https://www.aliexpress.us/item/3256812849867781.html
[M09]: https://www.aliexpress.us/item/3256812710866317.html
[M10]: https://www.aliexpress.us/item/3256812919568063.html
[M11]: https://www.aliexpress.us/item/3256812792537969.html
[M12]: https://www.aliexpress.us/item/3256812327244857.html
[M13]: https://www.aliexpress.us/item/3256812338362363.html
[M14]: https://c-payne.com/products/pcie-gen5-mcio-switch-100-lane-microchip-switchtec-pm50100
[M15]: https://reddit.com/r/LocalLLaMA/comments/1vfdbsr/deepseek_v4_flash0731_2000_tps_on_8x_5090_for_25/
[M16]: https://reddit.com/r/LocalLLaMA/comments/1vlurlv/we_quantized_deepseek_v4_0731_and_benchmarked_it/
[M17]: https://github.com/Unravl/deepseek-v4-flash-5090
[M18]: https://www.reddit.com/r/LocalLLaMA/comments/1plwgun/8x_rtx_pro_6000_server_complete/
[M19]: https://www.reddit.com/r/LocalAIServers/comments/1u9s6kh/i_built_a_8x_rtx_4090d_with_192_vram_heres_what_i/
[M20]: https://www.reddit.com/r/LocalLLaMA/comments/1phcyvk/after_1_year_of_slowly_adding_gpus_my_local_llm/
[M21]: https://www.reddit.com/r/LocalLLaMA/comments/1qc81si/built_an_8_rtx_3090_monster_considering_nuking_it/
[M22]: https://reddit.com/r/LocalLLaMA/comments/1mizar6/what_pc_specs_do_i_need_for_an_efficient_4x_5090/
[M23]: https://reddit.com/r/LocalAIServers/comments/1u8u7dj/finally_found_where_i_fit_in/
[M24]: https://reddit.com/r/LocalAIServers/comments/1wuvbe5/full_build_4x_rtx_5090_128gb_vram_to_serve_a_team/
[M25]: https://reddit.com/r/LocalLLM/comments/1wdugyy/4x5090_and_only_like_50toks_running_320b_moe/
[M26]: https://reddit.com/r/LocalLLaMA/comments/1mhu9tx/help_building_an_price_efficient_inference_server/
[M27]: https://reddit.com/r/vastai/comments/1tmikqx/new_build_sanity_check/
[M28]: https://reddit.com/r/nvidia/comments/1ktwaao/any_desktop_motherboard_that_can_support_4x_rtx/
[M29]: https://reddit.com/r/homelab/comments/1whd1a1/motherboard_options_for_running_dual_rtx_5090s_on/
[M30]: https://reddit.com/r/LocalLLaMA/comments/1n4n9yx/56gb_vram_achieved_gigabyte_5090_windforce_oc/
[M31]: https://reddit.com/r/LocalLLaMA/comments/1uavhsb/glm_52_ud_iq2_m_thats_the_best_pelican_svg_image/
[M32]: https://reddit.com/r/AutonomousLounge/comments/1u98isx/building_a_dual_rtx_5090_local_ai_workstation/
[M33]: https://reddit.com/r/ASUSROG/comments/1mn2ge0/need_help_with5090_with_9950x3d_running_at_pcie/
[M34]: https://www.reddit.com/r/LocalLLaMA/comments/1kl505t/dual_5090_80k_context_prompt_evalinference_speed/
[M35]: https://www.reddit.com/r/ASRock/comments/1nqjf7d/x870e_taichi_lite_dual_5090_only_pcie_gen1/
[M36]: https://reddit.com/r/LocalLLaMA/comments/1wmoqgz/5090_3090_qwen38_27b_and_flashnext_at_60k160k/
[M37]: https://reddit.com/r/LocalLLaMA/comments/1vvl7pc/single_rtx_5090_qwen3827b_nvfp4_at_a_real_262k/
[M38]: https://reddit.com/r/LocalLLaMA/comments/1wvwssq/strata_on_a_power_limited_5090_and_96gb_of/
[M39]: https://gamersnexus.net/gpus/nvidia-rtx-5090-pcie-50-vs-40-vs-30-x16-scaling-benchmarks
[M40]: https://reddit.com/r/pcmasterrace/comments/1ogw8nf/5090_at_x8_pcie_50_vs_x16_pcie_50_lanes/
[M41]: https://reddit.com/r/ROCm/comments/1vyfisx/notes_on_dual_7900_xtx_split_mode_tensor/
[M42]: https://reddit.com/r/ROCm/comments/1w14qal/dual_7900xtx_tensor_parallel_on_limited_pcie_x4/
[M43]: https://reddit.com/r/ROCm/comments/1w8d4p6/results_pcie_bandwidth_of_a_dual_rx9070_pc_setup/
[M44]: https://reddit.com/r/LocalLLaMA/comments/1n3qcqn/patched_p2p_nvidia_driver_now_works_with_multiple/
[M45]: https://github.com/aikitoria/open-gpu-kernel-modules
[M46]: https://reddit.com/r/Qwen_AI/comments/1vv39n5/got_qwen38_27b_running_locally_with_dspark_on_my/
[M47]: https://reddit.com/r/pcmasterrace/comments/1u85htp/my_turn_today_boys_caught_it_before_it_turned/

---

## 附录 B：版本记录

### v3.9（2026-10-05）：Z790 纯 Ubuntu + 多 PSU 安全设计

1. 按用户选择，推荐路线改为 **A2**：Z790 跑纯 Ubuntu Server，X870E 保持 Win10。A1 改为内存不足时的回退方案，DDR5 混插调参移到附录 C。
2. 新增 128GB 内存缓解措施（最小化系统、swap / zram、检查 CPU 侧 KV 缓冲）；G4 增加内存峰值检查。
3. 新增 §6.1 多 PSU 查证结论：
   - REFCLK 与 PSU 无关；
   - 少卡的原因是上电时序（CEM T_PVPERL 100ms，[X05]）；
   - 烧卡的原因是 12V 倒灌（[X06]）。
4. 供电设计改为"同卡同源 + 同步上电 + 共地"。kit 选型（§3.2）改为优先选每槽独立供电输入的一体背板，其次是分体 kit；§3.4 增加供电输入和上电时序两个询问项。
5. §6 改为：旧 1200W 作 PS_ON 主控，只带 host 和 switch；1600W 带 GPU0/1 及其槽供电；新 1200W 带 GPU2；1000W 带 GPU3。AC 回路改为 1600W + 旧 1200W 一条、新 1200W + 1000W 一条。
6. G1 增加"连续冷启动 10 次，4 卡全部识别"；新增少卡排障流程。
7. 阶段 2：X870E 不再作为第二岛，第二岛需要新 host。
8. 新增来源 X05–X08。
9. 补充：DDR4 确认为全新 4×32GB 同一套装；§1.2 加上 r10 的含义说明。
10. 查证每槽独立供电：
    - ADT-Link 5 槽背板槽距 40.6mm，4×5090 放不下；
    - c-payne 的 switch 板写明不兼容 Intel 消费级平台；
    - 改为推荐分体 kit：host 里插 switch 卡，每张 GPU 一块带 12V 输入的转接板。新增 Intel 兼容性风险，新增来源 X09–X13。
11. §6.1 新增"社区 PEX88096 实建都是多电源供电"，§6.4 补充服务器电源实例。引用 [M03]、[M04]（已有编号，补充了供电要点）和新增的 [X14]、[X15]。
12. 2026-10-06 对照用户粘贴的全文逐帖核对这 4 条：
    - 修正 [X15] 的措辞：OP 原话是"怀疑 molex 不够、可能需要额外电源"，不是定论；
    - 修正 [X14] 的日期为约 2026-10-05；
    - 补充核对中发现的信息：120V 下服务器电源降额实例、WRX80E 嵌套 switch 问题、拆机 PEX 卡、presence 信号、`intel_iommu=off` 的替代做法；
    - 风险表新增两行。


### v3.8（2026-10-05）：按实际资产更正

1. 资产更正：DDR5 是 **4×48GB**（目前只插了 2 根）；PSU 是 **1600W ×1 + 1200W ×2 + 1000W ×1**。
2. 推荐路线由 A2（Z790，128GB DDR4，余量仅约 3GB）**改回 A1**（X870E，插满 4×48GB = 192GB）；A2 降为兜底方案和 §8 的第二个岛。
3. 新增 4 根 DDR5（2DPC 双 rank）降频与稳定性说明，新增验收 Gate **G-1**；新增"X870E / Z790 角色互换"选项，解决双启动问题。
4. §6 供电按 4 台 PSU 重新设计：每台只带 1 张卡的 12V-2x6，主机和背板接 1600W；575W 不限瓦时每台负载也不超过约 65%；给出 AC 回路分配和 20A 要求；≤400W 时可省一台。
5. 成本：A1 内存从"需询价"改为 $0；同步板预算调整为支持 4 台 PSU。
6. host RAM 门槛改为"≥160GB 留余量，128GB 只算勉强可用"。
7. 补充更正：
   - 只有旧 1200W 没有 12V-2x6，1600W 有 2 根。§6 改为：旧 1200W 带主机和背板；1600W 带 GPU0 + GPU1；新 1200W 带 GPU2；1000W 带 GPU3。回路 1 = 1600W + 1000W，回路 2 = 两台 1200W。
   - 内存是两套芝奇 DDR5-6000、时序不同：§3.1 新增混插调参步骤（不用 EXPO，查颗粒，取较松时序，5200 起步）。

### v3.7（2026-10-05）

**方案层：**

1. 新增**路线 A2**（Z790-A D4 + 现有 DDR4 + PEX88096，做成独立 Linux 服务器），设为推荐方案。理由：r10 要求 125GB host RAM，X870E 的 96GB 不够；A2 内存零新增，主力机也不用双启动。
2. 新增**路线 C**（EPYC SP3）作为 B2 的比价项；新增"内存复用决定路线排序"的判断（2026 DRAM 涨价）。
3. 新增**阶段 0**（买 switch 前用现有 2×5090 验证补丁驱动）和决策树。
4. 8 卡阶段新增"两台现有主机各挂一套 kit"的最省钱路径。

**技术修正：**

5. BAR1 从 16GiB 改为 **32GiB**（5090 显存 32GB）。
6. R3 混卡 P2P 结论更新：新版 aikitoria 支持跨代，需打 libcuda 补丁。
7. 新增"上游 vLLM 在多于 2 张 PCIe GPU 时禁用 custom AR"，验收必须用 r10 overlay 和 `VLLM_CUSTOM_AR_ALLOW_PCIE`。
8. 驱动版本固定为 610.57.04 + iommu=pt；ACS setpci 改为 systemd 开机持久化。
9. host 聚合带宽：说明 PLE 走 UVA 是小粒度随机读，更受延迟影响，用 G4/G5 实测判定。
10. 当前 GGUF/llama.cpp 栈需切换为 vLLM TP4 + NVFP4；补上 135GB 磁盘和 mlock 要求。

**验收、供电、成本：**

11. 验收改为 G0–G6 分级 Gate，带量化门槛；新增 AER/replay 计数、Xid、24h soak、接头测温。
12. 供电按实际库存 1800/1200/1000W 重排，补上"背板给 4 个槽供电导致跨 PSU"的处理。
13. 成本修正：路线 A 小计统一为 $665–1,120，含 retimer 的最坏情况改为 $1,250–1,780。

**文档层：**

14. 一页结论前置；版本旁注（v2/v3/v3.4）并入正文；§0.5 调研压缩为 §10。
15. 参考来源去重：v3.6 的 N/R/M 三套编号中有 11 个重复 URL，合并为每个 URL 一个 ID，旧编号列为别名。共 74 条，旧链接全部保留。新增 X01–X04。
16. 改用 Markdown 引用式链接，正文不再夹完整 URL。
17. 新增风险登记表、待确认问题（工作负载形态、DDR4 清点、5090 卡厚）。

### 更早版本

- **v3.6**：给原方案来源登记 M01–M47 并插入文内引用。
- **v3.5**：cited-merged。
- **v3.4**：Reddit 深度调研 R01–R10。
- **v3**：新增 WRX80 路线和 Qwen3.8 专项基准。
- **v2**：删除 X870E 直拆四卡；retimer 改为按需；NCCL/vLLM 改为"先验证，再强制"。

## 附录 C：回退 A1 时的 DDR5 混插调参

仅在 A2 的 128GB 内存不够、需要把 kit 搬到 X870E 并双启动 Linux 时使用。插槽规则：PCIEX16_1 独占，PCIEX16_2 空着，M.2_2/M.2_3 不插（[N01], [M33]）。

**X870E 4×48GB DDR5（两套芝奇 2×48GB DDR5-6000 混插，时序不同；2DPC 双 rank）：**

- **EXPO 不能用。** 两套时序不同，EXPO 只能套用其中一套的配置；而且 4 根双 rank 在 AM5 上跑 6000 基本不现实。频率和时序要手动设置。
- **先查颗粒。** 用 ZenTimings / CPU-Z 的 SPD 页或 Thaiphoon Burner，看两套是否同为 SK Hynix 24Gb（48GB 条常见颗粒）。
  - 同颗粒：混插难度主要在时序，问题不大。
  - 不同颗粒（如一套 Hynix、一套 Samsung）：要预期更低的频率。
- **调参步骤：**
  1. 先更新到最新 BIOS（新 AGESA 对 4 根大容量条的支持更好）。插满 4 根，全部 Auto，先确认能开机。首次训练 192GB 可能要好几分钟，属正常。
  2. 手动设置 **DDR5-5200**；主时序（CL / tRCD / tRP / tRAS）**逐项取两套里较大（较松）的值**，其余保持 Auto；VDD/VDDQ 不超过两套 EXPO 中较高的那个电压。
  3. 跑 MemTest86 至少 1 轮，加 TestMem5（anta777 extreme 配置）。通过后可以试 5600；**不通过就降到 4800**。
  4. 稳定后再打开 Memory Context Restore 缩短开机时间；之后改任何内存设置都要重测。
- 插法：4 槽全插，每个通道一根 A 套、一根 B 套，或每套占一个通道，两种都可以；选能稳定通过测试的那种。
- 频率低一些对本方案影响很小（GPU↔GPU 在 switch 内，host 只走一条约 31.5 GB/s 的上行；即使降到 DDR5-3600，双通道约 57 GB/s 也高于它）。**稳定性远比频率重要**：推理服务 24/7 运行，内存错误会表现为难以复现的崩溃。

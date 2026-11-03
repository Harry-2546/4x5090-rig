# 4×RTX 5090 + PEX88096 实施计划（精简版）v1.8

- 版本：**lite v1.8**（2026-10-30）
- 上一版：lite v1.7（2026-10-28）
- 依据：[5090-multi-gpu-plan-v3.9.md](5090-multi-gpu-plan-v3.9.md)（2026-10-06）。论证、备选平台、8 卡扩展和完整来源都在完整版里，本文只保留 4 卡 88096 的执行方案。
- 约定：被替换或已不适用的内容没有删除，用 `<!-- 已注释 vX.X：原因 -->` 注释掉保留。

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.8 | 2026-10-30 | **4 卡跑通，写入实测**：3 张以上卡开机卡在 Q-LED VGA，原因是 BIOS 的 64-bit 窗口只有 256GiB；改为 BIOS Re-Size BAR = Off + 内核参数 `pci=nocrs` + 开机服务 `gpu-rebar.service`（加载驱动前把 BAR1 放大到 32G 并重新扫描 switch），写入 §3 第 4 步"4 卡 BAR"和启动 profile 3；switch 实测 ID `1000:c010`，卡内两级结构（topo 多为 PXB）；线序定为 X1 → 转接板 ②、X2 → 转接板 ①；新增 §4.1 实测记录（4 卡 P2P 单向 28.6 / 双向 56.5 GB/s）；功率上限改为默认不设（用户决定，以 §2.4 满载测试为准），§2.4 分阶段加负载随之调整；版本冻结新增"不升级到 7.x 内核"（[X33]、[X34]）；§5 新增 VGA 卡住和 gpu-rebar 排查两行 |
| v1.7 | 2026-10-28 | **主板型号更正**：推理服务器主板是 ROG STRIX **Z690-A** GAMING WIFI D4（此前误写为 Z790-A D4），全文统一改正，规格引用改为 [X31] 和用户手册 [X32]；按手册更正 M.2_1 说明（CPU 直连 PCIe 4.0 x4，手册未列与 PCIEX16(G5) 共享）；注明第二个 x16 长槽来自芯片组、只有 PCIe 3.0 x4，不能插 switch 卡；记录进度：BIOS 已是最新、4×32GB 全部识别、JEDEC DDR4-2666 CL19、MemTest86+ 0 错误、决定 XMP 保持关闭；BIOS 设置表补充常见菜单位置和 ASUS User Profile 存档。**补充（2026-10-28）**：系统盘保留在 M.2_1（CPU 直连 x4，手册未列与 x16 共享），取消"M.2_1 先空槽"的 A/B，改为到货验收时直接确认 switch 上行是 16GT/s x16，只有异常时才挪盘 |
| v1.6 | 2026-10-24 | 同步板由"两块串联"改为**星形**：两块都直接从 PSU-H 的外设（Molex）口取电；写入具体型号（主用 B077VQL5NT，备件 B08F9WGLP2 / B09Q11WG4Z）和安装要求；更正 §2.5 中同步线发烫报告的引用（原误引 [X26]，改为 [X30]）；新增 [X27]–[X30] |
| v1.5 | 2026-10-24 | 转接板 6-pin 改为借用转接线所在 PSU 线的空头，不再单独占插座；转接线 4 个头分到 4 根线上；GPU1 上限由 450W 提到 500W；Super Flower 实物确认 6 个 PCIe 插座，GPU3 默认 400W、G6 通过后最多 450W；记录 4×8-pin 转接线带 5090 已稳定使用一年 |
| v1.4 | 2026-10-24 | PSU 按实物核实结果重排：PC2 改为 3 台（Super Flower SF-1000F14MP 主控 / High Power 1300W / Corsair SF1000），MSI 1600W 留在 PC1；GPU1、GPU3 改用显卡原装英伟达 4×8-pin 转接线；新增按卡功率上限、§2.5 同步上电（继电器同步板）、§2.6 转接线规则；§2.4 测温加入转接线接头；物料表加入同步板和转接线；§5 新增无故断电排查；新增 [X22]–[X26] |
| v1.3 | 2026-10-21 | 供电改为单条 240V/30A dryer 回路（NEMA 10-30R）→ 成品 10-30P→L6-30R adapter → L6-30 PDU，注释掉 115V 双回路方案；新增 §2.1 供电链路、§2.2 电气风险与约束、§2.3 物理布置、§2.4 首次上电流程；PSU 负载表改为 400W 目标 / 500W 上限；新增功率上限开机自动设置；第 1 步新增 Z790 的 BIOS 更新、内存训练、BIOS 设置存档、Ubuntu Server 安装；BIOS 表新增 Secure Boot 关闭；G6 和 §5 改为按 PDU 读数判定 |
| v1.2 | 2026-10-20 | G1 的 LnkSta 速率改为**负载下**判定（5090 空闲会降到 2.5GT/s）；新增 `NVreg_EnableResizableBar=1`；第 1 步内存峰值改为模拟测试，真实测试移到 G3 之后；物料表改为实际到货的套装，新增 DIP / 成对接线 / 交叉线 / 6-pin 与 4-pin 说明；修正"转接板 DIP"为"switch 卡 DIP"；版本冻结改为禁止安装发行版 nvidia 驱动；MMIO 窗口估算改为约 192–256GiB；参考编号去冲突（`N11`→[X16]，`R10`→[X17]），新增 [X18]–[X21]。**补充（卖家答复）**：8654 线通用、两头相同；转接板白色 4-pin 是风扇口 |
| v1.1 | 2026-10-20 | 硬件已到货：注释掉采购确认项和采购步骤，新增"到货验收"；ACS 改用 `pci=disable_acs_redir` 内核参数（注释掉 systemd 方案）；新增 3 个启动 profile（realloc A/B）；G1 改为 LnkCap / LnkSta 两层判定并加入 BAR 检查；补充内核 / 驱动冻结与升级流程；修正 AC 回路算术，改为优先使用 20A 回路；M.2_1 改为先空槽测 baseline 再做 A/B；ASPM 说明改写；新增风险排序 |
| v1.0 | 2026-10-06 | 初版 |

---

<!-- 已注释 v1.7：v1.0–v1.6 正文中的 "Z790" / "Z790-A D4" 是主板型号记错，本版已统一改为 Z690 / Z690-A D4；逐处原文见 v1.6 -->

## 0. 方案一览

| 项目 | 决定 |
|---|---|
| 推理服务器 | ROG STRIX **Z690-A** GAMING WIFI D4 + i7-12700K + 4×32GB DDR4（G.Skill F4-3600C18，同一套装，128GB；**按 JEDEC DDR4-2666 CL19 运行，XMP 关闭**），**纯 Ubuntu Server** |
| 日常机（PC1） | X870E + 9950X3D + MSI 1600W + 2×5090，继续跑 Win10，不改动，不接 240V PDU，**不在本文范围**（触发回退方案时会被停用） |
| GPU fabric | PEX88096 **分体 kit**：switch 卡插在 Z690 的 PCIEX16(G5)（CPU 直连）；每张 GPU 用 2 根 SFF-8654 8i 线接一块带 12V 输入的 x16 转接板 |
| 链路 | 上行 1×Gen4 x16，下行 4×Gen4 x16，4 张卡在同一块 switch 卡内。卡内是两级 switch：`topo -m` 里同一下级 switch 的卡对显示 PIX，其余显示 **PXB**，P2P 带宽不受影响（§4.1） |
| 软件 | aikitoria P2P 驱动 610.57.04 + QWEN-PEDIA r10 配方（vLLM overlay，TP4 + EP，NVFP4） |
| 供电 | **3 台 PSU**：Super Flower 1000W（主控，带主机 + GPU3）、High Power 1300W（GPU0 + GPU1）、Corsair SF1000（GPU2）。**每张卡的转接板 12V 和 GPU 供电来自同一台 PSU**，全部同步上电；GPU1、GPU3 用英伟达原装 4×8-pin 转接线（§2.6）；**单条 240V/30A dryer 回路**：NEMA 10-30R → 成品 10-30P→L6-30R adapter → L6-30P 输入的 240V PDU（§2.1）；**功率上限默认不设（出厂 600W，用户决定），以 §2.4 满载测试为准**（§2） |
| 新增花费 | 约 $0.7k–1.15k（不含 retimer），已采购；adapter 和 PDU 另计 |
| 回退方案 | 内存不够，或 switch 在 Z690 上识别不到设备 / 分不到 BAR 时，把 kit 整体搬到 X870E（4×48GB = 192GB，AM5 已有成功案例） |
| **风险排序** | ① switch 卡 EEPROM/固件配置 → ② Z690 firmware 的 MMIO 窗口 → ③ 128GB 内存 → ④ 线材与链路训练 → ⑤ 补丁驱动的可复现性。**② 已在 2026-10-29 实际遇到并解决**（§3 第 4 步"4 卡 BAR"）。**另列：电气安全**（adapter 借用 10-30 的第三导体做保护连接，见 §2.2）不参与排序，按 §2.4 单独把关 |

<!-- 已注释 v1.8：§0 原"链路"行和"供电"行结尾
| 链路 | 上行 1×Gen4 x16，下行 4×Gen4 x16，4 张卡在同一 switch 内（PIX） |
供电行原结尾：每卡目标 400W，按卡设上限（§2）
-->

**为什么不用一体背板**：ADT-Link 5 槽背板槽距只有 40.6mm，4 张 5090 放不下（[X11]）；c-payne 背板写明不兼容 Intel 消费级平台（[X12]）；而且一体背板的槽供电通常共用一个入口，做不到"同卡同源"。

---

## 1. 物料清单（已到货）

| 项目 | 实际到货 / 规格要点 |
|---|---|
| PEX88096 switch 卡 | x16 金手指，10×SFF-8654 8i（口位成对标注 A1/A2、B1/B2、C1/C2、D1/D2、E1/E2）；**DIP 开关选模式**：FS1-1 = X16，FS1-2 = X8X8，FS1-3 = X4×4；卡上无辅助供电口，由主板插槽供电，白色 4-pin 只接风扇 |
| x16 转接板 × 5（用 4 块） | RBS-16G4-2PS4，双 8i 输入（标 ① ②）；右侧直角 **6-pin PCIe 供电口（丝印 GPU1）**；左侧白色 4-pin 是**风扇口**（卖家确认），可接风扇，不是供电输入 |
| SFF-8654 线 × 10（用 8 根） | 套装自带，60cm；卖家确认**线通用、两头相同**，不分方向。仍优先用这批线（阻抗、长度一致），坏了再换同规格的线 |
| switch 散热 | 卡上风扇 + 机箱气流；88096 待机也很热（[M04]） |
| PSU 同步 | 继电器同步板 × 2，**星形**：两块都从 PSU-H 的外设（Molex）口取电（§2.5）。主用 BAY Direct "2-Pack Add2PSU"（Amazon B077VQL5NT，[X27]）；备件 Thsion 2 块装（SATA 取电，B08F9WGLP2，[X28]），或带状态指示灯的 BQZYX+ 4 合 1（B09Q11WG4Z，[X29]） |
| 英伟达 4×8-pin → 16-pin 转接线 × 2 | 显卡原装，给 GPU1、GPU3 用（§2.6） |
| 矿架 / 测试台 | 转接板按卡厚固定，3 槽卡中心距 ≥ 80mm |
| Retimer | **默认不买**，只在 G1 链路不稳时再加（最坏约 $130 × 链路数） |

<!-- 已注释 v1.6：原同步板一行，按串联写法
| PSU 同步 | 继电器同步板（Add2PSU 类）× 2，串联带 2 台从电源（§2.5） |
-->

<!-- 已注释 v1.2 补充：卖家已答复（线通用、两头相同；白色 4-pin 为风扇口），原两行如下
| x16 转接板 × 5（用 4 块） | RBS-16G4-2PS4，双 8i 输入（标 ① ②）；右侧直角 **6-pin PCIe 供电口（丝印 GPU1）**；左侧另有一个白色 4-pin，用途待卖家确认 |
| SFF-8654 线 × 10（用 8 根） | 套装自带，60cm，卖家描述为 "intersection" / "AB crossover" 交叉线；**只用这批线** |
-->

<!-- 已注释 v1.2：采购前的物料规格，被上方实际到货清单替代
| 项目 | 规格要点 | 预算 |
|---|---|---:|
| PEX88096 switch 卡 | x16 金手指，10×SFF-8654 8i，固件配成 1×x16 上行 + 5×x16 下行（[M09] 卡价约 $446） | 与下两项合计 $575–850 |
| SFF-8654 8i 线 × 8 | 与 switch 卡**同一卖家**，≤50cm，问清阻抗（85Ω / 100Ω） | （含上） |
| x16 设备转接板 × 4 | 双 8i 输入，**每块自带 12V 输入**（6-pin / EPS，[X09], [X10]） | （含上） |
| switch 散热 | 卡上风扇 + 机箱气流；88096 待机也很热（[M04]） | $60–150 |
| PSU 同步线 / 同步板 | 支持 4 台 | $40–150 |
| 矿架 / 测试台 | 转接板按卡厚固定，3 槽卡中心距 ≥ 80mm | 已有或少量 |
| Retimer | **默认不买**，只在 G1 链路不稳时再加 | $0（最坏约 $130 × 链路数） |
-->

<!-- 已注释 v1.1：硬件已到货，采购前的卖家确认项不再适用；其中的检查点已并入 §1.1 到货验收

**下单前必须拿到卖家书面答复：**

1. 固件 / DIP 支持 **1×Gen4 x16 上行 + 4–5×Gen4 x16 下行同时工作**；提供 DIP 表和固件版本，SPI flash 已烧录。
2. 每块转接板都有独立 12V 输入，并说明接口类型；switch 卡本身由什么接口供电。
3. REFCLK / PERST# / presence 信号由卡和转接板正确处理；便宜的线材可能不传 presence 信号（[X14]）。
4. **在 Intel LGA1700 / Z790 上测试过吗？** 在 RTX 50 系上测试过吗？能否提供 `lspci -vv` 输出？
5. 多台 PSU 时的上电建议。
-->

### 1.1 到货验收（装整机之前，退货窗口内完成）

约 $500 的 PEX 卡多为拆机件（[X14]）；杂牌卡还有出厂即只报 Gen1 x4 的案例，原帖认为是 EEPROM 配错，跟帖认为更像没加载到有效配置，根因有争议（[X17]）。

1. 只接 switch 卡和 **1 张** GPU，开机，找到 switch 的 ID 和上行端口：
   ```bash
   lspci -nn | grep -iE 'Broadcom|PEX|PLX'
   lspci -tv
   ```
   **device ID 以这里的实际输出为准，不要用猜的。** 已知参考：[X17] 帖子里的 PEX880xx 卡是 `1000:c012`；88096 的 ID 未确认。
   **实测（2026-10-28）：本卡是 `1000:c010`**。卡内是两级 switch：上行 → 4 个下级 switch → 每个下级 switch 2 个下行口。
2. 看上行端口的**能力**（LnkCap），不只看协商结果（LnkSta）：
   ```bash
   sudo lspci -vv -s <上行端口BDF> | grep -E 'LnkCap:|LnkSta:|LnkCap2'
   ```
   - `LnkCap` 必须是 `Speed 16GT/s, Width x16`；
   - `LnkCap` 本身就是 Gen1 x4 一类 → switch 配置有问题。可以先查 `DLActive`、`PresDet` 和 dmesg 里的链路错误；c-payne 一类厂商可能有工具重配，但**退货最省事**（[X17]）。
   - **空载时只有 LnkCap 能下结论。** LnkSta 的**速率**要在 GPU 有负载时看：5090 空闲会降到 2.5GT/s，属正常省电（[X18]）。LnkSta 的**宽度**空载时也不应该降。
   <!-- 已注释 v1.2：原判定，根因表述过于肯定
   - `LnkCap` 本身就是 Gen1 x4 一类 → EEPROM 配置错误，用户手上没有工具可修，**直接退货**。
   -->
3. 下行端口同样检查 LnkCap；**switch 卡**的 DIP 设置和固件版本记录存档。
   <!-- 已注释 v1.2：DIP 在 switch 卡上，转接板没有 DIP
   3. 下行端口同样检查 LnkCap；转接板的 DIP 设置和固件版本记录存档。
   -->
4. 每块转接板的 12V 输入接口类型，switch 卡的供电接口，逐一核对。
5. 套装专属检查：
   - DIP 只拨 **FS1-1 = ON**，FS1-2 / FS1-3 = OFF；改 DIP 后整机断电再开机；
   - 1 张 GPU 测试时，接同一对口；**实测线序：编号 1 的口（A1/B1/C1/D1）→ 转接板 ②，编号 2 的口 → 转接板 ①**，反过来只训练到 x8；线两头相同，不分方向；
   <!-- 已注释 v1.8：线序已实测确定
   - 1 张 GPU 测试时，接同一对口（如 A1 + A2）到转接板 ① + ②；线两头相同，不分方向；
   -->
   - 这张卡只训练到 x8 或不识别时，先把 ① ② 两根线对调复测，再排查别的；
   - 转接板左侧白色 4-pin 是风扇口，可接风扇。
   <!-- 已注释 v1.2 补充：卖家已答复线通用、4-pin 为风扇口
   - 1 张 GPU 测试时，接同一对口（如 A1 + A2）到转接板 ① + ②；哪个口接 ① 以卖家答复为准；
   - 只用套装自带的交叉线；
   - 转接板左侧白色 4-pin 在确认用途前不接。
   -->
6. **单卡验收结果（2026-10-28，A 口 + 转接板 1 + 线 1/2）**：上行和 GPU 的 LnkCap 都是 Gen4 x16，负载下 LnkSta 也是 Gen4 x16；BAR1 32GiB；14 个下行口 ACSCtl 全为 0；AER 0；`nvbandwidth` H2D 23.66 GB/s、D2H 28.43 GB/s。**E 口、转接板 5、线 9/10 还没有单独测试**，退货期内补测。

---

## 2. 拓扑与供电

```text
Z690 PCIEX16(G5)（CPU 直连）
  └─ PEX88096 switch 卡（插槽供电 → 主板 → PSU-H）
       ├─ A1/A2 ─ 转接板0 ─ GPU0 ┐ PSU-1 High Power 1300W（GPU0 原生 12V-2x6）
       ├─ B1/B2 ─ 转接板1 ─ GPU1 ┘                        （GPU1 英伟达转接线）
       ├─ C1/C2 ─ 转接板2 ─ GPU2 ── PSU-2 Corsair SF1000（原生 12VHPWR）
       └─ D1/D2 ─ 转接板3 ─ GPU3 ── PSU-H Super Flower 1000W（英伟达转接线；同时带主机）
```

| PSU | 带什么 | 按卡功率上限 | 负载 @400W/卡（目标） | 负载 @上限 |
|---|---|---|---|---|
| **PSU-H Super Flower SF-1000F14MP**（旧平台：Intel 设计指南 v2.92，**无 ATX 3.x 瞬时过载余量**；无原生 16-pin；实物：**6 个 PCIe 插座**、4 个 SATA、2 个外设；PCIe 线 16AWG，[X23]） | Z690 主机（24-pin + EPS）+ switch 卡 + **GPU3**（英伟达转接线）+ 转接板 3；**PS_ON 主控** | GPU3 默认 400W；G6 通过后最多 450W | ~68% | ~73% |
| PSU-1 High Power HP1-O21300GD-F14C 1300W（ATX 3.x；实物：1 个 12V-2x6 600W 插座、**4 个 PCIe 插座**、2 个 CPU 插座，[X22]） | **GPU0**（原生 12V-2x6）+ **GPU1**（英伟达转接线）+ 转接板 0 / 1 | GPU0 ≤ 500W，GPU1 ≤ 500W | ~62% | ~77% |
| PSU-2 Corsair SF1000（SFX，ATX 3.1） | **GPU2**（原生 12VHPWR）+ 转接板 2 | GPU2 ≤ 500W | ~40% | ~50% |

**PCIe 插座分配（同卡同源；转接线每个头独占一根线，转接板借用空头）：**

转接板的 6-pin 只给 PCIe 插槽供电（12V 最多 66W），5090 从插槽取的电通常只有几十瓦；而且功率上限算的是整卡功率（插槽 + 16-pin），插槽多取一点，16-pin 就少一点。所以转接板不必单独占一个插座，借用同一台 PSU 某根线上空着的第二个头即可。

| PSU | 插座 | 头 1 | 头 2 | 最坏负载 |
|---|---|---|---|---|
| PSU-1 High Power | 12V-2x6（600W） | GPU0 | — | ≤ 500W |
| | PCIe #1 | GPU1 转接线 ① | 转接板 0（GPU0）的 6-pin | ≤ 约 125W + 66W ≈ 190W |
| | PCIe #2 | GPU1 转接线 ② | 转接板 1（GPU1）的 6-pin | ≤ 约 190W |
| | PCIe #3 | GPU1 转接线 ③ | 空 | ≤ 约 125W |
| | PCIe #4 | GPU1 转接线 ④ | 空 | ≤ 约 125W |
| | CPU × 2 | **不用**：EPS 和 PCIe 针脚定义不同，绝不混插 | | |
| PSU-2 Corsair | 12VHPWR | GPU2 | — | ≤ 500W |
| | 任一 PCIe | 转接板 2 的 6-pin | — | 很小 |
| PSU-H Super Flower | 24-pin、EPS | 主板、CPU | | |
| | PCIe #1–#4 | GPU3 转接线 ①–④（每根线 1 个头） | 空 | 每根 ≤ 约 115W（GPU3 ≤ 450W） |
| | PCIe #5 | 转接板 3 的 6-pin | 空 | 很小 |
| | PCIe #6 | 备用 | | |

- 66W 是规范上限，实际插槽取电远低于这个值。
- 用 6+2 头接转接板时只插 6-pin 部分，+2 让它空着。

<!-- 已注释 v1.5：原负载表和插座分配，转接板单独占插座、GPU1 两根线各带 2 个头、GPU1 上限 450W
| PSU | 带什么 | 按卡功率上限 | 负载 @400W/卡（目标） | 负载 @上限 |
|---|---|---|---|---|
| **PSU-H Super Flower SF-1000F14MP**（旧平台：Intel 设计指南 v2.92，**无 ATX 3.x 瞬时过载余量**；无原生 16-pin；PCIe 线 16AWG，[X23]） | Z790 主机（24-pin + EPS）+ switch 卡 + **GPU3**（英伟达转接线）+ 转接板 3；**PS_ON 主控** | GPU3 **固定 400W** | ~68% | ~68% |
| PSU-1 High Power HP1-O21300GD-F14C 1300W（ATX 3.x；实物：1 个 12V-2x6 600W 插座、**4 个 PCIe 插座**、2 个 CPU 插座，[X22]） | **GPU0**（原生 12V-2x6）+ **GPU1**（英伟达转接线）+ 转接板 0 / 1 | GPU0 ≤ 500W，GPU1 ≤ 450W | ~62% | ~73% |
| PSU-2 Corsair SF1000（SFX，ATX 3.1） | **GPU2**（原生 12VHPWR）+ 转接板 2 | GPU2 ≤ 500W | ~40% | ~50% |

**PCIe 插座分配（实物插座数决定，同卡同源）：**

| PSU | 插座 | 接什么 |
|---|---|---|
| PSU-1 High Power | 12V-2x6（600W） | GPU0 |
| | PCIe #1（线上 2 个头） | GPU1 转接线 8-pin ① ② |
| | PCIe #2（线上 2 个头） | GPU1 转接线 8-pin ③ ④ |
| | PCIe #3（用 1 个头） | 转接板 0 的 6-pin |
| | PCIe #4（用 1 个头） | 转接板 1 的 6-pin |
| | CPU × 2 | **不用**。EPS 和 PCIe 针脚定义不同，绝不混插 |
| PSU-2 Corsair | 12VHPWR | GPU2 |
| | 任一 PCIe（用 1 个头） | 转接板 2 的 6-pin |
| PSU-H Super Flower | 24-pin、EPS | 主板、CPU |
| | PCIe：GPU3 转接线 4 个头 + 转接板 3 的 1 个头 | **待目测**：至少要 3 个 PCIe 插座（2 根线各带 2 个头 + 1 根线给转接板）；有单头线的话优先用单头线 |
-->

<!-- 已注释 v1.4：原 4 台 PSU 的拓扑与负载表（1600 / 1200 新 / 1200 旧 / 1000），已按实物核实结果替换；MSI 1600W 留在 PC1
```text
Z790 PCIEX16_1（CPU 直连）
  └─ PEX88096 switch 卡（主机 PSU 供电）
       ├─ 2×8i ─ 转接板0 ─ GPU0 ┐ PSU-1 1600W
       ├─ 2×8i ─ 转接板1 ─ GPU1 ┘
       ├─ 2×8i ─ 转接板2 ─ GPU2 ── PSU-2 1200W（新）
       └─ 2×8i ─ 转接板3 ─ GPU3 ── PSU-3 1000W
```

| PSU | 带什么 | 负载 @400W/卡（目标） | 负载 @500W/卡（上限） |
|---|---|---|---|
| **PSU-H 1200W（旧，无 12V-2x6）** | Z790 主机 + switch 卡；**PS_ON 主控** | ~30% | ~30% |
| PSU-1 1600W | GPU0、GPU1 的 12V-2x6（2 个独立接口）+ 转接板 0/1 的 6-pin | ~50% | ~63% |
| PSU-2 1200W（新） | GPU2 的 12V-2x6 + 转接板 2 的 6-pin | ~33% | ~42% |
| PSU-3 1000W | GPU3 的 12V-2x6 + 转接板 3 的 6-pin | ~40% | ~50% |
-->

<!-- 已注释 v1.3：原负载表按 400W / 575W 计算；本版功率上限定为 500W
| PSU | 带什么 | 负载 @400W/卡 | 负载 @575W/卡 |
|---|---|---|---|
| **PSU-H 1200W（旧，无 12V-2x6）** | Z790 主机 + switch 卡；**PS_ON 主控** | ~30% | ~30% |
| PSU-1 1600W | GPU0、GPU1 的 12V-2x6（2 个独立接口）+ 转接板 0/1 的 12V | ~50% | ~72% |
| PSU-2 1200W（新） | GPU2 的 12V-2x6 + 转接板 2 的 12V | ~33% | ~48% |
| PSU-3 1000W | GPU3 的 12V-2x6 + 转接板 3 的 12V | ~40% | ~58% |
-->

**规则：**

- **同卡同源**：一张卡的所有 12V 来自同一台 PSU，避免 12V 倒灌烧卡（[X06]）。
- **同步上电**：PSU-1、PSU-2 通过继电器同步板跟随 PSU-H 启动（§2.5）。主机 POST 要几秒才释放 PERST#，GPU 的 12V 早已稳定，满足 PCIe 规范"供电稳定 100ms 后才释放 PERST#"的要求（[X05]）。
- **不单独断电**：运行中任何一台 PSU 都不能单独关；掉了一台就整机断电重启。
- GPU0、GPU2 用 PSU 原生 16-pin；GPU1、GPU3 用显卡原装的英伟达 4×8-pin 转接线，规则见 §2.6。任何卡都不用第三方转接线或 Y 线（[M47]）。
  <!-- 已注释 v1.4：PC2 只有 2 个原生 16-pin 口，GPU1、GPU3 必须用转接线
  - 每张卡用原生 12V-2x6，不用转接线，不用 Y 线（[M47]）。
  -->
- **AC 供电**：全部 PSU 插在同一个 240V PDU 上，走单条 240V/30A 回路，见 §2.1。
- **功率上限默认不设**（用户决定，2026-10-29）：4 张卡按出厂 600W 运行。不设上限时的持续负载估算：
  - High Power（GPU0 + GPU1）约 1200W，约 92%；
  - Super Flower（主机 + GPU3）约 850W，约 85%。它是旧平台、没有 ATX 3.x 瞬时余量，又是主控，触发保护就整机断电；
  - Corsair（GPU2）约 600W，约 60%。

  以 §2.4 有人值守的"4 卡同时满载 1 小时"为准：稳定就保持不设；出现掉卡（Xid 79）或断电，**只给出问题那台 PSU 带的卡设上限**（例如 GPU0 / GPU1 设 500W），其他卡照样不设。上表的按卡上限作为这时的参考值。LLM 推理的 decode 阶段通常远低于 600W，只有大批量 prefill 和压力测试才会顶满。
  <!-- 已注释 v1.8：原按卡上限规则
- 每张卡的功率上限开机自动设为 400W（§3 第 4 步"功率上限"）；要提高时按上表的按卡上限：GPU0 / GPU1 / GPU2 ≤ 500W，**GPU3 默认 400W，G6 通过后最多 450W**。
  -->
  <!-- 已注释 v1.5：GPU1 改为 500W，GPU3 允许在 G6 后到 450W
  - 每张卡的功率上限开机自动设为 400W（§3 第 4 步"功率上限"）；要提高时按上表的按卡上限：GPU0 / GPU2 ≤ 500W，GPU1 ≤ 450W，**GPU3 固定 400W**。
  -->
  <!-- 已注释 v1.4：上限改为按卡设置
  - 每张卡的功率上限开机自动设为 400W，任何时候不超过 500W（§3 第 4 步"功率上限"）。
  -->

<!-- 已注释 v1.3：原 115V 双回路方案，被单条 240V/30A 回路替代
- **AC 回路（115V）**：回路 1 = PSU-1 + PSU-H，回路 2 = PSU-2 + PSU-3。**优先两条独立 20A 回路**。
  - 持续负载按 NEC 125% 规则（[R16]），相当于：15A 回路持续 ≤ 12A，20A 回路持续 ≤ 16A。
  - 估算（PSU 效率按 92%，PSU-H 按约 360W DC）：

    | 每卡功率 | 回路 1：DC → AC → 电流 | 回路 2 | 结论 |
    |---|---|---|---|
    | 400W | 800 + 360 = 1160W → ≈1260W → **≈11.0A** | ≈7.6A | 15A 回路贴线，不作为生产配置 |
    | 575W | 1150 + 360 = 1510W → ≈1640W → **≈14.3A** | ≈10.9A | 必须 20A，离 16A 也不算远 |

  - 只有 15A 回路时：`nvidia-smi -pl 400` 或更低封顶。
  - 以上是估算，最终在 G6 用功率计或钳形表**按墙端实测**判定。
-->

<!-- 已注释 v1.1：原 AC 回路结论，被上方表格替代
  - 400W/卡：回路 1 约 11A，15A 回路可用；
  - 575W/卡：回路 1 约 14A，**必须是 20A 回路**。
-->

- **Super Flower（PSU-H）上机前先体检**：只接主机，满载 CPU 1 小时，观察 12V 电压和风扇。它是主控，又没有 ATX 3.x 的瞬时余量，出问题会导致整机掉电。
  <!-- 已注释 v1.4：原"旧 1200W"已不在本机
  - 旧 1200W 上机前先体检：接功率计带主机满载 1 小时，观察 12V 电压。
  -->

### 2.1 240V 供电链路

```text
配电箱 双极 30A（标注 "220 VOLT DRYER"）
  └─ 10/3 带地线 NM 电缆（护套印 "10/3 GROUND TYPE NM 600V"）
       └─ 墙插 NEMA 10-30R（老式 BELL，30A/250V；H + H + N，无独立地线）
            └─ 成品 adapter：NEMA 10-30P → L6-30R（短线，10AWG/3C，30A/250V，UL/ETL 可核实）
                 └─ 240V 单相 rack PDU：L6-30P 输入，带浪涌保护、电压/电流表
                      ├─ PSU-H Super Flower SF-1000F14MP（主控）
                      ├─ PSU-1 High Power 1300W
                      └─ PSU-2 Corsair SF1000
```

**负载估算**（PSU 在 240V 下效率按约 93% 计）：

| 每卡功率 | DC 合计 | AC 合计 | 240V 电流 | 30A 回路持续上限 24A（80%，[R16]） |
|---|---|---|---|---|
| 400W（目标） | 1600 + 275 = 1875W | ≈ 2.0kW | **≈ 8.4A** | 余量很大 |
| 按卡上限（500 / 500 / 500 / 450） | 1950 + 275 = 2225W | ≈ 2.4kW | **≈ 10.0A** | 余量很大 |

<!-- 已注释 v1.5：原按卡上限一行
| 按卡上限（500 / 450 / 500 / 400） | 1850 + 275 = 2125W | ≈ 2.3kW | **≈ 9.5A** | 余量很大 |
-->

<!-- 已注释 v1.4：原负载估算按 4 台 PSU、主机侧约 360W、统一 500W 上限计算
| 400W（目标） | 1600 + 360 = 1960W | ≈ 2.1kW | **≈ 8.8A** | 余量很大 |
| 500W（上限） | 2000 + 360 = 2360W | ≈ 2.5kW | **≈ 10.6A** | 余量很大 |
-->

- 这条 30A 回路**只给本机用**，不接其他负载。
- 换到 240V 后，原来 115V 双回路的 15A / 20A 问题不复存在；单条回路的电流也只有 115V 时的一半左右。
- **上电前要核对：**
  - 每台 PSU 铭牌都标有 `100–240V~`；
  - PDU 插座类型（C13 / C19）和每台 PSU 的电源输入口（C14 / C20）对应。在 240V 下每台 PSU 的电流都不超过约 7A，C13/C14 电源线足够；
  - PDU 如果带按插座组的分路断路器或远程开关，把所有插座组设为常通，不设定时 / 远程断电（遵守"不单独断电"）。
- PDU 的读数（电压、总电流）作为 §2.4 首次上电和 G6 验收的依据。

### 2.2 电气风险与约束（暂住、不改线前提下的已知取舍）

**adapter 的本质：** NEMA 10-30 是 Hot + Hot + Neutral，没有独立的设备地线（EGC）；L6-30 是 Hot + Hot + Ground，不需要 Neutral。市面上的 10-30P→L6-30R adapter 一般把 10-30 的第三导体（neutral）接到 L6-30 的地脚上。所以：

- **正常运行时**：L6-30 负载不走 neutral，这根导体上只有 PSU 滤波电容的泄漏电流（毫安级），不发热，PDU 和 PSU 都正常工作。
- **它的作用**：PDU、PSU 外壳、机架上金属件的"接地"，全部依赖这根 neutral 导体、它在墙插和配电箱 neutral 排上的两个端子，以及配电箱的 N-G 跨接。
- **失效模式**：这条路径上任何一处开路（例如老墙插端子松动），设备金属件就失去保护连接。此时如果再发生火线碰壳，所有外露金属可能带上对地约 120V 的电压，**而断路器不会跳**。
- **规范层面**：用 neutral 给设备外壳做接地，只有既有的电炉 / 烘干机这类设备有例外条款（NEC 250.140），其他设备不在例外之内（NEC 250.142(B)）。本方案明确不符合现行规范，是暂住条件下有意接受的取舍。
- **已有的低成本正规改法（记录在案，本方案不采用）**：电缆护套印的是 "10/3 GROUND"，说明线里很可能有一根地线，只是老式 10-30R 墙插没用上。征得房东同意后，由持证电工把墙插换成 L6-30R（或 14-30R），就能得到真正独立的地线，而且不用动墙内线路。

**在不改线前提下的缓解措施：**

1. **只用一个**成品 adapter：短线、10AWG/3C、30A/250V。在 UL Product iQ 或 Intertek ETL 目录里核实认证编号，不只看商品页的标志。不再串第二个 adapter，不 DIY 双插头，不另外借地线。
2. **可选：请持证电工"只检查、不改线"**：确认 10-30R 的 neutral 端子紧固、配电箱 neutral 排连接良好、N-G 跨接存在。这不改动任何线路，但能消除"neutral 是否可靠"这个未知数。
3. **避免形成第二条接地路径**：
   - 运行中只用网线（UTP）连接本机，用 SSH 管理；
   - 装机阶段临时接的显示器、键盘，也从同一个 PDU 取电；
   - 不用 HDMI、USB 等屏蔽线把本机长期连到插在其他回路上的设备。
4. 运行中避免一手接触机架金属、另一手接触其他接地物体（水管、洗衣机 / 烘干机外壳等）。
5. 地下室装烟雾报警器；附近放一个 ABC 干粉灭火器。

**操作安全边界（本人执行范围）：**
- 不做带电固定布线；不拆配电箱面板（dead-front），不拆墙插，不碰裸线。
- 普通橡胶手套、橡胶鞋不能让带电操作变安全，不作为防护依据。
- 插拔 10-30 / L6-30 时，PDU 总开关和所有 PSU 都处于关闭状态。

### 2.3 物理布置

- 开放式矿架 / 测试台，不追求外观；**PSU 不放进木盒**。
- PSU 放在干燥、硬质、不可燃（至少耐热）的表面上，四周留出进出风空间；不放地毯上。
- PSU 金属外壳保持原有的 PE 连接，不故意绝缘，不拆地脚。
- GPU、主板、PEX 卡都固定在矿架上；8i 线和电源线不承受拉力。
- 不混用不同 PSU 的模组线：每台 PSU 只用它自带的线，包括转接板 6-pin 用的 PCIe 线。
- GPU0、GPU2 用 PSU 原生 16-pin，GPU1、GPU3 用英伟达原装转接线（§2.6）；不用 Y 线；16-pin **完全插到底**，接口附近不急弯。
  <!-- 已注释 v1.4：GPU1、GPU3 改用转接线
  - 每张 5090 用 PSU 原生 12V-2x6，不用 Y 线；**完全插到底**，接口附近不急弯。
  -->
- adapter、L6-30 接头、PDU 输入线都放在地面以上，避开积水和踩踏的位置；L6-30 旋锁到位。

### 2.4 首次上电流程

1. 所有 PSU 关机，PDU 总开关关闭。
2. 检查墙插外观：无裂纹、无烧痕；adapter 插入后握持力正常，不松垮。老墙插夹持力不足本身就是发热隐患。
3. 插上 10-30P → L6-30R adapter。
4. 接 PDU，确认 L6-30 **旋锁到位**。
5. 各 PSU 接入 PDU；PDU 总开关打开，记录**空载电压**（正常约 230–250V）。
6. **分阶段加负载**，每个阶段稳定 5–10 分钟，记录 PDU 的电压和总电流：
   1. 只开主机，空载；
   2. 1 张 GPU 跑满（不设上限，最高 600W）；
   3. 2 张 GPU 跑满（先加 High Power 上的 GPU0 + GPU1，它是负载率最高的一台）；
   4. 4 张 GPU 同时跑满，**持续 1 小时**（这就是第 9 条要求的有人值守满载）。期间用 `nvidia-smi --query-gpu=index,power.draw,temperature.gpu,clocks.sm --format=csv -l 1` 每秒记录，并盯 `dmesg -w` 有没有 Xid / AER。
   <!-- 已注释 v1.8：原分阶段（按 400 / 500W 上限）
   2. 1 张 GPU 跑满（400W）；
   3. 4 张 GPU 都跑到 400W；
   4. 4 张 GPU 跑到 500W 上限。
   -->
7. **电压判据**：负载下的电压比空载下降超过约 2%（约 5V），说明链路上有某处接触电阻偏大。立即降负载，按第 8 条测温查找发热点。
8. **温度检查**：第一次运行后约 10–15 分钟、30 分钟、1 小时各查一次，用红外测温仪做非接触对比。检查以下位置有没有异常温升、焦味、变色或松动：
   - 10-30 墙插附近
   - adapter 两端
   - L6-30 接头
   - PDU 输入线
   - 各 12V-2x6 接头
   - GPU1、GPU3 转接线的 4 个 8-pin 头，以及它们在 PSU 端的插头

   **温升判据**：
   - 本机满载约 10A，只有这条 30A 链路额定电流的 1/3，接头温升本应很小。任何接头**比环境温度高 10°C 以上**就要排查，**高 20°C 以上**立即停机。
   - 4 个 12V-2x6 接头横向比较，某一个比其他明显高约 10°C 以上，就断电后重新插到底。
   - 转接线：同一根转接线的 4 个 8-pin 头之间横向比较；GPU1、GPU3 的 16-pin 和原生卡（GPU0、GPU2）对比；High Power 上和转接板共用的两根线（PCIe #1、#2）与另外两根对比。
9. **首次高负载不无人值守**，不过夜。至少完成一次有人值守的 1 小时满载，温度和电压都稳定后，再进入 G6 的 24h 压测。
10. 发现焦味、变色或温度异常：先在软件里降负载或停服务 → 关闭 PSU → 关闭 PDU 总开关 → 再拔插头。之后不再使用该 adapter 或墙插，联系房东或电工。


### 2.5 同步上电

| 角色 | PSU | 接法 |
|---|---|---|
| 主电源 | PSU-H Super Flower | 原厂 24-pin 接主板；主机电源键控制它 |
| 从电源 1 | PSU-1 High Power | 原厂 24-pin 插到同步板 A；同步板 A 的取电接 **PSU-H 外设口 #1** |
| 从电源 2 | PSU-2 Corsair SF1000 | 原厂 24-pin 插到同步板 B（SFX 电源同样有 24-pin 模组线）；同步板 B 的取电接 **PSU-H 外设口 #2** |

- **原理**：同步板上的继电器线圈由 PSU-H 的外设口供电，触点接在从电源的 24-pin 上。PSU-H 一开，外设口有电，继电器吸合，把从电源的 PS_ON#（第 16 脚）拉到地，从电源开机；关机时反过来（[X25]）。
- **星形接法**：两块同步板都**直接**从 PSU-H 取电，不串联。任何一台从电源出问题不会牵连另一台，两台也同时启动。取电**只接 PSU-H**，不接从电源自己的 Molex / SATA。
- **型号**：
  - 主用：BAY Direct "2-Pack Add2PSU"，Molex 取电，一次 2 块（[X27]）。Super Flower 正好有 2 个外设口。
  - 备件：Thsion 2 块装，SATA 取电（[X28]）；或 BQZYX+ 4 合 1，板上有 3.3V / 5V / 12V / PS-ON / 待机指示灯，排障时一眼看出哪台没开（[X29]）。
  - 这些都是通用板，品质有差异，所以必须做下面的上线前测试，并保留一块备件。
- **安装**：裸 PCB 用塑料支柱或绝缘垫固定在矿架上，不直接贴金属；24-pin 线不承受拉力。
<!-- 已注释 v1.6：原串联写法
- 用**继电器同步板（Add2PSU 类）**，两块串联：主电源一开，继电器就把从电源的 PS_ON 拉到地（[X25]）。同步板的取电接 PSU-H 的 Molex / SATA。
-->
- 同步板只传开机信号，**不连通任何供电线**；同卡同源仍然靠 §2 的插座分配保证。
- 不选"带供电线的 24-pin 同步线"：有用户报告便宜的同步线用了几小时后发烫（[X30]）。正常的同步只需要 PS_ON 和地线两根细线，发烫说明那款线的接法有问题。
- **上线前单独测试**（不接显卡和转接板）：
  1. 3 台 PSU 背后的开关都打开，按主机电源键：PSU-1、PSU-2 的风扇或指示灯应同时启动；关机时也应同时停；
  2. 用万用表量从电源一个空闲 PCIe 头上的 12V（低压直流，安全）；
  3. 冷启动重复 10 次，每次都必须跟随开、跟随关。有一次不跟随就换备件。
  4. 有评价提到个别高端 PSU 搭配继电器板时从电源启动偏慢；主机 POST 要几秒，通常不是问题，但 G1 的"冷启动 10 次 4 卡都识别"要照做。
  <!-- 已注释 v1.6：原第 3 条
  3. 冷启动重复 5–10 次，每次都必须跟随。有一次不跟随就换板。
  -->
- 运行中不单独关闭任何一台从电源（§2"不单独断电"）。

### 2.6 英伟达转接线规则（GPU1、GPU3）

- 只用**显卡原装**的英伟达 4×8-pin → 16-pin 转接线，不用第三方转接线，不用 Y 线。
- **4 个 8-pin 全部来自同一台 PSU**，和这张卡转接板的 6-pin 也是同一台（同卡同源）。
- **4 个都接满**：接 3 个能开机，但功率上限会被限制在约 450W；只接 2 个开不了机（[X24]）。接好后用 `nvidia-smi -q -d POWER` 确认 Max Power Limit 符合预期。
- **转接线的 4 个头各占一根 PSU 线**，转接板的 6-pin 借用空头（§2 插座分配表）。High Power 4 个插座、Super Flower 6 个插座都够这样接；Super Flower 的 PCIe 线是 16AWG（[X23]）。
- 本地经验：同款 4×8-pin 转接线带 5090 已稳定使用一年。仍按 §2.4 测温，因为这次是不同的 PSU 和不同的线。
  <!-- 已注释 v1.5：转接线改为每个头独占一根线
  - 每根 PSU 线最多带 2 个头。High Power 只有 4 个 PCIe 插座，所以 GPU1 用两根线、每根 2 个头（400W 时每根约 200W），GPU1 因此上限 450W。Super Flower 有单头线的话优先用单头线（[X26]），它的 PCIe 线是 16AWG（[X23]）。
  -->
- PSU 的 CPU / EPS 插座**绝不**接 PCIe 线，反之亦然。
- 16-pin 端插到底，3cm 内不弯折；转接线和 8-pin 线不承受拉力，并固定在矿架上。
- 测温见 §2.4 第 8 条。

---

## 3. 实施步骤

### 第 1 步：装机前验证（$0）

1. **Z690 准备**（此时只接 PSU-H，不接 GPU 和 switch 卡）：
   1. **更新 BIOS**
      - 从 ASUS 官网 ROG STRIX **Z690-A** GAMING WIFI D4 的支持页下载最新**正式版** BIOS，不用 beta 版；**（已完成：BIOS 已是最新）**
      - 刷写方式：BIOS 里的 EZ Flash 3（FAT32 U 盘），或用 BIOS FlashBack（文件先用官网的 BIOS Renamer 改名）；
      - 刷写过程中不断电、不按任何键；
      - 刷完进 BIOS，执行 Load Optimized Defaults。
   2. **内存训练**
      - 装上 4×32GB，先用默认（JEDEC）开机。首次训练 128GB 可能自动重启几次、黑屏几分钟，属正常，**不要中途断电**；
      - **已完成（2026-10-28）**：4×32GB 全部识别，JEDEC DDR4-2666 CL19，MemTest86+ 0 错误；
      - **决定 XMP 保持关闭**：4 根双 rank 32GB 在 JEDEC 下最稳，本机瓶颈在 PCIe 和 GPU，不在内存频率；
      <!-- 已注释 v1.7：已决定不开 XMP
      - 默认设置下能稳定进 BIOS 后，再开 XMP；
      -->
      - MemTest86 至少 1 轮，建议跑满 4 轮。进系统后可再跑 1 小时 `stressapptest -s 3600 -M 100000`；
      - 以后若 BIOS 更新或改动内存设置，重跑一轮 MemTest86+。
      <!-- 已注释 v1.7：XMP 不再使用
      - XMP 下测试不过 → 退回 JEDEC，或降一档频率重测。
      -->
   3. **BIOS 设置**：按第 4 步的设置表设置（含 Secure Boot 关闭），然后用 ASUS 的 Save Profile 存一份到 U 盘。以后更新 BIOS 会清空设置，用它一键恢复。
   4. **安装 Ubuntu Server 24.04 LTS**
      - 系统盘装在 **M.2_1**（12 代 CPU 单独的 PCIe 4.0 x4；手册未列出与 PCIEX16(G5) 共享通道，[X32]）；
      <!-- 已注释 v1.7 补充：系统盘保留在 M.2_1
      - 系统盘装在芯片组的 **M.2_2、M.2_3 或 M.2_4**（[X32]），**M.2_1 留空**，留给第 3 步的 A/B 测试；
      -->
      <!-- 已注释 v1.7：规格引用改为 Z690 手册
      - 系统盘装在芯片组的 M.2 槽（以 [N10] 规格页为准），**M.2_1 留空**，留给第 3 步的 A/B 测试；
      -->
      - 安装选项：最小化安装；勾选 OpenSSH server；**不勾选 "Search for third-party drivers"**，避免装进发行版的 nvidia 驱动；不选装额外的 snap；
      - 装完立刻做一次 `sudo apt update && sudo apt full-upgrade`，然后安装编译依赖 `build-essential` 和 `linux-headers-$(uname -r)`，再按第 4 步执行版本冻结。冻结之后不再随意升级；
      - 设置固定 IP（或在路由器上做 DHCP 保留）、主机名、`ufw`。

<!-- 已注释 v1.3：原第 1 点，被上方 Z790 准备流程替代
1. Z790：装 4×32GB，开 XMP，MemTest86 跑 1 轮；装 Ubuntu Server LTS 最小化。
-->
2. 在 X870E 上用临时 SSD 启动 Ubuntu。现有 2×5090 是 CPU 直连 x8/x8，在这台上装 aikitoria 驱动，跑 `p2pBandwidthLatencyTest` 和 vLLM TP2。
   - P2P 不通 → 先解决驱动或 BIOS，再进行第 3 步装机。
3. 在 Z690 上做一次**内存模拟测试**（装机前没有 4 张卡，跑不了 TP4 的 r10）：
   - 用 `vmtouch -l`（或一个 mlock 小程序）锁住 48GB，模拟 PLE 表；
   - 同时把 135GB 的 checkpoint 完整读一遍（`cat 文件 > /dev/null` 或 `vmtouch -t`），观察 `free -m` 和 `vmstat 1`；
   - 通过标准：不触发 OOM，系统仍能响应；
   - **真实的 r10 内存峰值**放到 G3 之后、G4 之前测（`/usr/bin/time -v` 看 maxrss，同时用 `free -m` 采样）。

<!-- 已注释 v1.2：装机前没有 4 张卡，无法加载 TP4 的 r10
3. 在 Z790 上单独测一次 r10 模型加载时的内存峰值（`/usr/bin/time -v` 看 maxrss，同时用 `free -m` 采样），不要等到 G4 才发现 OOM。
-->

<!-- 已注释 v1.1：原第 1 步第 2 点的采购门槛，硬件已到货
   - P2P 不通 → 先解决驱动或 BIOS，**暂不采购**。
-->

<!-- 已注释 v1.1：硬件已到货
### 第 2 步：采购

按 §1 下单，拿到卖家对 5 条确认项的书面答复。
-->

### 第 2 步：到货验收

按 §1.1 执行，不通过就退货，不进入下一步。

### 第 3 步：装机

- switch 卡只能插 **PCIEX16(G5)**。第二个 x16 长槽来自 Z690 芯片组，只有 **PCIe 3.0 x4**（或 x4/x4），**不能插 switch 卡**（[X32]）。
- **M.2_1**：系统盘就装在这里。按 Z690-A D4 手册，它走 12 代 CPU 单独的 PCIe 4.0 x4，手册未列出与 PCIEX16(G5) 共享通道（[X32]）。不做空槽 A/B，改为在 §1.1 到货验收时直接确认：
  1. switch 上行端口的 LnkCap **和** LnkSta 宽度都是 **x16**（宽度空载时也不应降）；
  2. 只有上行宽度异常（如 x8）时，才把系统盘挪到 M.2_2 / M.2_3 / M.2_4 复测，以排除通道共享。
  <!-- 已注释 v1.7 补充：原 A/B 写法（需要 M.2_1 空槽）
  - **M.2_1**：按 Z690-A D4 手册，它走 12 代 CPU 单独的 PCIe 4.0 x4，手册未列出与 PCIEX16(G5) 共享通道（[X32]）。为保险仍做一次 A/B：
  1. 首次部署时 M.2_1 空着，记录上行 LnkSta baseline；
  2. 再插 SSD 复测，上行仍是 16GT/s x16 就可以正常使用。
  -->
  <!-- 已注释 v1.7：原说明基于 Z790-A D4 规格和零售商页面
  - **M.2_1**：ASUS 官方规格显示它走 CPU 独立的 PCIe 4.0 x4，理论上不占用 PCIEX16_1 的 x16（[N10]），但有零售商页面写的是"占用后 x16 降为 x8"。处理方式：
  -->
- **接线**（套装专属）：
  - switch 卡 DIP：FS1-1 = ON（X16），其余 OFF；
  - 每张 GPU 用同一对**同字母**的口，**X1 → 转接板 ②，X2 → 转接板 ①**（实测，反接只有 x8）；不能跨字母混接（如 A1 + B2 接同一块转接板）；E1/E2 空着；
  <!-- 已注释 v1.8：线序已实测确定
  - 每张 GPU 用同一对口：GPU0 = A1/A2，GPU1 = B1/B2，GPU2 = C1/C2，GPU3 = D1/D2，分别接转接板 ① / ②；E1/E2 空着；
  -->
  - 线通用、两头相同；同一张 GPU 的两根线保持同一批、同长度；
  - 某张卡只到 x8 或不识别时，先对调这张卡的 ① ② 两根线复测；
  - 转接板 6-pin（GPU1）接这张卡 12V-2x6 所在的同一台 PSU（§2）；左侧白色 4-pin 是风扇口，可接风扇给转接板附近散热。
  <!-- 已注释 v1.2 补充：卖家已答复
  - 只用套装自带的交叉线，不混用其他线；
  - 转接板 6-pin（GPU1）接这张卡 12V-2x6 所在的同一台 PSU（§2）；左侧白色 4-pin 不接。
  -->
- 转接板按卡厚固定，8i 线不要硬折，switch 卡要有气流吹过。
- 按 §2 接电，接好同步线；首次上电按 §2.4 的流程执行，再按 G1 的方法冷启动。
  <!-- 已注释 v1.3：首次上电改按 §2.4
  - 按 §2 接电，接好同步线，再按 G1 的方法冷启动。
  -->

<!-- 已注释 v1.1：原 M.2 说明，被上方 A/B 流程替代
- switch 卡只插 PCIEX16_1。和它共享通道的 M.2 槽不插，以 Z790-A D4 规格页为准（[N10]）。
-->

### 第 4 步：BIOS 与系统

```text
BIOS（Z690）：Above 4G = On，Resizable BAR = Off（见下方"4 卡 BAR"），CSM = Off，VT-d = On，
             PCIEX16_1 = Auto（训练不稳时强制 Gen4），ASPM = Disabled，
             Secure Boot = 关闭（Boot → Secure Boot → OS Type = Other OS；补丁驱动模块未签名，[M03]）
```

<!-- 已注释 v1.8：原 BIOS 行，4 卡时 ReBAR = On 会卡在 VGA
BIOS（Z690）：Above 4G = On，Resizable BAR = On，CSM = Off，VT-d = On，
-->

<!-- 已注释 v1.3：原 BIOS 表缺 Secure Boot
```text
BIOS（Z790）：Above 4G = On，Resizable BAR = On，CSM = Off，VT-d = On，
             PCIEX16_1 = Auto（训练不稳时强制 Gen4），ASPM = Disabled
```
-->

**常见菜单位置**（ASUS 12 代主板的常见位置，以实际界面为准；手册 [X32] 没有逐项列出）：

| 设置 | 常见位置 | 值 |
|---|---|---|
| Above 4G Decoding | Advanced → PCI Subsystem Settings | Enabled |
| Re-Size BAR Support | Advanced → PCI Subsystem Settings（打开 Above 4G 后出现） | **Disabled**（4 卡时开着会卡在 VGA 灯；BAR 由 Linux 放大，见下方） |
| VT-d | Advanced → System Agent (SA) Configuration | Enabled |
| CSM | Boot → CSM → Launch CSM | Disabled |
| Secure Boot | Boot → Secure Boot → OS Type | Other OS |
| ASPM | Advanced → Platform Misc Configuration（或 PCH / SA 下的 PCI Express 设置） | Disabled |
| PCIEX16(G5) 速率 | Advanced → PCI Subsystem Settings 或 SA Configuration | Auto（训练不稳时改 Gen4） |
| XMP | Ai Tweaker | Disabled（保持 DDR4-2666） |

<!-- 已注释 v1.8：原 ReBAR 一行
| Re-Size BAR Support | Advanced → PCI Subsystem Settings（打开 Above 4G 后出现） | Enabled |
-->

- 从 Ubuntu 直接重启进 BIOS：`sudo systemctl reboot --firmware-setup`。

设完后在 **Tool → ASUS User Profile** 保存一份，并另存到 U 盘；以后更新 BIOS 会清空设置，用它恢复。

**MMIO / BAR**：4 张卡的 BAR1 各 32GiB，每个下游端口还要再放一个 32MiB 的 BAR，而 BAR1 必须按 32GiB 对齐。所以 switch 上行桥的 64-bit prefetchable 窗口**至少 128GiB，按对齐实际约需 192–256GiB**。

- 12700K 的物理地址是 46 位（[X21]），地址空间不是瓶颈，关键在 BIOS 有没有预留这么大的窗口。
- 检查：`sudo lspci -vv -s <上行端口BDF> | grep -i 'Prefetchable memory behind bridge'`。

**4 卡 BAR：实测结论与方案（2026-10-29/30，已部署）**

- **现象**：1–2 张卡正常；接 3 张或 4 张时，开机停在 Q-LED **VGA**（白灯），进不了系统。
- **原因**：
  - BIOS 给 64-bit PCIe 设备只留了 **256GiB**（`0x40_0000_0000`–`0x7F_FFFF_FFFF`），核显先占掉开头约 4GiB（含它的 SR-IOV VF）。
  - 每张 5090 有 BAR1 32G 和 BAR3 32M。BAR1 按 32G 对齐，多出的 32M 会挤占下一个 32G 位置；Linux 6.x 按每卡 48G 计算，4 卡需要一块连续的 **192GiB**。BIOS 分不出来，就卡在 VGA。
  - 同样是 PEX88096 + ASUS Z790，有人报告了同样的 POST 卡死和窗口不足（[X34]）。
  - 关掉 ReBAR 后每张卡只要 256MiB，BIOS 能过 POST。但 BIOS 又把 USB、声卡、VMD（系统盘在它下面）等芯片组设备放在了窗口中部（`0x60_74…`），两边各剩约 127GiB，**仍然放不下 192GiB**，所以单靠 `pci=realloc` 不够。
- **方案**：
  1. BIOS：Re-Size BAR = **Off**，Above 4G 保持 On；
  2. 内核参数加 `pci=nocrs`：Linux 不再局限于 BIOS 声明的窗口，可以用 CPU 的 46 位地址空间。实测 192GiB 窗口被放在 `0x64_0000_0000`–`0x93_FFFF_FFFF`，跨出了 BIOS 窗口（[X34] 在同平台也验证过 512GiB 以上的地址可用）；
  3. 开机服务 `gpu-rebar.service`：在加载 nvidia 驱动**之前**，把每张卡的 ReBAR 控制寄存器改成 32G，移除 switch 所在的 root port（PCIEX16(G5) = `0000:00:01.0`）再重新扫描，让 6.8 内核重新分配，最后加载驱动；
  4. `/etc/modprobe.d/nvidia-defer.conf` 禁止 nvidia 驱动开机自动加载，改由上面的服务加载。
- **结果**：4/4 张卡 BAR1 = 32GiB，都是 Gen4 x16，P2P 全通（§4.1）。远程重启验证过：默认启动项开机后全自动完成。
- 这个方法和 [X33] 里 resize-amdgpu-bars 工具的做法相同：改 ReBAR 控制寄存器，再从 root port 重新扫描。用 sysfs 的 `resource1_resize` 不行，因为 switch 后面的父桥窗口不会被释放。

`/usr/local/sbin/gpu-rebar.sh`（权限 755）：

```bash
#!/bin/bash
# Grow RTX 5090 BAR1 to 32G and re-enumerate the PEX88096 tree, then load nvidia.
# BIOS Re-Size BAR stays off (4 x 32G BARs hang POST); needs pci=nocrs so the
# 192G bridge window can go above the BIOS 64-bit window.
set -u
ROOT_PORT=0000:00:01.0
GPU_ID=10de:2b85
BAR1_SIZE=$((32 << 30))

gpus() { lspci -D -d "$GPU_ID" | cut -d" " -f1; }
bar1() { sed -n 2p "/sys/bus/pci/devices/$1/resource"; }

need=0
for d in $(gpus); do
	ctrl=0x$(setpci -s "$d" ECAP15+8.l) || continue
	if [ $(( (ctrl >> 8) & 0x3f )) -ne 15 ]; then
		setpci -s "$d" COMMAND=0000:0002
		setpci -s "$d" ECAP15+8.l=$(printf %08x $(( (ctrl & ~0x3f00) | (15 << 8) )))
		need=1
	fi
	read -r s _ <<<"$(bar1 "$d")"
	[ $((s)) -eq 0 ] && need=1
done

if [ $need -eq 1 ]; then
	echo 1 > "/sys/bus/pci/devices/$ROOT_PORT/remove"
	sleep 2
	echo 1 > /sys/bus/pci/rescan
	sleep 3
fi

n=0; ok=0
for d in $(gpus); do
	n=$((n + 1))
	read -r s e _ <<<"$(bar1 "$d")"
	[ $((s)) -ne 0 ] && [ $((e - s + 1)) -eq $BAR1_SIZE ] && ok=$((ok + 1))
done
echo "gpu-rebar: $ok/$n GPUs have a 32G BAR1"

modprobe -a nvidia nvidia_uvm nvidia_modeset nvidia_drm
[ $ok -eq $n ] && [ $n -gt 0 ]
```

```ini
# /etc/systemd/system/gpu-rebar.service
[Unit]
Description=Resize GPU BAR1 to 32G, re-enumerate PCIe switch, load nvidia
After=systemd-udev-settle.service systemd-modules-load.service local-fs.target
Before=nvidia-persistenced.service nvidia-powerd.service multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/sbin/gpu-rebar.sh

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/modprobe.d/nvidia-defer.conf
# Loaded by gpu-rebar.service after BAR1 is resized; do not autoload.
blacklist nvidia
blacklist nvidia_drm
blacklist nvidia_modeset
blacklist nvidia_uvm
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable gpu-rebar.service
# /etc/default/grub：GRUB_CMDLINE_LINUX_DEFAULT 末尾加 pci=nocrs（即下表 profile 3），然后 update-grub

# 验证
systemctl status gpu-rebar --no-pager                          # active (exited)
journalctl -u gpu-rebar -b | grep gpu-rebar:                   # gpu-rebar: 4/4 GPUs have a 32G BAR1
nvidia-smi -q -d MEMORY | grep -A2 "BAR1" | grep Total         # 4 行 32768 MiB
sudo lspci -vv -s 00:01.0 | grep "Prefetchable memory behind"  # 约 192G
```

- **回退**：原启动参数备份在 `/etc/default/grub.bak-before-nocrs`。GRUB 菜单显示 10 秒，保留两个调试启动项："Ubuntu (debug: no nvidia, verbose)" 和 "Ubuntu (test: pci=nocrs, no nvidia)"；`GRUB_DEFAULT=saved`，可以用 `sudo grub-reboot "<菜单名>"` 只在下一次开机时选某一项。
- **注意**：
  - BIOS 更新会恢复默认设置，ReBAR 可能被重新打开。更新后先确认 ReBAR = Off，再接 4 张卡开机。
  - 内核不要升级到 7.x（见下方"版本冻结"）。
  - 换口、加减卡都不用改脚本：它按 device ID `10de:2b85` 找卡。换 GPU 型号时改 `GPU_ID`；switch 改插别的槽时改 `ROOT_PORT`。
  - 驱动参数 `NVreg_EnableResizableBar=1` 保留无害：驱动加载时 BAR1 已经是 32G。

<!-- 已注释 v1.2：窗口估算未考虑 32GiB 对齐
**MMIO / BAR**：4 张卡的 BAR1 各 32GiB，switch 上行桥需要 128GiB 以上的 64-bit prefetchable 窗口。
-->

- 原来的首选"让 BIOS 在 POST 阶段就预留足够大的窗口"在本机行不通：4 卡时 POST 直接卡住。改用上面的方案。
<!-- 已注释 v1.8：原首选方案
- **首选**：让 BIOS（Above 4G + ReBAR）在 POST 阶段就预留足够大的窗口，这是最可靠的方案。
-->
- `pci=realloc` 能修复一部分 BIOS 窗口分配不足的问题（[R12]），但不保证所有 switch / ReBAR 拓扑都能修好：GPU 在 switch 后面时，Linux 可能拒绝重新分配上行桥的资源（[R11]）。

**启动参数分 3 个 profile**，每次只改一个变量（`XXXX` 填 §1.1 实测的 device ID）：

| Profile | GRUB_CMDLINE_LINUX_DEFAULT | 适用情况 |
|---|---|---|
| **0（默认）** | `intel_iommu=on iommu=pt pcie_aspm=off pci=disable_acs_redir=pci:1000:XXXX` | 先跑 G1/G2 |
| **1** | 同上，但改为 `pci=disable_acs_redir=pci:1000:XXXX,realloc` | 出现 `BAR … no space` / `failed to assign` |
| **2** | 同上，但改为 `pci=disable_acs_redir=pci:1000:XXXX,realloc=off` | BIOS 已分配好，但 Linux 重分配后出现 BAR0 = 0M 或 probe 失败（[R13]） |
| **3（当前使用）** | `intel_iommu=on iommu=pt pcie_aspm=off pci=disable_acs_redir=pci:1000:c010,realloc=off pci=nocrs`，配合 BIOS ReBAR = Off 和 `gpu-rebar.service` | 4 卡时 BIOS 分不出 4×32G（见上方"4 卡 BAR"） |

```bash
sudo nano /etc/default/grub     # 修改 GRUB_CMDLINE_LINUX_DEFAULT
sudo update-grub && sudo reboot
cat /proc/cmdline               # 确认生效
```

- 本机实测：profile 0 下 switch 和 5090 的 SR-IOV VF BAR 分不到地址，内核自动 realloc 会释放 BIOS 已分配的窗口，结果 BAR0 = 0M、驱动探测失败；改 profile 2 后正常。4 卡阶段再加 `pci=nocrs`，即 profile 3。

profile 0–2 都失败时，按以下顺序升级，**每次只加一项**：
1. `pci=hpmmioprefsize=...`：只对 hotplug bridge 生效，不保证对本拓扑有效；
2. `pci=resource_alignment=...`：针对具体 bridge；
3. 回退到 X870E（§5）。

**ASPM**：BIOS 设为 Disabled 负责关闭；`pcie_aspm=off` 的作用是"Linux 不改动 firmware 的 ASPM 配置"，两者配合使用。

**IOMMU**：passthrough 模式下 P2P 不通时，可改为 `intel_iommu=off`（[M03]）。

**ACS**：用内核参数 `pci=disable_acs_redir`（[K01], [K02]）。它在枚举设备、创建 IOMMU group 之前生效，关闭 P2P Request Redirect、P2P Completion Redirect 和 P2P Egress Control 三个位，没有和 nvidia 驱动加载抢时序的问题。

- 验证时要检查 PEX 的**所有** bridge function：
  ```bash
  sudo lspci -vvv -d 1000:XXXX | grep -E '^[0-9a-f]|ACSCap|ACSCtl'
  # 每个 function 的 ACSCtl 里，ReqRedir- CmpltRedir- EgressCtrl- 都应为 '-'
  ```
- vendor:device 匹配漏掉了某个 function 时，改用 BDF 或 path 指定，多个设备用 `;` 分隔（GRUB 里整串加引号）。
- 代价：IOMMU group 会合并，设备隔离变弱。专用推理机可以接受。
- 需要保留部分 ACS 功能时，可改用 `config_acs` 逐位控制（[K03]）。现阶段不需要。

<!-- 已注释 v1.1：ACS 改用 pci=disable_acs_redir 内核参数。原 systemd 方案存在时序问题：nvidia 模块可能在 udev 阶段就加载，早于 multi-user.target，同时 vendor ID 匹配可能误关其他 Broadcom 桥

**ACS**：只关 switch 桥上的 ACS，并做成开机自动执行（[M03]）：

```bash
#!/usr/bin/env bash
# /usr/local/sbin/pex-acs-off.sh
# 先用 lspci -nn 确认 switch 的 vendor ID：Broadcom 为 1000，旧 PLX 为 10b5
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

验证：`sudo lspci -vvv | grep -i ACSCtl`，switch 桥上各项应全部显示为 `-`。
-->

<!-- 已注释 v1.1：原内核参数，被上方 3 个 profile 替代
内核参数：    intel_iommu=on iommu=pt
             （passthrough 下 P2P 不通时可改为 intel_iommu=off，[M03]）
-->

**驱动**：aikitoria open-gpu-kernel-modules **610.57.04**（[X01]）。

- **打开驱动侧 ReBAR。** Blackwell 即使 BIOS 开了 ReBAR 也要显式设置（[X19]）；16×5060 Ti 实建配方里也有这一项（[M03]）：
  ```bash
  echo 'options nvidia NVreg_EnableResizableBar=1' | sudo tee /etc/modprobe.d/nvidia-rebar.conf
  sudo update-initramfs -u
  ```
  设置后**整机断电**再开机。
- 确认 BAR1 = **32GiB**（覆盖全部显存）：`nvidia-smi -q -d MEMORY | grep -A3 BAR1`。
  - 仍是 256MiB：说明上游桥窗口不够，驱动没法扩大 BAR（[X20]）。实测驱动在 switch 后面放大 BAR 会失败（日志 `bridge window … can't assign`），所以本机由 `gpu-rebar.service` 在加载驱动之前放大，见上方"4 卡 BAR"。
  <!-- 已注释 v1.8：原处理方法
  - 仍是 256MiB：说明上游桥窗口不够，驱动没法扩大 BAR（[X20]）。按上面的 profile 1 / 2 和升级顺序处理。
  -->

**功率上限**：**用户决定（2026-10-29）默认不设上限**，4 张卡按出厂 600W 运行，以 §2.4 满载测试结果为准（§2）。下面的服务**目前没有安装**，只在某台 PSU 撑不住时才用。`nvidia-smi -pl` 重启后就失效，所以做成 systemd 服务；启用时在 `[Unit]` 里加 `After=gpu-rebar.service`，因为驱动由那个服务加载。

<!-- 已注释 v1.8：原说明，目标 400W
**功率上限（开机自动设置）**：`nvidia-smi -pl` 重启后就失效，所以做成 systemd 服务。目标 400W；任何时候不超过 500W（§2）。
-->

```ini
# /etc/systemd/system/gpu-power-limit.service
[Unit]
Description=Set GPU persistence mode and power limit
After=systemd-modules-load.service

[Service]
Type=oneshot
ExecStart=/usr/bin/nvidia-smi -pm 1
ExecStart=/usr/bin/nvidia-smi -pl 400

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now gpu-power-limit.service
nvidia-smi --query-gpu=index,power.limit --format=csv   # 4 张卡都应显示 400.00 W
```

- 默认 4 张卡统一 400W。需要提高时按卡设置（`-i` 指定卡号；卡号以 `nvidia-smi -L` 对应到 GPU0–GPU3 为准）：
  ```ini
  ExecStart=/usr/bin/nvidia-smi -i 0 -pl 500   # GPU0：High Power 原生
  ExecStart=/usr/bin/nvidia-smi -i 1 -pl 500   # GPU1：转接线，每个头独占一根线
  ExecStart=/usr/bin/nvidia-smi -i 2 -pl 500   # GPU2：Corsair 原生
  ExecStart=/usr/bin/nvidia-smi -i 3 -pl 400   # GPU3：Super Flower 无 ATX 3.x 余量；G6 通过后最多 450
  ```
  每次提高后都重新执行 §2.4 第 6–8 条的电压和温度检查。
  <!-- 已注释 v1.5：原代码块中 GPU1 为 450、GPU3 固定 400
  ExecStart=/usr/bin/nvidia-smi -i 1 -pl 450   # GPU1：转接线，每根线 2 个头
  ExecStart=/usr/bin/nvidia-smi -i 3 -pl 400   # GPU3：转接线 + Super Flower，固定 400W
  -->
  <!-- 已注释 v1.4：改为按卡上限
  - 提到 500W 时只改 `-pl` 这一个数值，并重新执行 §2.4 第 6–8 条的电压和温度检查。
  -->

**版本冻结**：把这台机当 appliance 管理。

```bash
# 只 hold 实际安装的那一支内核元包（GA 或 HWE），先用 dpkg -l 'linux-*generic*' 确认
sudo apt-mark hold linux-generic linux-image-generic linux-headers-generic
# 如果装的是 HWE 分支，hold 的是这三个：
# sudo apt-mark hold linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 linux-headers-generic-hwe-24.04
sudo apt-mark hold linux-image-$(uname -r) linux-headers-$(uname -r) linux-modules-$(uname -r)
apt-mark showhold
```

- **内核不要升级到 7.x。** Linux 7.0–7.3 在本机这种拓扑下（同一个父桥下有多个"32G + 32M"的子窗口）会把桥窗口算小，4 张卡只有 1 张分到 BAR1（回归提交 3958bf16e2fe 和 f909e3ee3ed1，[X33]、[X34]）；6.8–6.19 正常。本机当前是 6.8.0-147，已 hold。上游的修复系列（Ilpo Järvinen，2026-10-02 发出）合入主线并在本机验证之前，不升 7.x。

<!-- 已注释 v1.2：补丁驱动不是 dpkg 包，列表为空时 apt-mark 会报错
sudo apt-mark hold $(dpkg -l | awk '/^ii/ && /nvidia/ {print $2}')
-->

**禁止 apt 装进发行版 nvidia 驱动。** aikitoria 驱动是从源码编译安装的，dpkg 里通常没有对应的包，hold 也就无从谈起。真正的风险是 apt **新装**发行版驱动，把补丁驱动覆盖掉：

```bash
sudo tee /etc/apt/preferences.d/no-distro-nvidia > /dev/null <<'PIN'
Package: /^nvidia-(driver|dkms|kernel-common|kernel-source|utils|compute-utils|headless)-/ /^libnvidia-(compute|gl|extra|decode|encode|fbc1|cfg1|common)-/ /^xserver-xorg-video-nvidia-/
Pin: version *
Pin-Priority: -1
PIN
apt-cache policy nvidia-driver-570   # 应显示 Candidate: (none)
```

- 这条规则**不会**挡住 `nvidia-container-toolkit` / `libnvidia-container*`：用 Docker 跑 r10 时需要它们。

- CUDA 只装 `cuda-toolkit-X-Y`，**不装 `cuda` 元包**：它会依赖 `nvidia-driver-*`。
- 不运行 `ubuntu-drivers autoinstall`。

- 只 hold 具体版本号的内核包不够：元包还在的话，会把新内核作为依赖装进来（[R14]）。
- unattended-upgrades：专用推理机建议直接停用（`sudo apt remove unattended-upgrades`），按下面的升级流程手动升级。
  - 必须保留时，在 `/etc/apt/apt.conf.d/50unattended-upgrades` 的 `Package-Blacklist` 里加入 `linux-generic`、`linux-image-generic`、`linux-headers-generic`、`linux-modules-*`、`nvidia-*`（[R15]）。
- 记录已知可用的版本组合：kernel、aikitoria commit、NVIDIA userspace、CUDA、vLLM / r10 overlay。
- 升级流程：快照 / 备份启动环境 → 装新内核 → 重编补丁模块 → 跑 G1 → G4 → 全部通过才设为默认启动项。

<!-- 已注释 v1.1：原驱动锁定说明，被上方"版本冻结"替代
**驱动**：aikitoria open-gpu-kernel-modules **610.57.04**（[X01]），装好后 `apt-mark hold` 住 nvidia 相关包，防止升级把补丁覆盖掉。
-->

### 第 5 步：推理栈

- 使用 **QWEN-PEDIA r10 配方**（Qwen3.8-Flash-Next 部署配方的第 10 版）及其固定的 vLLM 版本（[N03]）。
  - 上游 vLLM 在超过 2 张 PCIe GPU 时会禁用 custom all-reduce（[X02]），所以不要用上游版本跑分去和基线比。
- 环境变量：

```bash
export VLLM_SKIP_P2P_CHECK=0          # 首次部署让 vLLM 做功能性 P2P 检查（[N08]）
export VLLM_CUSTOM_AR_ALLOW_PCIE=1    # r10 overlay 专用；P2P 验证通过后再开
# 不设置 NCCL_P2P_LEVEL；必须约束时用 PIX，不要用 SYS（[N06]）
```

- **128GB 内存余量很小**（r10 标称 125GB，其中 48GB PLE 表常驻内存）：
  - 系统不装桌面；
  - 建 32GB swapfile，只用来扛模型加载时的峰值。注意：被 mlock 的 PLE 表不会进 swap，swap 只能接其余部分的峰值；
  - r10 配置里的 CPU 侧 KV 缓冲能关就关；
  - mlock 不限额：容器加 `--ulimit memlock=-1:-1`，裸机改 `limits.conf`。
- 服务监听 LAN 地址，用 `ufw` 只放行 X870E；客户端改连 Z690 主机的 IP。

---

## 4. 验收 Gate（前一级不过，不进下一级）

| Gate | 方法 | 通过标准 |
|---|---|---|
| **G1 链路** | ① `lspci -vv` 看 **LnkCap 和 LnkSta**，LnkSta **在负载下看**（同时跑 `p2pBandwidthLatencyTest` 或 `nvbandwidth`）；② `dmesg \| grep -iE "no space\|failed to assign\|bridge window\|NVRM.*BAR"`；③ `nvidia-smi -q -d PCIE`、`dmesg \| grep -i aer` | ① 上行和 4 条下行的 LnkCap 都是 16GT/s x16；负载下 LnkSta 也是 16GT/s x16；空载时宽度仍是 x16、速率降到 2.5GT/s 属正常（[X18]）；② 无 BAR 分配失败，4 张卡 BAR1 都是 32GiB；③ 1h 内 AER 不增长；**连续冷启动 10 次，每次 4 张卡都识别** |
| **G2 P2P** | `nvidia-smi topo -m`、`p2pBandwidthLatencyTest` 或 `nvbandwidth`、ACSCtl 检查 | 所有卡对为 PIX 或 PXB（本卡是两级 switch，§4.1），不能出现 PHB / NODE / SYS；单向 ≥ 24 GB/s，双向 ≥ 45 GB/s（社区实测 25–28 / 约 52，[M03], [M04], [M05]）；PEX 所有 function 的 ReqRedir / CmpltRedir / EgressCtrl 为 `-` |
| **G3 NCCL** | `all_reduce_perf -b 8M -e 1G -f 2 -g 4` | 记录 busbw；1GB 时低于 15 GB/s 视为异常 |
| **G4 应用** | 先测 r10 真实内存峰值（§3 第 1 步第 3 点）；再跑 r10，TP4 + EP，固定 prompt 和功率上限 | ≥ r10 基线的 90%：≥ 95 steps/s，decode ≥ 290 tok/s，prefill ≥ 7,000 tok/s；内存峰值无 OOM，`vmstat` 的 si/so 接近 0 |
| **G5 A/B** | `NCCL_P2P_DISABLE=1` + 关掉 custom AR，重跑 G4 | 记录 P2P 带来的 pp / tg 差值 |
| **G6 稳定性** | 先完成 §2.4 有人值守的 1 小时满载；再跑 24h 服务压测，`dmesg \| grep -i xid`；记录 PDU 电压 / 电流；红外测温：10-30 墙插、adapter 两端、L6-30 接头、PDU 输入线、各 12V-2x6 | 无 Xid、无掉卡；PDU 持续电流 ≤ 24A（30A × 80%）；负载下电压降 ≤ 约 2%；各接头温升满足 §2.4 第 8 条 |

<!-- 已注释 v1.8：原 G2 行开头
| **G2 P2P** | `nvidia-smi topo -m`、`p2pBandwidthLatencyTest`、ACSCtl 检查 | 所有卡对为 PIX；
-->

<!-- 已注释 v1.3：原 G6 行，按 115V 双回路判定
| **G6 稳定性** | 24h 服务压测，`dmesg \| grep -i xid`，红外测温 12V-2x6 接头，**墙端功率计 / 钳形表** | 无 Xid、无掉卡、接头温度正常；每条回路实测持续电流 ≤ 断路器额定值的 80% |
-->

<!-- 已注释 v1.2：原 G1 行，LnkSta 未区分空载 / 负载
| **G1 链路** | ① `lspci -vv` 看 **LnkCap 和 LnkSta**；② `dmesg \| grep -iE "no space\|failed to assign\|bridge window\|NVRM.*BAR"`；③ `nvidia-smi -q -d PCIE`、`dmesg \| grep -i aer` | ① 上行和 4 条下行的 LnkCap、LnkSta 都是 16GT/s x16；② 无 BAR 分配失败，4 张卡 BAR1 都是 32GiB；③ 1h 内 AER 不增长；**连续冷启动 10 次，每次 4 张卡都识别** |
-->

**G1 的 LnkCap / LnkSta 判定：**

| LnkCap | LnkSta | 判断 |
|---|---|---|
| Gen4 x16 | Gen4 x16 | 通过 |
| Gen4 x16 | 空载时速率 2.5GT/s、宽度 x16 | 正常省电，加负载复查 |
| Gen4 x16 | **负载下**速率偏低，或任何时候宽度低于 x16 | 线材 / 训练 / 主板问题，按 §5 排查 |
| 偏低（如 Gen1 x4） | 偏低 | switch 卡配置问题（根因有争议，[X17]），退货 |

<!-- 已注释 v1.2：原行未区分空载 / 负载
| Gen4 x16 | 偏低（Gen1–3 或 x8 以下） | 线材 / 训练 / 主板问题，按 §5 排查 |
-->

<!-- 已注释 v1.1：原 G1 行，被上方两层判定替代
| **G1 链路** | `lspci -vv`（LnkSta）、`nvidia-smi -q -d PCIE`、`dmesg \| grep -i aer` | 上行和 4 条下行都是 16GT/s x16；1h 内 AER 不增长；**连续冷启动 10 次，每次 4 张卡都识别** |
-->

出现以下任一情况，**先查硬件链路，不要调 vLLM**：单向只有 10–15 GB/s、某张卡明显偏低、拓扑出现 PHB / NODE / SYS（走了 CPU）、链路掉到 Gen3/Gen2。

<!-- 已注释 v1.8：PXB 在本卡上属正常
出现以下任一情况，**先查硬件链路，不要调 vLLM**：单向只有 10–15 GB/s、某张卡明显偏低、拓扑不是 PIX、链路掉到 Gen3/Gen2。
-->

### 4.1 实测记录（2026-10-28 – 10-30）

| 项目 | 结果 | 判定 |
|---|---|---|
| switch | `1000:c010`；上行 LnkCap / LnkSta Gen4 x16；卡内两级结构 | ✅ |
| 单卡（A 口） | Gen4 x16，BAR1 32GiB，AER 0；H2D 23.66 / D2H 28.43 GB/s | ✅ |
| 双卡 P2P | 单向 28.2 GB/s（CE）/ 26.7（SM）；双向 56.5 / 45.2 | ✅ G2 |
| 4 卡识别 | 4 张都是 Gen4 x16，BAR1 都是 32GiB（ReBAR Off + `gpu-rebar.service`）；`topo -p2p r` 全部 OK | ✅ |
| 4 卡 P2P（拷贝引擎，12 对） | 单向每对 28.57 GB/s（合计 342.9）；双向每对 56.5 GB/s（合计 677.7）；各对之间差异为 0 | ✅ G2 |
| 拓扑 | 同一个下级 switch 下的那一对卡显示 PIX，其余卡对显示 PXB | 正常 |
| 错误 | Xid / AER / DMAR 都是 0 | ✅ |
| 版本 | kernel 6.8.0-147（hold）；aikitoria 610.57.04-p2p-v3（commit 461d638b7a91f73702001e343ec91b275a43ec35）；CUDA 13.3 | — |

- `nvidia-smi` 的卡号（0–3）按 PCI 地址排序，和 §2 按电源命名的 GPU0–GPU3 不一定一致。设按卡功率上限前，用 `nvidia-smi --query-gpu=index,pci.bus_id --format=csv` 对照 `lspci -tv` 找到每张卡接在哪个口。
- 其他实测：switch 接上后 PCI 总线号整体后移，板载网卡名从 `enp4s0` 变成了 `enp22s0`，导致开机断网；netplan 已改为按 MAC 地址匹配（`match: macaddress`），以后加减设备不受影响。
- **还没做**：G1 的"负载下 LnkSta"和"冷启动 10 次"；§2.4 的 4 卡满载 1 小时（需要有人在场）；E 口、转接板 5、线 9/10 单独测试；G3–G6。

**手动复测 P2P**：

```bash
nvidia-smi topo -m                 # 拓扑：PIX / PXB 为正常
nvidia-smi topo -p2p r             # 每对都应是 OK
cd ~/nvidia/nvbandwidth/build
./nvbandwidth -t device_to_device_memcpy_read_ce device_to_device_bidirectional_memcpy_read_ce
# 单向每对约 28.5 GB/s，双向约 56.5 GB/s；跑完看 sudo dmesg | grep -iE "xid|aer"
```

---

## 5. 故障处理与回退

| 现象 | 处理 |
|---|---|
| LnkCap 本身偏低 | switch 配置问题，退货（§1.1） |
| 空载 LnkSta 显示 2.5GT/s | 正常省电，加负载复查（[X18]） |
| BAR1 只有 256MiB | 本机由 `gpu-rebar.service` 放大 BAR：`systemctl status gpu-rebar`、`journalctl -u gpu-rebar -b`；确认 cmdline 有 `pci=nocrs`（§3 第 4 步"4 卡 BAR"） |
| 3 张以上卡开机卡在 Q-LED **VGA**（白灯） | BIOS 的 64-bit 窗口只有 256GiB。确认 BIOS Re-Size BAR = **Off**（BIOS 更新后会恢复默认，要重新确认）。先退回单卡进 BIOS 改设置 |
| `gpu-rebar: x/4 GPUs have a 32G BAR1`（x < 4），或 `nvidia-smi` 少卡 | `sudo dmesg \| grep -E "can't assign\|failed to assign"`；确认 cmdline 有 `pci=nocrs`、BIOS ReBAR = Off、内核不是 7.x；仍不行用 GRUB 调试项（不加载 nvidia）开机，手动执行 `sudo /usr/local/sbin/gpu-rebar.sh` 看输出 |
| `BAR … no space` / `failed to assign`，或 `NVRM: Fatal Error while attempting to resize PCIe BARs`（[X16]） | 检查 BIOS 的 Above 4G / ReBAR → Profile 1 → Profile 2 → §3 第 4 步里的升级顺序。注：[X16] 是基于 595 驱动的讨论，610.57.04 是否包含相关改动需要另行确认 |
| 冷启动少卡 | 整机全部 PSU 断电，等 10 秒，同步重新上电。别指望 `pci rescan`。总是同一张卡缺失时，交换 PSU / 线 / 转接板，看问题跟着哪个部件走 |
| 链路掉到 Gen2 / Gen3，或 AER 持续增长 | 换短线，确认线和转接板与卡同一卖家（[R03]）；BIOS 强制 Gen4；仍不行再加 retimer |
| 运行中 `Xid 79`（掉卡） | 先查那台 PSU 是否触发了过流 / 过功率保护，再查 12V-2x6 接头 |
| 整机无故断电或重启 | 先怀疑 PSU-H Super Flower：它是主控，又没有 ATX 3.x 瞬时余量。给 GPU3 设上限（400–450W）复测；可临时拔掉 GPU3 复测；仍断电再查同步板和 240V 链路 |
| 某张卡 Max Power Limit 只有约 450W | 转接线只接了 3 个 8-pin，或有一个没插到底（§2.6） |
| 从电源不跟随启动 / 少卡 | 先按 §2.5 单独测试同步板（带指示灯的 BQZYX+ 能直接看出哪路没起来）；换备件后再测 |
| Z690 识别不到 switch 下的设备，或 BAR 怎么都分不到 | 把 switch 卡、线、转接板整体搬到 X870E 的 PCIEX16_1（M.2_2/3 不插）。AM5 + 88096 有成功案例（[M04]） |
| G4 内存不够（OOM / 持续 swap） | 同上，搬到 X870E；插满 4×48GB DDR5，两套时序不同，要手动取两套中较松的时序，从 5200 起步并跑 MemTest（调法见完整版附录 C） |
| P2P 始终起不来 | 先确认 ACSCtl 和 IOMMU 设置（§3 第 4 步）；仍不行就临时改用 TP2×PP2 或 TP2×DP2，同时回到完整版重新评估平台 |
| 30A 断路器跳闸 / PDU 电流接近 24A | 降低功率上限（`nvidia-smi -pl`）；确认这条回路上没有接其他负载（§2.1） |
| 负载下 PDU 电压比空载下降超过约 2% | 链路上某处接触电阻偏大：降负载，按 §2.4 第 8 条测温找发热点 |
| 任一接头焦味、变色、温升超过判据 | 软件降负载 / 停服务 → 关闭 PSU → 关闭 PDU 总开关 → 再拔插头（§2.4 第 10 条）；停用该 adapter 或墙插，联系房东或电工 |

<!-- 已注释 v1.8：§5 原两行
| BAR1 只有 256MiB | 确认 `NVreg_EnableResizableBar=1` 已写入 initramfs，并整机断电重启；仍不行就是上游桥窗口不够（[X20]），按 profile 1 / 2 处理 |
| 整机无故断电或重启 | 先怀疑 PSU-H Super Flower：它是主控，又没有 ATX 3.x 瞬时余量。把 GPU3 降回 400W；可临时拔掉 GPU3 复测；仍断电再查同步板和 240V 链路 |
-->

<!-- 已注释 v1.6：§5 原"从电源不跟随"一行
| 从电源不跟随启动 / 少卡 | 先按 §2.5 单独测试同步板；换板后再测 |
-->

<!-- 已注释 v1.5：§5 原"整机无故断电"一行
| 整机无故断电或重启 | 先怀疑 PSU-H Super Flower：它是主控，又没有 ATX 3.x 瞬时余量。确认 GPU3 固定 400W；可临时拔掉 GPU3 复测；仍断电再查同步板和 240V 链路 |
-->

<!-- 已注释 v1.3：§5 原"断路器跳闸"一行，按 115V 双回路处理
| 断路器跳闸 / 回路电流超过 80% | 降低功率上限（`nvidia-smi -pl`），或重新分配回路（§2） |
-->

---

## 参考

| ID | 来源 |
|---|---|
| [N03] | QWEN-PEDIA Qwen3.8-Flash-Next r10 配方 |
| [N06] | NVIDIA NCCL 环境变量文档 |
| [N08] | vLLM P2P 检查 RFC |
| [K01] | Linux kernel-parameters 文档（disable_acs_redir / realloc / hpmmioprefsize / pcie_aspm） |
| [K02] | LKML：PCI: Introduce the disable_acs_redir parameter |
| [K03] | Ubuntu kernel SRU：PCI: Extend ACS configurability（config_acs） |
| [X01] | aikitoria P2P 驱动 README |
| [X02] | vLLM custom all-reduce 文档 |
| [X05] | PCIe CEM T_PVPERL（Linux 补丁说明） |
| [X06] | Level1Techs：双 PSU 倒灌烧卡 |
| [X09] | c-payne SlimSAS x16 设备转接板 |
| [X10] | SFF-8654 x16 转接板（6-pin 输入） |
| [X11] | Level1Techs：PLX88096 5 槽版（40.6mm 槽距） |
| [X12] | c-payne PM40084（Intel 消费级平台不兼容） |
| [X14] | r/LocalLLM Frankenserver |
| [M03] | r/LocalLLaMA 16×5060 Ti 双 88096 岛 |
| [M04] | r/LocalLLaMA 双 88096 岛（AM5 host） |
| [M05] | r/LocalLLaMA AM5 7-GPU switch 实测 |
| [M09] | AliExpress PEX88096 10×SFF-8654 switch 卡 |
| [M47] | 12V-2x6 熔毁警示 |
| [R03] | r/LocalLLM 4×3090 链路训练翻车 |
| [R11] | Red Hat RHEL-3672：switch 后的 GPU 无法 resize BAR |
| [R12] | Red Hat：多 GPU BAR no space，pci=realloc 解决 |
| [R13] | Graid：多 GPU + PLX/PEX 下 pci=realloc=off |
| [R14] | tecadmin：内核元包导致 hold 失效 |
| [R15] | HowtoForge：unattended-upgrades 内核 blacklist |
| [R16] | NEC 125% 持续负载规则 |
| [X16] | NVIDIA open-gpu-kernel-modules PR #1109（BAR resize 失败导致 GPU 不绑定；v1.1 编号为 `N11`） |
| [X17] | Level1Techs：杂牌 PEX88048 只报 Gen1 x4（根因有争议；v1.1 编号为 `R10`） |
| [X18] | NVIDIA 论坛：GPU 空闲时 PCIe 链路降速属正常 |
| [X19] | Arch Wiki 镜像：NVreg_EnableResizableBar（Blackwell 需显式开启） |
| [X20] | NVIDIA open-gpu-kernel-modules PR #3：上游桥窗口不够时无法扩大 BAR |
| [X21] | openbenchmarking：i7-12700K cpuinfo（46 位物理地址） |
| [X22] | Kingwin：High Power 1300W 规格（8 个 PCIe 6+2 头、ATX 3.0 瞬时余量） |
| [X23] | TechPowerUp：Super Flower SF-1000F14MP 评测（PCIe / EPS 线 16AWG） |
| [X24] | PPE.pl（引 ComputerBase）：RTX 5090 接 3 个 8-pin 可运行、2 个无法开机 |
| [X25] | Legit Reviews：Add2PSU 继电器同步板评测 |
| [X26] | TweakTown：Super Flower Leadex Platinum 1000 评测（PCIe 线含单头线） |
| [X27] | Amazon B077VQL5NT：BAY Direct 2-Pack Add2PSU（Molex 取电，4.5★ / 213 条评价，30 天退换；2026-10-24 查看时有货，$17.99） |
| [X28] | Amazon B08F9WGLP2：Thsion 同步板 2 块装（SATA 取电，4.5★ / 160 条，30 天退换；$15.98） |
| [X29] | Amazon B09Q11WG4Z：BQZYX+ ADD2PSU 4 合 1，带电压 / PS-ON 指示灯（4.4★ / 52 条，30 天退换；$22.99） |
| [X30] | Walmart：24-pin 同步线商品页（含"使用几小时后线发烫"的买家报告） |
| [X31] | ASUS ROG STRIX Z690-A GAMING WIFI D4 官方规格页 |
| [X32] | 《ROG STRIX Z690-A GAMING WIFI D4 User's Manual（Simplified Chinese Edition）》，本地文件，与本文件同目录：扩展槽、M.2 插槽、BIOS FlashBack |
| [X33] | linux-pci 邮件列表，2026-09 至 10："PCI: bridge window undersized when child bridge windows are larger than their alignment (regression since 3958bf16e2fe, v7.0)"。含 2×RTX 3090（32G + 32M）同类案例；6.8–6.17 正常、7.0 回归；Ilpo Järvinen 的修复系列 2026-10-02 发出 |
| [X34] | linux-pci 邮件列表，Matt Protacio，2026-10-25："[REGRESSION] PCI: sibling bridge windows undersized after rescan since f909e3ee3ed1"。PEX88096 + ASUS Z790 + 4×V100（32G + 32M）：BIOS 窗口太小且零碎，GPU 开机通电会卡 POST；6.17 下重新扫描得到 192G 窗口，v7.0–7.3 失败。正文由用户提供，链接为列表归档首页 |

<!-- 已注释 v1.7：主板型号更正，原 Z790 规格引用
| [N10] | ASUS Z790-A D4 规格 |
[N10]: https://rog.asus.com/us/motherboards/rog-strix/rog-strix-z790-a-gaming-wifi-d4-model/spec/
-->

<!-- 已注释 v1.2：参考编号去冲突。完整版 v3.9 的 [N11] 是 Ovi's Tech Blog，[R10a]/[R10b] 已占用 R10，因此改为 X 前缀
| [N11] | NVIDIA open-gpu-kernel-modules PR #1109（BAR resize 失败导致 GPU 不绑定） |
| [R10] | Level1Techs：杂牌 PEX88048 EEPROM 配成 Gen1 x4 |
-->

[N03]: https://github.com/abtraore/QWEN-PEDIA/blob/main/recipes/qwen3.8-flash-next/README.md
[N06]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
[N08]: https://github.com/vllm-project/vllm/issues/51513
[K01]: https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html
[K02]: https://lkml.iu.edu/hypermail/linux/kernel/1807.2/02169.html
[K03]: https://lists.snapcraft.io/archives/kernel-team/2025-May/159555.html
[X01]: https://raw.githubusercontent.com/aikitoria/open-gpu-kernel-modules/461d638b7a91f73702001e343ec91b275a43ec35/README.md
[X02]: https://docs.vllm.ai/en/v0.23.0/api/vllm/distributed/device_communicators/custom_all_reduce/
[X05]: https://lists.infradead.org/pipermail/linux-arm-kernel/2023-July/850966.html
[X06]: https://forum.level1techs.com/t/dual-psu-safety-on-romed8-2t-with-4x-3090/246583
[X09]: https://c-payne.com/products/slimsas-pcie-gen4-device-adapter-x8-x16
[X10]: https://ubbcentral.com/store/item/SlimSAS-8i-x2-to-PCIe4-0-x16-Slot-Adapter-SFF8654-Riser-Card-GEN4-for-Network_374904846028.html
[X11]: https://forum.level1techs.com/t/a-neverending-story-pcie-3-0-4-0-5-0-6-0-sci-fi-bifurcation-adapters-switches-hbas-cables-nvme-backplanes-risers-extensions-the-good-the-bad-the-ugly-will-there-be-a-final-solution/171428/950
[X12]: https://c-payne.com/products/pcie-gen4-switch-4x-x16-microchip-switchtec-pm40084
[X14]: https://reddit.com/r/LocalLLM/comments/1wy1o7y/frankenserver_its_alive_its_alive/
[M03]: https://reddit.com/r/LocalLLaMA/comments/1vthcwk/the_boring_way_to_run_deepseek_v4_flash0731/
[M04]: https://www.reddit.com/r/LocalLLaMA/comments/1wpczeb/dailychained_plx_88096_switches_quad_rtx_5070_ti/
[M05]: https://reddit.com/r/LocalLLaMA/comments/1qeimyi/7_gpus_at_x16_50_and_40_on_am5_with_gen54/
[M09]: https://www.aliexpress.us/item/3256812710866317.html
[M47]: https://reddit.com/r/pcmasterrace/comments/1u85htp/my_turn_today_boys_caught_it_before_it_turned/
[R03]: https://reddit.com/r/LocalLLM/comments/1wb7vxs/we_dont_judge_frankenstein_4x3090_testing_complete/
[R11]: https://issues.redhat.com/browse/RHEL-3672
[R12]: https://access.redhat.com/node/7052830
[R13]: https://support.graidtech.com/portal/en/kb/articles/supremeraid-not-detected-after-pre-installer-on-multi-gpu-systems-bar0-is-0m-pci-i-o-region-invalid
[R14]: https://tecadmin.net/?p=12224
[R15]: https://www.howtoforge.com/how-to-block-package-and-kernel-updates-in-debian-ubuntu/
[R16]: https://muhammed.portlandiaelectric.supply/blogs/news/how-to-size-circuit-breaker
[X16]: https://github.com/NVIDIA/open-gpu-kernel-modules/pull/1109
[X17]: https://forum.level1techs.com/t/generic-pex88048-cards-may-ship-with-misconfigured-eeprom-gen1-x4-upstream/251129
[X18]: https://forums.developer.nvidia.com/t/gpu-downgraded-to-x8-lanes/195427
[X19]: https://histre.com/@Drewlius/
[X20]: https://github.com/NVIDIA/open-gpu-kernel-modules/pull/3
[X21]: https://openbenchmarking.org/system/2410307-NE-12700K5G634/Intel%20Core%20i7-12700K/cpuinfo
[X22]: https://www.kingwin.com/high-power-modular-power-supply-1300w/
[X23]: https://www.techpowerup.com/review/super-flower-sf-1000f14mp/2.html
[X24]: https://www.ppe.pl/news/362747/nvidia-geforce-rtx-5090-traci-5-wydajnosci-przy-korzystaniu-z-3x-8-pinowej-przejsciowki-zasilajacej.html
[X25]: https://www.legitreviews.com/?p=1698
[X26]: https://www.tweaktown.com/reviews/5741/super-flower-leadex-platinum-1000-80-plus-platinum-psu-review/index.html
[X27]: https://www.amazon.com/dp/B077VQL5NT
[X28]: https://www.amazon.com/dp/B08F9WGLP2
[X29]: https://www.amazon.com/dp/B09Q11WG4Z
[X30]: https://www.walmart.com/ip/24-Pin-Power-Synchronization-Line-Extension-Cable-Efficient-for-Computer-Video-Card-Connection/18077019786
[X31]: https://rog.asus.com/motherboards/rog-strix/rog-strix-z690-a-gaming-wifi-d4-model/spec/
[X32]: ROG%20STRIX%20Z690-A%20GAMING%20WIFI%20D4%20User%E2%80%99s%20Manual%20(%20Simplified%20Chinese%20Edition%20).pdf
[X33]: https://lore-kernel.gnuweeb.org/linux-pci/e0619af8-c100-8b4a-86bb-f7252cf540b1%40linux.intel.com/T/
[X34]: https://marc.info/?l=linux-pci

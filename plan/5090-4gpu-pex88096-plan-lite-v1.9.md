# 4×RTX 5090 + PEX88096 实施计划（精简版）v1.9

- 版本：**lite v1.9**（2026-10-30，2026-10-31、2026-11-01 补充）
- 上一版：lite v1.8（2026-10-30）
- 依据：[5090-multi-gpu-plan-v3.9.md](5090-multi-gpu-plan-v3.9.md)（2026-10-06）。论证、备选平台、8 卡扩展和完整来源都在完整版里，本文只保留 4 卡 88096 的执行方案。
- 约定：被替换或已不适用的内容没有删除，用 `<!-- 已注释 vX.X：原因 -->` 注释掉保留。

## 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.9 | 2026-10-30 | **r10 部署上线，写入实测**：r10 原基础镜像已从 Docker Hub 下架，改为 v0.29.0 镜像 + eed1f3d0 wheel + r10 overlay 重建（§3 第 5 步）；新增 Docker / NVIDIA container toolkit / swap 的安装步骤；启动参数加 `--max-num-seqs 8`，上下文改为 YaRN 2 倍（524,288）；新增 `gpu-memoc.service`（持久模式 + 显存 offset，NVML +4000）；修复重启后 BAR 退回 256MiB 的问题（`nvidia-cdi-refresh` 抢先加载驱动），给 `gpu-rebar.sh` 加卸载保护；Docker 排在 `gpu-rebar` 之后；新增 §4.2 r10 实测（基线对比、超频、并发、YaRN、PC1 Strata 对比）和 §5 对应故障项；ufw 按决定保持关闭；新增 [X35]–[X37]。**补充（2026-10-31）**：**更正**此前的“YaRN 2 倍”：r10 的顶层 `rope_parameters` 覆盖从未生效，实际跑的是原生 RoPE；改为 `text_config` 嵌套写法并打补丁让草稿模型同步，A/B 后保留（§3 第 5 步、§4.2）；autotune 缓存命中时启动卡死，改用 tmpfs；新增核心超频实测，+300 MHz 时 GPU0 报 Xid 109，决定不超频（§4.2、§5）。**补充（2026-11-01）**：内存改为 **XMP DDR4-3600**（用户决定，未做压力测试），步速变化不到 1%（§0、§3 第 1 步、§4.2）；新增 r10 按温度和思考模式的速度与接受率（§4.2）；新增 §4.3 Basalt 实测（2 卡 vs r10，按上下文、温度、并发对比，未切换）和双实例候选方案；新增 §4.4 采样温度（开思考时建议 0.6，服务器默认仍是 1.0）；客户端新增温度和监控面板 `pc2speed` 说明（§3 第 5 步）；§5 新增两行；新增 [X38]–[X45] |
| v1.8 | 2026-10-30 | **4 卡跑通，写入实测**：3 张以上卡开机卡在 Q-LED VGA，原因是 BIOS 的 64-bit 窗口只有 256GiB；改为 BIOS Re-Size BAR = Off + 内核参数 `pci=nocrs` + 开机服务 `gpu-rebar.service`（加载驱动前把 BAR1 放大到 32G 并重新扫描 switch），写入 §3 第 4 步"4 卡 BAR"和启动 profile 3；switch 实测 ID `1000:c010`，卡内两级结构（topo 多为 PXB）；线序定为 X1 → 转接板 ②、X2 → 转接板 ①；新增 §4.1 实测记录（4 卡 P2P 单向 28.6 / 双向 56.5 GB/s）；功率上限改为默认不设（以 §2.4 满载测试为准），§2.4 分阶段加负载随之调整；版本冻结新增"不升级到 7.x 内核"（[X33]、[X34]）；§5 新增 VGA 卡住和 gpu-rebar 排查两行 |
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
| 推理服务器 | ROG STRIX **Z690-A** GAMING WIFI D4（BIOS 4601）+ i7-12700K + 4×32GB DDR4（G.Skill F4-3600C18，同一套装，128GB；**2026-10-31 起开 XMP，DDR4-3600**，未做压力测试），**纯 Ubuntu Server** |
| 日常机（PC1） | X870E + 9950X3D + MSI 1600W + 2×5090，继续跑 Win10，不改动，不接 240V PDU，**不在本文范围**（触发回退方案时会被停用） |
| GPU fabric | PEX88096 **分体 kit**：switch 卡插在 Z690 的 PCIEX16(G5)（CPU 直连）；每张 GPU 用 2 根 SFF-8654 8i 线接一块带 12V 输入的 x16 转接板 |
| 链路 | 上行 1×Gen4 x16，下行 4×Gen4 x16，4 张卡在同一块 switch 卡内。卡内是两级 switch：`topo -m` 里同一下级 switch 的卡对显示 PIX，其余显示 **PXB**，P2P 带宽不受影响（§4.1） |
| 软件 | aikitoria P2P 驱动 610.57.04 + QWEN-PEDIA r10 配方（vLLM overlay，TP4 + EP，NVFP4）；基础镜像已下架，按 §3 第 5 步重建；服务地址 `http://192.168.1.OBFUSCATED:8036/v1` |
| 备选引擎 | Basalt（2 卡）单流更快、并发和超长上下文更弱，**未切换**；候选是 GPU 0,1 和 2,3 各跑一个 Basalt，测试通过才考虑（§4.3） |
| 供电 | **3 台 PSU**：Super Flower 1000W（主控，带主机 + GPU3）、High Power 1300W（GPU0 + GPU1）、Corsair SF1000（GPU2）。**每张卡的转接板 12V 和 GPU 供电来自同一台 PSU**，全部同步上电；GPU1、GPU3 用英伟达原装 4×8-pin 转接线（§2.6）；**单条 240V/30A dryer 回路**：NEMA 10-30R → 成品 10-30P→L6-30R adapter → L6-30P 输入的 240V PDU（§2.1）；**功率上限默认不设（出厂 600W），以 §2.4 满载测试为准**（§2） |
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
   - `LnkCap` 本身就是 Gen1 x4 一类 → EEPROM 配置错误，手上没有工具可修，**直接退货**。
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
- **功率上限默认不设**（决定，2026-10-29）：4 张卡按出厂 600W 运行。不设上限时的持续负载估算：
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
      <!-- 已注释 v1.9（2026-11-01）：已改为开 XMP
      - **决定 XMP 保持关闭**：4 根双 rank 32GB 在 JEDEC 下最稳，本机瓶颈在 PCIe 和 GPU，不在内存频率；
      -->
      - **2026-10-31 改为开 XMP（DDR4-3600）**，用户决定保留。实测步速变化不到 1%，8 路约 +1.3%（§4.2）。**3600 还没做过内存压力测试**，要做的话停 r10 后跑 `memtester` 或 `stressapptest`，需要有人在场；
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
| XMP | Ai Tweaker | **开（DDR4-3600）**（2026-10-31 起；CMOS 清空或 BIOS 更新后要重新打开） |

<!-- 已注释 v1.9（2026-11-01）：原 XMP 一行
| XMP | Ai Tweaker | Disabled（保持 DDR4-2666） |
-->

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
- **v1.9 补充**：装 nvidia-container-toolkit 后，第一次重启变成 `gpu-rebar: 0/4`。它带的 `nvidia-cdi-refresh.service` 和 `gpu-rebar` 同时启动，在重新扫描之前就把驱动加载了；扫描时驱动接管了显卡，ReBAR 控制寄存器退回 256MiB（`0x821`）。修复：下方脚本开头先卸载已加载的驱动，并用 drop-in 让 `nvidia-cdi-refresh` 排在 `gpu-rebar` 之后。修复后重启验证通过：14.5 秒 4/4 → 14.6 秒加载驱动 → 18.9 秒 cdi-refresh → 19.1 秒 `gpu-memoc` → 20.7 秒 Docker。**以后新装任何会调用 NVIDIA 库的开机服务，都要检查它是否排在 `gpu-rebar` 之后。**
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

# If something loaded nvidia first (e.g. nvidia-cdi-refresh.service from
# nvidia-container-toolkit), it binds the GPUs during rescan and resets
# ReBAR to 256M. Unload it before touching the BARs.
if grep -q "^nvidia " /proc/modules; then
	echo "gpu-rebar: nvidia already loaded, unloading first"
	modprobe -r nvidia_drm nvidia_modeset nvidia_uvm nvidia ||
		echo "gpu-rebar: unload failed (GPU in use?)"
fi

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

```ini
# /etc/systemd/system/nvidia-cdi-refresh.service.d/after-gpu-rebar.conf（v1.9 新增）
[Unit]
# Loading nvidia before gpu-rebar re-enumerates the switch resets BAR1 to 256M
After=gpu-rebar.service
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

**功率上限**：**决定（2026-10-29）默认不设上限**，4 张卡按出厂 600W 运行，以 §2.4 满载测试结果为准（§2）。下面的服务**目前没有安装**，只在某台 PSU 撑不住时才用。`nvidia-smi -pl` 重启后就失效，所以做成 systemd 服务；启用时在 `[Unit]` 里加 `After=gpu-rebar.service`，因为驱动由那个服务加载。

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

**显存超频（v1.9，决定保留）**：`gpu-memoc.service` 开机时打开持久模式，并给 4 张卡设显存 offset。排在 `gpu-rebar` 之后、Docker 之前。

- **单位**：NVML 的 offset 是 Afterburner / `nvidia-smi` 显示频率的 **2 倍**。NVML +4000 = 显示频率 +2000，最高频率从 14001 变成 16001 MHz。NVML 允许范围是 -2000 到 +6000。
- **收益很小**：8 路并发约 +2.5%，已接近误差范围；+5000 / +6000 没有继续提高（§4.2）。r10 不受显存带宽限制。GeForce 的显存没有 ECC，超频出错可能不崩溃而是悄悄算错，所以这个值还要经过 §2.4 的 1 小时满载验证。
- **持久模式必须开**：否则没有程序占用 GPU 时，驱动可能释放状态，offset 随之丢失。

NVML 库单独装在 `/opt/gpu-oc`，不依赖用户目录：

```bash
sudo python3 -m venv /opt/gpu-oc && sudo /opt/gpu-oc/bin/pip -q install nvidia-ml-py
```

`/usr/local/sbin/gpu-memoc.py`（权限 755）：

```python
#!/opt/gpu-oc/bin/python
# Apply the RTX 5090 memory VF offset on every GPU and verify it took.
# NVML units are 2x the Afterburner / nvidia-smi clock: 4000 = +2000 MHz (14001 -> 16001 max).
# Chosen 2026-10-30: +2.5% aggregate decode on r10 (8x concurrent); +5000/+6000 gave no more.
import sys
from pynvml import *
OFFSET = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
nvmlInit()
bad = 0
for i in range(nvmlDeviceGetCount()):
    h = nvmlDeviceGetHandleByIndex(i)
    nvmlDeviceSetMemClkVfOffset(h, OFFSET)
    got = nvmlDeviceGetMemClkVfOffset(h)
    print(f"gpu-memoc: GPU{i} mem offset {got}, max mem clock {nvmlDeviceGetMaxClockInfo(h, NVML_CLOCK_MEM)} MHz")
    bad += got != OFFSET
sys.exit(1 if bad else 0)
```

```ini
# /etc/systemd/system/gpu-memoc.service
[Unit]
Description=RTX 5090 persistence mode + memory clock offset
After=gpu-rebar.service
Requires=gpu-rebar.service
Before=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
# Persistence mode keeps the offset when no process holds the GPUs.
ExecStart=/usr/bin/nvidia-smi -pm 1
ExecStart=/usr/local/sbin/gpu-memoc.py 4000
# Stopping the unit restores stock memory clocks.
ExecStop=/usr/local/sbin/gpu-memoc.py 0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now gpu-memoc.service
journalctl -u gpu-memoc -b | grep gpu-memoc:    # 4 行 mem offset 4000, max mem clock 16001 MHz
sudo systemctl stop gpu-memoc                   # 临时恢复默认频率
sudo systemctl disable --now gpu-memoc          # 永久取消
```

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

- 这条规则**不会**挡住 `nvidia-container-toolkit` / `libnvidia-container*`：用 Docker 跑 r10 时需要它们。这个工具包带 `nvidia-cdi-refresh` 开机服务，必须排在 `gpu-rebar` 之后（见上方"4 卡 BAR"）。

- CUDA 只装 `cuda-toolkit-X-Y`，**不装 `cuda` 元包**：它会依赖 `nvidia-driver-*`。
- 不运行 `ubuntu-drivers autoinstall`。

- 只 hold 具体版本号的内核包不够：元包还在的话，会把新内核作为依赖装进来（[R14]）。
- unattended-upgrades：专用推理机建议直接停用（`sudo apt remove unattended-upgrades`），按下面的升级流程手动升级。
  - 必须保留时，在 `/etc/apt/apt.conf.d/50unattended-upgrades` 的 `Package-Blacklist` 里加入 `linux-generic`、`linux-image-generic`、`linux-headers-generic`、`linux-modules-*`、`nvidia-*`（[R15]）。
- 记录已知可用的版本组合：kernel、aikitoria commit、NVIDIA userspace、CUDA、vLLM / r10 overlay。
  - **当前（2026-10-30）**：kernel 6.8.0-147；aikitoria 610.57.04-p2p-v3（commit 461d638b7a91）；CUDA 13.3；Docker 29.1.3；NVIDIA Container Toolkit 1.20.1；镜像 `qwen-pedia/fnext-vllm:r10`（`5b2088524a80`）；QWEN-PEDIA commit ed7901322730 + `launch.sh` 两处本地改动；模型 snapshot fc694b54fb01。
- 升级流程：快照 / 备份启动环境 → 装新内核 → 重编补丁模块 → 跑 G1 → G4 → 全部通过才设为默认启动项。

<!-- 已注释 v1.1：原驱动锁定说明，被上方"版本冻结"替代
**驱动**：aikitoria open-gpu-kernel-modules **610.57.04**（[X01]），装好后 `apt-mark hold` 住 nvidia 相关包，防止升级把补丁覆盖掉。
-->

### 第 5 步：推理栈

- 使用 **QWEN-PEDIA r10 配方**（Qwen3.8-Flash-Next 部署配方的第 10 版）及其固定的 vLLM 版本（[N03]）。
  - 上游 vLLM 在超过 2 张 PCIe GPU 时会禁用 custom all-reduce（[X02]），所以不要用上游版本跑分去和基线比。
- 环境变量：全部由 `launch.sh` 设置（含 `VLLM_CUSTOM_AR_ALLOW_PCIE=1`）。不要另外设置 `NCCL_P2P_LEVEL`；必须约束时用 PIX，不要用 SYS（[N06]）。启动日志应有 `Custom allreduce kept ENABLED on 4 PCIe-only GPUs`。日志里的 `Unknown vLLM environment variable` 警告可以忽略：这些变量是 overlay 读的，vLLM 原版不认识。

<!-- 已注释 v1.9：launch.sh 已包含所需环境变量，实际部署没有手动 export
- 环境变量：

```bash
export VLLM_SKIP_P2P_CHECK=0          # 首次部署让 vLLM 做功能性 P2P 检查（[N08]）
export VLLM_CUSTOM_AR_ALLOW_PCIE=1    # r10 overlay 专用；P2P 验证通过后再开
# 不设置 NCCL_P2P_LEVEL；必须约束时用 PIX，不要用 SYS（[N06]）
```
-->

- **128GB 内存余量很小**（r10 标称 125GB，其中 48GB PLE 表常驻内存）：
  - 系统不装桌面；
  - 建 32GB swapfile，只用来扛模型加载时的峰值。注意：被 mlock 的 PLE 表不会进 swap，swap 只能接其余部分的峰值；
  - r10 配置里的 CPU 侧 KV 缓冲能关就关；
  - mlock 不限额：容器加 `--ulimit memlock=-1:-1`，裸机改 `limits.conf`。
- **网络**：决定 ufw 保持关闭，服务也没有设 API 密钥，所以局域网内任何设备都能调用。以后要加密钥：在 `launch.sh` 加 `--api-key`，重建容器，客户端填同一个值。

<!-- 已注释 v1.9：决定 ufw 保持关闭
- 服务监听 LAN 地址，用 `ufw` 只放行 X870E；客户端改连 Z690 主机的 IP。
-->

**部署步骤（已执行，2026-10-30）**

1. **Docker 和 NVIDIA container toolkit**（[X37]）：

   ```bash
   sudo apt-get install -y docker.io curl gpg
   curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed "s#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g" | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   sudo usermod -aG docker USER
   sudo docker run --rm --gpus all ubuntu:24.04 nvidia-smi -L   # 应列出 4 张卡
   ```

   然后让 Docker 排在 `gpu-rebar` 之后，容器才不会在驱动加载前启动（`/etc/systemd/system/docker.service.d/after-gpu-rebar.conf`）：

   ```ini
   [Unit]
   # vLLM container (restart=unless-stopped) needs nvidia loaded with 32G BARs first
   After=gpu-rebar.service
   Wants=gpu-rebar.service
   ```

   `nvidia-cdi-refresh` 的 drop-in 见第 4 步"4 卡 BAR"，两个都要有。

2. **swap**：系统原有 8GB，再加 32GB：

   ```bash
   sudo fallocate -l 32G /swapfile32 && sudo chmod 600 /swapfile32
   sudo mkswap /swapfile32 && sudo swapon /swapfile32
   echo "/swapfile32 none swap sw 0 0" | sudo tee -a /etc/fstab
   ```

3. **模型**（约 124GB，snapshot `fc694b54fb0174e0913e6adf86691ef85a4ead47`）：

   ```bash
   python3 -m venv ~/hfenv && ~/hfenv/bin/pip install -U "huggingface_hub[hf_transfer]"
   HF_HUB_ENABLE_HF_TRANSFER=1 ~/hfenv/bin/hf download nvidia/Qwen3.8-Flash-Next-NVFP4
   ```

4. **重建镜像**：r10 的基础镜像 `vllm/vllm-openai:nightly-eed1f3d0…` 和 `cu129-nightly-eed1f3d0…` 已从 Docker Hub 下架，registry 接口直接返回 404（第三方 registry 浏览器的缓存里还能看到，但拉不下来）。这个 commit 的 wheel 还在（[X35]），所以用 v0.29.0 正式版镜像作底（2026-09-09，比 eed1f3d0 早 3 天，torch 同为 2.13.0+cu130）。flashinfer 的三个包版本必须一致，否则 import 时报错，不要用 `FLASHINFER_DISABLE_VERSION_CHECK=1` 跳过；PyPI 上没有 cubin 的 post1，要从 GitHub Release 下载（[X36]）。

   ```bash
   git clone https://github.com/abtraore/QWEN-PEDIA ~/QWEN-PEDIA      # commit ed7901322730
   mkdir -p ~/r10-rebuilt && cd ~/r10-rebuilt
   cp -r ~/QWEN-PEDIA/recipes/qwen3.8-flash-next/image .
   curl -fLO "https://wheels.vllm.ai/eed1f3d0c6043bd494424a22443ee198dd56f657/vllm-0.1.1.dev50%2Bgeed1f3d0c-cp38-abi3-manylinux_2_28_x86_64.whl"
   # 把文件名里的 %2B 改回 +；sha256 1f56ce8036af731f4ffd71b3123e2a9959d166c111f53356977027e6dc303b48
   sudo docker build -t qwen-pedia/fnext-vllm:r10 .
   ```

   `~/r10-rebuilt/Dockerfile`：

   ```dockerfile
   # r10 rebuilt: the original base vllm/vllm-openai:nightly-eed1f3d0... was pruned from Docker Hub.
   # Same vLLM commit (eed1f3d0, per-commit wheel from wheels.vllm.ai) on the v0.29.0 image
   # (torch 2.13.0+cu130 identical), then the unchanged QWEN-PEDIA r10 overlay.
   FROM vllm/vllm-openai:v0.29.0
   ARG FI=https://github.com/flashinfer-ai/flashinfer/releases/download/v0.6.18.post1
   COPY vllm-0.1.1.dev50+geed1f3d0c-cp38-abi3-manylinux_2_28_x86_64.whl /tmp/
   RUN uv pip install --system \
         /tmp/vllm-0.1.1.dev50+geed1f3d0c-cp38-abi3-manylinux_2_28_x86_64.whl \
         flashinfer-python==0.6.18.post1 \
         "$FI/flashinfer_cubin-0.6.18.post1-py3-none-any.whl" \
         "$FI/flashinfer_jit_cache-0.6.18.post1%2Bcu130-cp39-abi3-manylinux_2_28_x86_64.whl" \
    && rm /tmp/*.whl \
    && python3 -c "import vllm, torch, flashinfer; print(vllm.__version__, torch.__version__, flashinfer.__version__)"
   COPY image/vllm/ /usr/local/lib/python3.12/dist-packages/vllm/
   ```

   和原配方的差别：vLLM 代码和 overlay 相同；底层系统库和部分依赖来自 v0.29.0 镜像，cutlass-dsl 由 wheel 的依赖升到 4.7.1。跑分明显低于基线时，先查这里。

5. **启动**：`~/QWEN-PEDIA/recipes/qwen3.8-flash-next/launch.sh` 有下面这些本地改动，另有新增文件 `patches/speculative.py`，`git pull` 时都要保留：

   <!-- 已注释 v1.9（2026-10-31）：原写法只改顶层配置，模型读 text_config，YaRN 没有生效
   ```diff
   -CTX="${CTX:-393216}"          # 262144 = native, no YaRN
   +CTX="${CTX:-524288}"          # YaRN 2x, needle 3/3 at 275K and 483K (2026-10-30); 393216 = r10 default, 262144 = native
      --tensor-parallel-size 4 --enable-expert-parallel --async-scheduling \
   +  --max-num-seqs 8 \
   ```

   - `CTX=524288`：YaRN 2 倍，`launch.sh` 会自动算倍数，并同步草稿模型的长度上限。KV 池 751,128 token，可同时容纳 1.43 个满长度请求。
   -->

   ```diff
   -CTX="${CTX:-393216}"          # 262144 = native, no YaRN
   +CTX="${CTX:-524288}"          # real YaRN 2x on model and drafter (text_config override + patches/speculative.py), A/B 2026-10-31; 262144 = native
    YARN_ARGS=()
   +DRAFT_PATCH=()
   -  YARN_ARGS=(--hf-overrides "{\"rope_parameters\":{\"rope_type\":\"yarn\",\"factor\":$FACTOR,\"original_max_position_embeddings\":262144}}")
   +  YARN_ARGS=(--hf-overrides "{\"text_config\":{\"rope_parameters\":{\"mrope_interleaved\":true,\"mrope_section\":[11,11,10],\"rope_type\":\"yarn\",\"rope_theta\":10000000,\"partial_rotary_factor\":0.25,\"factor\":$FACTOR,\"original_max_position_embeddings\":262144}}}")
   +  DRAFT_PATCH=(-v "$HERE/patches/speculative.py":/usr/local/lib/python3.12/dist-packages/vllm/config/speculative.py:ro)
      -v "$HERE/plans":/plans:ro \
   +  "${DRAFT_PATCH[@]}" \
   +  --tmpfs /root/.cache/vllm/flashinfer_autotune_cache \
      --tensor-parallel-size 4 --enable-expert-parallel --async-scheduling \
   +  --max-num-seqs 8 \
   ```

   `patches/speculative.py` 是从镜像里 `vllm/config/speculative.py` 复制后改的。vLLM 不把字典形式的 `--hf-overrides` 传给草稿模型，这里让 `text_config` 覆盖也传过去：

   ```python
   # 新增到 SpeculativeConfig
   @staticmethod
   def _apply_text_config_override(text_overrides, hf_config):
       hf_config = SpeculativeConfig.hf_config_override(hf_config)
       for key, value in text_overrides.items():
           setattr(hf_config.get_text_config(), key, value)
       return hf_config

   # 加在 compose_draft_hf_overrides 的 `if not callable(...)` 之前
   if isinstance(target_hf_overrides, dict) and "text_config" in target_hf_overrides:
       return functools.partial(
           SpeculativeConfig._apply_text_config_override,
           target_hf_overrides["text_config"],
       )
   ```

   - `CTX=524288`：YaRN 2 倍（模型卡写法，factor 2.0），主模型和草稿模型都生效，同时固定草稿模型的长度上限。KV 池 751,128 token，可同时容纳 1.43 个满长度请求。回退到原生 RoPE：`launch.sh.bak-before-real-yarn`（那份的注释写着 YaRN，实际没有）。
   - 不能用改 `config.json` 的方式开 YaRN：这版 transformers 解析时会报 `'Qwen4ExpConfig' object has no attribute 'max_position_embeddings'`。
   - `--tmpfs`：每次启动清空 autotune 缓存，重新调参只多约 6 秒。缓存命中时启动会卡死（§5）。
   - `--max-num-seqs 8`：CUDA graph 最多覆盖 32 个 token（8 路 × (1 + 3 个投机 token)）。不加这个参数时，16 路并发每路只有约 40 tok/s（§4.2）。

   ```bash
   cd ~/QWEN-PEDIA/recipes/qwen3.8-flash-next
   sudo docker rm -f fnext-vllm
   sudo HOME=$HOME bash ./launch.sh
   curl -s localhost:8036/health -o /dev/null -w "%{http_code}\n"    # 约 4.5 分钟后返回 200
   ```

   容器是 `--restart unless-stopped`：开机自动启动，但**手动 `docker stop` 过的不会自动启动**，要 `docker start fnext-vllm`。

**客户端**（OpenAI 兼容，API 模式选 Chat Completions）：

| 项目 | 值 |
|---|---|
| 端点 | `http://192.168.1.OBFUSCATED:8036/v1` |
| 模型名 | `vllm/qwen3.8-flash-next` |
| 上下文 | `524288` |
| API 密钥 | 无 |
| 温度（v1.9 补充） | 客户端不传时用模型的 `generation_config.json`：temperature 1.0、top_p 0.95、top_k 20。my agent stack 没有设温度，所以大概率是 1.0（推断）。**开思考时建议 0.6**，理由和测试计划见 §4.4；服务器默认值还没改 |
| 历史思考内容（v1.9 补充） | 这版 vLLM 输入只认 `reasoning`，只传 `reasoning_content` 会被静默丢掉（变成空的 `<think>`）。客户端回传历史时至少带 `reasoning`。my agent stack 按配置两个字段都发，没有抓包确认 |

**PC2 屏幕监控**：`/usr/local/bin/pc2dash` 用 tmux 分屏：左边 vLLM 日志，右上 `nvtop`（GPU），右下 `btop`（CPU、内存）。需要 `sudo apt install tmux nvtop btop`。btop 要求至少 80×24，屏幕太小时右下角起不来。

**速度面板（v1.9 补充，2026-11-01）**：`/usr/local/bin/pc2speed` 嵌在 `pc2dash` 左上角，每秒读一次 `/metrics`：

| 行 | 内容 |
|---|---|
| `NOW` / `SINGLE` / `CONCUR` / `PREFILL` | 当前速度；单流、并发、填充的最近值和最高值（`CONCUR` 至少连续 3 秒并发才显示） |
| `ACCEPT` | 接受率（10 秒 / 24 小时 / 启动以来）、3 个草稿位置的接受率、tok/step、steps/s |
| `VRAM` / `KV` | 权重 21.0、KV 5.6、计算图 0.21 GiB/卡来自启动日志（不是实时）；已用和空闲每 5 秒读 `nvidia-smi`；KV 百分比只算正在运行的请求 |
| `RECENT` | 最近 8 个请求的“上下文 / 重算量”。重算超过一半且上下文 ≥ 1 万 token 时标红，表示缓存被挤掉 |
| `24H` | 重算时间 ÷ 请求总时间（vLLM 收到请求到最后一个 token），另列 `misses`、命中率 |

- 和客户端核对：单流 +3%，填充 +1%，8 路 +7–12%（面板只统计 8 路都在跑的时段）。
- 每分钟汇总永久保存在 `~/pc2speed-history/`（按月分文件，只追加，字段说明见同目录 `README.txt`），只有数字，不含对话内容。
- 每秒读一次 `/metrics` 会让 Docker 日志每天多约 13 MB，容器重建前不会轮转。
- 不打补丁就看不到每个会话的 KV 占用（vLLM 没有会话概念），这是用户的选择。

```bash
pc2dash                                # 打开或回到分屏；Ctrl+b 再按 d 退出（程序继续运行）
docker logs -f --tail 100 fnext-vllm   # 只看日志；Ctrl+C 只退出查看，不影响 vLLM
```

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

### 4.1 硬件实测记录（2026-10-28 – 10-30）

| 项目 | 结果 | 判定 |
|---|---|---|
| switch | `1000:c010`；上行 LnkCap / LnkSta Gen4 x16；卡内两级结构 | ✅ |
| 单卡（A 口） | Gen4 x16，BAR1 32GiB，AER 0；H2D 23.66 / D2H 28.43 GB/s | ✅ |
| 双卡 P2P | 单向 28.2 GB/s（CE）/ 26.7（SM）；双向 56.5 / 45.2 | ✅ G2 |
| 4 卡识别 | 4 张都是 Gen4 x16，BAR1 都是 32GiB（ReBAR Off + `gpu-rebar.service`）；`topo -p2p r` 全部 OK | ✅ |
| 4 卡 P2P（拷贝引擎，12 对） | 单向每对 28.57 GB/s（合计 342.9）；双向每对 56.5 GB/s（合计 677.7）；各对之间差异为 0 | ✅ G2 |
| 拓扑 | 同一个下级 switch 下的那一对卡显示 PIX，其余卡对显示 PXB | 正常 |
| 错误 | Xid / AER / DMAR 都是 0 | ✅ |
| 负载下链路（v1.9） | r10 推理时 `nvidia-smi` 的 `pcie.link.gen.current` / `width.current`：4 张卡都是 Gen4 x16 | ✅ G1 这一项 |
| 重启（v1.9） | 热重启 3 次：第 1 次 4/4；装 toolkit 后第 2 次 0/4（§3 第 4 步"4 卡 BAR"的 v1.9 补充）；修复后第 3 次 4/4，且驱动、超频、Docker 顺序正确 | ✅（冷启动未测） |
| 版本 | kernel 6.8.0-147（hold）；aikitoria 610.57.04-p2p-v3（commit 461d638b7a91f73702001e343ec91b275a43ec35）；CUDA 13.3 | — |

- `nvidia-smi` 的卡号（0–3）按 PCI 地址排序，和 §2 按电源命名的 GPU0–GPU3 不一定一致。设按卡功率上限前，用 `nvidia-smi --query-gpu=index,pci.bus_id --format=csv` 对照 `lspci -tv` 找到每张卡接在哪个口。
- 其他实测：switch 接上后 PCI 总线号整体后移，板载网卡名从 `enp4s0` 变成了 `enp22s0`，导致开机断网；netplan 已改为按 MAC 地址匹配（`match: macaddress`），以后加减设备不受影响。
- **还没做**：G1 的"冷启动 10 次"；§2.4 的 4 卡满载 1 小时（需要有人在场，要带着 NVML +4000 跑）；E 口、转接板 5、线 9/10 单独测试；G5、G6；DDR4-3600 的内存压力测试（v1.9 补充）。G3 跳过（最小化测试，直接用 r10 验证）。部署全部结束后撤销免密 sudo：`sudo rm /etc/sudoers.d/90-USER-nopasswd`。

<!-- 已注释 v1.9（2026-11-01）：原待办，未含 3600 内存压力测试
- **还没做**：G1 的"冷启动 10 次"；§2.4 的 4 卡满载 1 小时（需要有人在场，要带着 NVML +4000 跑）；E 口、转接板 5、线 9/10 单独测试；G5、G6。G3 跳过（最小化测试，直接用 r10 验证）。部署全部结束后撤销免密 sudo：`sudo rm /etc/sudoers.d/90-USER-nopasswd`。
-->

<!-- 已注释 v1.9：原待办
- **还没做**：G1 的"负载下 LnkSta"和"冷启动 10 次"；§2.4 的 4 卡满载 1 小时（需要有人在场）；E 口、转接板 5、线 9/10 单独测试；G3–G6。
-->

**手动复测 P2P**：

```bash
nvidia-smi topo -m                 # 拓扑：PIX / PXB 为正常
nvidia-smi topo -p2p r             # 每对都应是 OK
cd ~/nvidia/nvbandwidth/build
./nvbandwidth -t device_to_device_memcpy_read_ce device_to_device_bidirectional_memcpy_read_ce
# 单向每对约 28.5 GB/s，双向约 56.5 GB/s；跑完看 sudo dmesg | grep -iE "xid|aer"
```

### 4.2 r10 实测记录（2026-10-30）

**对比作者基线**（作者没有公开测试命令和 prompt，只有 steps/s 和 KV 池可以严格比较）：

| 指标 | r10 作者 | PC2 | 判定 |
|---|---|---|---|
| Engine steps/s（`/metrics` 投机解码步数 ÷ decode 时间，定义可能和作者略有差别） | 105.7–106.0 | 112.3（默认频率）/ 116.1（+4000） | ✅ G4 |
| KV 池（CTX 393,216） | 736,359 token | 736,359 token | ✅ 完全相同 |
| 启动时间 | 约 10 分钟 | 约 4.5 分钟 | ✅ |
| Decode（代码） | 319–331 tok/s | 278–300（红黑树 prompt，2048 token，默认频率）；386（LRU prompt，768 token，+4000） | ⚠️ 随 prompt 变化，只能参考 |
| Prefill | 7,841（36K）/ 7,767（100K） | 12,673（15.7K）/ 12,554（60.4K）/ 12,149（152K） | ✅ ≥ 7,000；测法可能不同 |

- tok/s 约等于 steps/s ×（1 + 每步接受的投机 token 数），接受率取决于内容（本次 0.44–0.74）。所以比较引擎性能看 steps/s，不看 tok/s。
- G4 的内存项：没有 OOM kill，启动后可用内存约 34GB，swap 用了 8GB；空闲时 `vmstat` 的 si/so 为 0。**加载阶段的内存峰值和负载期间的 si/so 没有单独采样。**
- 硬件：推理时每张卡峰值 353–397W，最高 66°C。PDU 最高约 7.6A（245V，约 1.86kW），空载也是约 245V，负载没有造成明显压降（读数都是目测）；12V-2x6 接头 34–40°C。这些都是几分钟的短时测试，不能代替 §2.4 的 1 小时满载。
- 对比用的脚本都在服务器 `~/bench/`：`bench.py`、`bench_strata_r10.py`、`conc_strata.py`、`needle.py`、`memoc.py`。

**显存超频**（8 路并发，每路约 17.7K 上下文、生成 1500 token，每档 2 轮）：

| NVML offset | Afterburner 等效 | 最高频率 | 总 decode tok/s | 平均 | 算术检查 | Xid |
|---|---|---|---|---|---|---|
| 0 | 0 | 14001 | 944 / 930 | 937 | 8/8 | 0 |
| **+4000（当前）** | +2000 | 16001 | 955 / 966 | 960（+2.5%） | 8/8 | 0 |
| +5000 | +2500 | 16501 | 936 / 969 | 952（+1.6%） | 8/8 | 0 |
| +6000 | +3000 | 17001 | 952 / 949 | 950（+1.4%） | 8/8 | 0 |

同一档两轮之间就差约 ±15 tok/s。单路 steps/s 从 112.3 到 116.1（+3.4%）。每档只跑了约 1 分钟。

**核心超频**（2026-10-31，显存保持 +4000；每档 3 轮单路 + 1 轮 8 路并发 + 8 道算术，约 1 分钟）：

| NVML 核心 offset | 最慢卡平均频率 | 单路 steps/s | 8 路总 decode tok/s | 单卡峰值 | 最高温度 | 算术 | 结果 |
|---|---|---|---|---|---|---|---|
| **0（当前）** | 2891 MHz | 116.1 | 970 | 384W | 60°C | 8/8 | 正常 |
| +100 | 2981 MHz | 117.3 | 971 | 392W | 64°C | 8/8 | 正常 |
| +150 | 3033 MHz | 117.9 | 974 | 399W | 66°C | 8/8 | 正常 |
| +200 | 3078 MHz | 118.5 | 970 | 402W | 67°C | 8/8 | 正常 |
| +250 | 3126 MHz | 119.1（+2.6%） | 991 | 402W | 67°C | 8/8 | 正常 |
| +300 | 约 3199 MHz | — | — | — | — | — | **GPU0 Xid 109、175、154，引擎退出，必须重启** |

- **决定：不超频。** 频率提高 8% 只换来约 2.6% 的步速，而且离崩溃只差 50 MHz。这些卡没有 ECC，每档又只测了约 1 分钟，算错不一定能发现。偏移不持久，重启后回到 0，没有写进任何服务。
<!-- - **更正瓶颈判断**：此前推断步速主要卡在 GPU 核心，实测并非如此。核心频率 +8.1% → 步速 +2.6%（敏感度约 0.32），显存频率 +14.3% → 步速 +3.4%（约 0.24），两者相加约 0.56。也就是说约四成多的步时不随 GPU 频率变化，可能花在 PCIe 同步或 CPU 调度上（推测，没有分开测过）。功耗和温度不是限制。 -->
- **更正瓶颈判断（2026-10-31 实测）**：单流每步约 8.75ms。核心锁频 1200–2400MHz 拟合为 步时 ≈ 19.5/频率(GHz) + 1.8ms，即约 78% 随核心频率变化，其余 1.8ms 与显存频率能解释的部分大致相当。CPU 上限 4700→2200MHz 只掉 1.5% 步速（Python 线程占满是空转等待）；DDR4 2666→3600 变化不到 1%；PCIe 平均每卡每向约 1.3GB/s。此前“四成多花在 PCIe 同步或 CPU 调度”的推测不成立。接近上限时核心频率的收益明显变小（敏感度 1200–1600MHz 约 0.9，2400–2900MHz 约 0.65，+8% 超频约 0.32），原因未测。功耗和温度不是限制。
- 接受率波动比这大得多：同一个 prompt 连跑 3 轮，接受率就有 0.45–0.74，tok/s 在 273–372 之间。

**并发**（短 prompt，code / prose / zh 轮换，每路 768 token）：

| 并发 | 总吞吐（不限 8 路） | 每路 | 总吞吐（`--max-num-seqs 8`） | 每路 |
|---|---|---|---|---|
| 1 | 约 364 | 376–388 | 363 | 381 |
| 2 | 499 | 299 | — | — |
| 4 | 778 | 240 | — | — |
| 8 | **1,223** | 183 | 1,085（开机后第一轮，未复测） | 181 |
| 16 | 552 | 40 | **1,136**（平均 TTFT 2.8s，超出的请求排队） | 167 |

每路一个不同的约 32K 上下文时（不限 8 路）：1 路 168 tok/s（TTFT 2.5s）、4 路 224（6.4s）、8 路 245（11.7s）。瓶颈在 prefill。

**YaRN 2 倍 A/B**（2026-10-31，CTX 524,288，KV 751,128 token，三组 prompt 相同，temperature 0）：

<!-- 已注释 v1.9（2026-10-31）：下面这组实际跑的是原生 RoPE，YaRN 覆盖没有生效，结果并入下方 A 组的说明
**YaRN 2 倍**（CTX 524,288，KV 751,128 token）：

| 测试 | 结果 |
|---|---|
| 大海捞针，约 27.5 万 token，埋在 10% / 50% / 90% | 3/3 通过，每次约 23 秒 |
| 大海捞针，约 48.3 万 token，埋在 10% / 50% / 90% | 3/3 通过，每次约 43 秒（约 11.2K tok/s） |
| 算术检查 | 8/8 |
| 短 prompt code / prose / zh | 387 / 271 / 285 tok/s（1.5 倍时 386 / 274 / 278） |

作者只验证过 1.5 倍。这里的测试只覆盖检索和算术，长文档理解等更细的质量差异没有评估。客户端在 75% 处压缩（约 39.3 万 token），在测过的长度以内。
-->

| 测试 | A：原生 RoPE（原配置） | B1：只有主模型 YaRN | **B2：主模型 + 草稿模型 YaRN（当前）** |
|---|---|---|---|
| 短 prompt steps/s | 116.4–116.8 | 116.4–117.0 | 116.4–117.0 |
| 短 prompt 接受率 code / prose / zh | 0.49 / 0.44 / 0.38 | 0.46 / 0.48 / 0.42 | 0.48 / 0.44 / 0.40 |
| 48.3 万 token steps/s | 113.7–114.8 | 114.0–114.2 | 114.4–114.8 |
| 48.3 万 token 接受率 code / prose | 0.68 / 0.46 | 0.47 / 0.43 | 0.52 / 0.49 |
| 48.3 万 token tok/s code / prose | 350 / 271 | 275 / 262 | 293 / 284 |
| 大海捞针（27.5 万 ×3，48.3 万 ×5） | 8/8 | 7/8 | 7/8 |
| 顺序题（两句话谁在前，48.3 万 ×8） | 7/8 | 6/8 | 8/8 |
| 算术 | 8/8 | 8/8 | 8/8 |

- **根因**：r10 把覆盖写到顶层 `rope_parameters`，而模型读 `hf_text_config`，那里仍是 `rope_type: default`。Flash-Next 配方里 YaRN 从未生效；作者的 1.5 倍数据如果也用这个写法，同样如此。作者自己合并的 [vllm-project/recipes#398](https://github.com/vllm-project/recipes/pull/398) 用的是 `text_config` 嵌套写法。
- **结论**：三组差异都没有超出测试波动。所有失败都是思考跑满 token 上限、没有给出答案（A 1 次，B1 3 次，B2 1 次），没有答错。同一 prompt 的接受率本身就有 0.45–0.74 的波动，所以 A 的 0.68 不算明显更好。
- **决定：保留 B2**。它是模型卡给的方案，主模型和草稿模型的 RoPE 一致，测试结果也不比 A 差。代价是多一个本地补丁。
- **未评估**：这里只测了检索、顺序和算术，样本也小。模型卡和 #398 提到 YaRN 会影响短上下文质量，这一项没有测出来，也不能算排除。
- 客户端在 75% 处压缩（约 39.3 万 token），在测过的长度以内。

**长上下文的显存警告**：跑长上下文时日志有 70 条 `CUDACachingAllocator … memory allocation failed with OOM`，单次申请 214–512MB，请求全部成功（24 个 200，1 个 400 是超长请求），容器没有重启，没有 Xid。原因：r10 固定了 KV 大小，跳过了显存测算（`skipped memory profiling`），每张卡只剩约 0.5–1.5GB，PyTorch 释放缓存后重试成功。用户单请求为主，决定不改；真正出现 500 或容器重启时，把 `KV_BYTES` 降到 5.5GB（KV 约 69 万 token，仍大于 524,288）。

**GPU3 显存略高**：`nvidia-smi` 3 号卡（总线 0C）比其他卡多约 1.1GB（31,178 MiB 对 30,074–30,102 MiB），全部算在 `Worker_TP3_EP3` 进程上；4 张卡的模型（20.66GiB）、KV（5.59GiB）、graph（0.21GiB）相同。**推测**是 PyTorch 留着临时显存没有归还，未直接证实。下次容器重启时，对比第一个长请求前后的占用即可确认；如果占用随时间一直上涨才可能是泄漏。

**PC1 Strata 对比**：用同一个 `bench_strata.py`，分词器相同（同一段文本 `prompt_tokens` 完全一致），上下文长度对齐到 32,235 / 107,835 token。完整结果在 PC1 的 `D:\Strata-backups\bench\20261030-r10-pc2.txt`。

| 测试 | r10 code / prose / zh（4×5090，+4000） | Strata IQ3_XXS（2×5090，10-05） | r10 快多少 |
|---|---|---|---|
| 短 prompt | 386 / 274 / 278 | 287 / 197 / 217 | +35% / +39% / +28% |
| 32,235 token | 374 / 284 / 278 | 274 / 192 / 209 | +36% / +48% / +33% |
| 107,835 token | 367 / 271 / 271 | 261 / 187 / 206 | +41% / +45% / +32% |
| Prefill 15.7K / 60.4K | 12,673 / 12,554 tok/s | 6,721 / 9,683 tok/s | 1.9 倍 / 1.3 倍 |

两边量化不同、卡数不同，这里只比速度，没有比回答质量。Strata 不支持并发处理：2 路、4 路时总吞吐约 175 tok/s，请求排队（当天 IQ3_S 配置）。

**内存 XMP A/B**（v1.9 补充，2026-10-31；同一脚本，temperature 0，DDR4-2666 → 3600）：

| 测试 | steps/s 2666 | steps/s 3600 |
|---|---|---|
| 短 prompt code / prose / zh | 116.4 / 117.0 / 117.0 | 116.0 / 116.6 / 116.5 |
| 48.3 万 token code / prose | 114.8 / 114.4 | 115.8 / 115.2 |

- 48.3 万 token 首次填充 43.16 → 42.91 秒；8 路约 +1.3%。都在波动范围内。
- 开机后 BAR1 4/4，r10 约 3 分钟恢复，Xid 0。这次完整重启也验证了 autotune tmpfs 的修复。
- needle 7/8、order 6/8，失败都是思考跑满 token 上限。

**按温度和思考模式**（v1.9 补充，2026-10-31；短 prompt，每格 3 轮，tok/s / 接受率；采样期间没有外部请求）：

| 模式 | code | prose | zh | 复制文本 |
|---|---|---|---|---|
| 温度 1 + 思考（my agent stack 很可能的实际用法） | 235 / 0.38 | 222 / 0.34 | 232 / 0.37 | 318 / 0.65 |
| 温度 0 + 思考 | 292 / 0.54 | 256 / 0.43 | 265 / 0.46 | 329 / 0.66 |
| 温度 1，不思考 | 319 / 0.63 | 242 / 0.40 | 259 / 0.45 | 394 / 0.89 |
| 温度 0，不思考 | 342 / 0.69 | 256 / 0.46 | 302 / 0.57 | 397 / 0.88 |

- 步速基本不变，差别全在接受率。温度越低，草稿越容易命中，同样开思考时温度 0 比温度 1 快 3–24%。
- 前面各表的 tok/s 大多是温度 0 或不思考测的，比日常用法偏高。
- 这些数字保留了每个 prompt 的第一轮，没有单独预热。

### 4.3 Basalt 实测记录（v1.9 补充，2026-11-01）

**是什么**：[Basalt](https://github.com/jesdga95/basalt)（[X38]）是 Strata 的 C++ 分支，只支持 Blackwell（SM120），跑的是同一个 Qwen3.8-Flash-Next。主卡负责密集层、KV、草稿模型和一部分专家，其余卡只放专家，**没有张量并行**。草稿窗口最多 8，按接受概率自适应。NVFP4 包（[X39]）的专家和 NVIDIA 权重逐位相同，密集层是 Q6_K（对 Q8 的 KLD 0.068，top-1 一致 91.46%），KV 用 int8。

**部署（只用于测试，没有开机自启）**：

| 项目 | 值 |
|---|---|
| 源码 | `~/basalt`，commit `9175e7a3211b`，用 `/usr/local/cuda/bin` 的 nvcc 编译，venv `.venv` |
| 模型 | `~/basalt/models/Qwen3.8-FN-NVFP4.basalt`（122 GiB） |
| 配置 | `~/bench/bt/cfg1.json`：GPU `0,1`，端口 8037，别名 `vllm/qwen3.8-flash-next`，`parallel 1`，`expert-cache auto`，`kv int8`，`resident-experts true`，`max-context 524288` |
| 启动 | 先停 r10；`sudo prlimit --memlock=unlimited:unlimited --pid $$; cd ~/basalt; bin/basalt serve --config ~/bench/bt/cfg1.json --python ~/basalt/.venv/bin/python`（默认只监听 127.0.0.1） |
| 加载时间 | 约 35 秒（r10 约 3.5 分钟） |
| 不开 | `--relaxed-drafting`：会改变输出分布 |

**卡数**（`basalt-bench --community`，每档只跑 1 次）：

| 卡数 | 1 | **2** | 3 | 4 |
|---|---|---|---|---|
| tok/s | 232 | **549** | 461 | 397 |

- 这个跑分 76% 的 token 来自温度 0 的 JSON 生成（另两段温度 0.6），不开思考，没有预热，**不能代表日常速度，也不能和 r10 比**。同 commit 的公开 2×5090 数据是 553.6（[X40]）。
- 2 卡放下 24576 个专家中的 21085 个：主卡 24.3 GiB（其中 7.12 GiB 借给 KV）、第二张 30.0 GiB、内存 9.0 GiB，命中约 99%。内存里锁定的专家副本 55.2 GiB。
- 公开的多卡报告都是加卡变快（4×5080：2 卡 286 → 4 卡 343，[X41]、[X42]），但那是 16GB 卡，2 卡命中率只有 69%。我 3、4 卡变慢的原因没查。

**和 r10 同 prompt 对比**（tok/s，r10 → Basalt 2 卡）：

| 场景 | code | prose | zh | 复制文本 |
|---|---|---|---|---|
| 短 prompt，温度 1 + 思考 | 235 → 382 | 222 → 348 | 232 → 325 | 318 → 370 |
| 短 prompt，温度 0 + 思考（Basalt 去掉第一轮） | 292 → 392 | 256 → 387 | 265 → 388 | 329 → 466 |
| 短 prompt，温度 1，不思考 | 319 → 463 | 242 → 377 | 259 → 397 | 394 → 758 |
| 11 万 token，温度 1 + 思考 | 248 → 324 | 218 → 288 | — | — |
| 22 万 token，温度 1 + 思考 | 241 → 307 | 229 → 270 | — | — |
| 33 万 token，温度 1 + 思考 | 234 → 252 | 241 → 257 | — | — |
| 48.3 万 token，温度 0（Basalt 去掉第一轮） | 287 → 296 | 277 → 248 | — | — |

| 其他 | r10 | Basalt |
|---|---|---|
| 8 路总吞吐 | 约 1,190–1,210 | 约 475–495（0 损坏） |
| 首次填充 11 / 22 / 33 / 48 万 token | 8.9 / 18.4 / 28.3 / 约 43 秒 | 10.6 / 19.6 / 27.2 / 42.3 秒 |
| 缓存命中后首 token | 0.26–0.75 秒 | 0.04–0.08 秒 |
| 回忆（needle / order） | 7/8 / 6/8 | 8/8 / 8/8 |
| 工具调用 | 可用 | 两轮完整通过，返回 `reasoning_content` |

- **第一轮慢是真实的**：Basalt 每个新 prompt 第一轮每步约 8–9 ms，之后约 6 ms，专家命中率从 97.5% 升到 99.7%（可能是常用专家还没换进显存，推断）。48 万 token 第一轮只有 153 / 167 tok/s。
- 早先报告的“温度 1 下 Basalt 略快”和“48 万 token 慢 13–20%”都是测试顺序造成的：温度 0 总在前面，承担了第一轮。表里已改为去掉第一轮的数字；r10 的数字保留了第一轮，所以对比略偏向 Basalt。
- Basalt 回忆 8/8 可能部分来自它的思考预算：到上限会强制收尾（日志 `thinking budget reached (4500 tokens), wrapping up`），r10 没有这个机制。
- 11–33 万 token 没测过温度 0；48 万到 52.4 万 token 没测过；图片输入（测试配置 `images=off`）没测过；稳定性只跑了约 40 分钟；没有接 my agent stack 实际用过。

**为什么快**（引擎日志，每步 token / 每步耗时）：

| 场景 | r10 | Basalt |
|---|---|---|
| code，温度 1 + 思考 | 2.13 / 9.1 ms | 2.28 / 5.9 ms |
| prose，温度 1 + 思考 | 2.01 / 9.1 ms | 1.92 / 5.5 ms |
| 复制文本，温度 1，不思考 | 3.66 / 9.3 ms | 8.2 / 10.6 ms |
| prose，48 万 token，温度 0 | 2.41 / 8.7 ms | 2.07 / 8.4 ms |

- 快在每步耗时，不在接受率（两边的接受率定义不同，不能比）。
- 约一半来自窗口更窄：r10 每步固定算 4 行，Basalt 平均 2.4–2.9 行（约 2.7 行 5.5–6 ms，4–5 行 7–8.5 ms，8 行 10.6 ms）。另一半来自引擎开销小：同样约 4 行时 Basalt 约 7.3 ms，r10 约 9 ms，大致对应 r10 每步约 106 次卡间同步约 2 ms（推断）。
- 长上下文时 Basalt 每步从 5.5 涨到 8.4 ms，可能是 KV 变大后主卡要还回借用的显存，显存里的专家降到约 75%（推算，未直接测）。
- 8 路并发时 Basalt 几乎不再用草稿（每步 1.00 token，8 行 14.3 ms），所以只有约 490 tok/s。

**上下文**：`parallel 1` + `max-context 524288` 和 r10 的上限相同，超限返回 400。`max-context` 由所有 slot 平分（`parallel 2` 各 262,144，`parallel 8` 各 65,536）；`slot-full-context` 估算 2 路要约 23 GiB KV，几乎占满主卡的专家缓存，不实用。r10 则是所有请求共用约 75 万 token 的 KV。

**实际流量**（r10 日志，10-31 20:27 到 11-01 19:19 UTC，客户端 `192.168.1.OBFUSCATED` 是 PC1）：

- 运行加排队的请求数：1 个 162 次采样，2 个 10 次，3 个 4 次（7–9 个的 26 次基本是我的测试）。KV 占用 p50 23%、p90 34%、p99 53.5%、最高 63.7%。
- 平时基本是单个长对话（例如 13 万涨到 26 万、24 万涨到 31 万 token），切换集中爆发：23:48–00:27 两个 11 万和 26 万的对话隔 10–50 秒交替，23:55 有 3 路同时运行、合计约 47.8 万 token。切回 10 万 token 以上的对话共 14 次，其中 11 次在这 40 分钟里。
- 这些是用 KV 占用推算的对话长度，次数是近似值。r10 自己也有 8 次超过 10 万 token 的重读，原因没查。

**结论（2026-11-01）**：**不切换**。单个长对话时 Basalt 明显更快，但 `parallel 1` 下切换爆发会排队，交替时可能反复重读（未测）；`parallel 2` 又装不下 26 万以上的对话。

**候选：两个 Basalt 实例**（未测，上游也没有这种部署的报告）：

| 项目 | 方案 |
|---|---|
| 分卡 | 实例 A 用 GPU 0,1，实例 B 用 GPU 2,3，各有完整 524288 上下文。GPU 1 和 2 在同一个下级 switch 下（PIX），配对方式要比较；GPU 2,3 还没单独跑过 Basalt |
| 内存 | 两个实例各锁 55.2 GiB 会超出 125 GiB。首选 `peer-exclusive`（估计每个约 25 GiB，代价是长 prompt 不能分卡读取）；备选 `shared-expert-arena`（`/dev/shm` 共用一份，仓库测试没覆盖） |
| CPU | 每个实例工作线程从默认 11 改为约 9（共 20 线程） |
| 请求分配 | 一个小代理监听 `:8036`，按对话开头固定发到同一个实例，my agent stack 不用改 |
| 和 r10 | 都要占满 4 张卡，不能同时运行 |

通过标准：同时运行时每路不低于单独运行的 85%；两个长对话交替时不重读，切回首 token ≤ 约 0.1 秒；温度 0 输出和单实例一致、无损坏；50 万 token 下内存仍有余量。**通过就用两个实例，不通过就留在 r10。** 测试时以温度 0 / 0.3 / 0.6 为主，每组先预热，并补测 11–33 万 token 低温度、52 万 token、4 卡单实例在 33 / 48 万 token。需要停 r10 约 30 分钟。

**其他评估（2026-10-31，未实测）**：

- DeepSeek V4.1 Flash 1017：可走 Strata 的 2.25 bpw 包（约 274GB），估计 78–83% 专家在显存、60–100 tok/s、一次一个请求。难的多文件代码任务可能更强（DeepSWE 77.0 对 58.7），其他场景 r10 优先。第三方仓库里的转换和启动脚本没有审查，不运行。
- RTX PRO 6000 单卡：一份公开报告单流 287、8 路 965、prefill 14.5K tok/s，和本机 r10 大致相当。

### 4.4 采样温度（v1.9 补充，2026-11-01）

| 来源 | 内容 |
|---|---|
| 模型卡（[X43]）和 `generation_config.json` | 思考模式 temperature 1.0、top_p 0.95、top_k 20；不思考 0.7、0.8、presence_penalty 1.5。官方代码榜单按 1.0 测。没有说明原因，只提到用 presence_penalty 减轻无尽重复 |
| QwenCloud（[X45]，云端 `qwen3.8-flash`） | “In thinking mode, `temperature` defaults to 0.6; smaller values are automatically adjusted to 0.6.” 也就是开思考时 **0.6 是下限**。没有说明原因；和本机的 Flash-Next 是否同一权重没有确认 |
| 论文（[X44]） | 推理模型在低温度下都会循环，温度 0 最严重；没测这个模型 |
| 本机 | r10 温度 0 的回忆测试里有 3 次失败都是 4000–6000 token 全在思考、答案为空，符合循环症状，但没保存文本，无法确认 |

- **建议**：开思考（my agent stack 是 `reasoning_effort: xhigh`）默认 **0.6**；关思考的短任务可以更低。用户偏好低温度，用途是写代码、agent 工具调用和务实回答。
- **现状**：服务器默认仍是 1.0，没有改。
- **测试计划（未做）**：约 20 个代码和 agent 任务，开思考，比较 0 / 0.3 / 0.6 / 1.0，记录循环率（同一个 30-gram 出现 ≥ 20 次）、无答案率、正确率和 tok/s。选循环率和无答案率都不比 1.0 差的最低温度；0 或 0.3 只有在这两项不比 0.6 差时才采用。温度按请求设置，在 r10 上跑不用重启，约 30–60 分钟，要等客户端空闲。
- **怎么改默认值**：r10 在 `launch.sh` 里加 vLLM 的 `--override-generation-config '{"temperature": 0.6}'`，然后重建容器（约 3.5 分钟，没试过）；Basalt 用 `--temperature`。客户端自己传的温度优先。

---

## 5. 故障处理与回退

| 现象 | 处理 |
|---|---|
| LnkCap 本身偏低 | switch 配置问题，退货（§1.1） |
| 空载 LnkSta 显示 2.5GT/s | 正常省电，加负载复查（[X18]） |
| BAR1 只有 256MiB | 本机由 `gpu-rebar.service` 放大 BAR：`systemctl status gpu-rebar`、`journalctl -u gpu-rebar -b`；确认 cmdline 有 `pci=nocrs`（§3 第 4 步"4 卡 BAR"） |
| 3 张以上卡开机卡在 Q-LED **VGA**（白灯） | BIOS 的 64-bit 窗口只有 256GiB。确认 BIOS Re-Size BAR = **Off**（BIOS 更新后会恢复默认，要重新确认）。先退回单卡进 BIOS 改设置 |
| `gpu-rebar: x/4 GPUs have a 32G BAR1`（x < 4），或 `nvidia-smi` 少卡 | `sudo dmesg \| grep -E "can't assign\|failed to assign"`；确认 cmdline 有 `pci=nocrs`、BIOS ReBAR = Off、内核不是 7.x；仍不行用 GRUB 调试项（不加载 nvidia）开机，手动执行 `sudo /usr/local/sbin/gpu-rebar.sh` 看输出 |
| `gpu-rebar: 0/4`，日志里 BAR 分配的前缀是 `nvidia`，`ctrl=0x821`；dmesg 有 `P2P mailbox area expected` | 有别的服务抢先加载了驱动。`journalctl -b -o short-monotonic \| grep -E "NVRM: loading\|gpu-rebar"` 看顺序，给它加 `After=gpu-rebar.service`。临时恢复：`docker stop fnext-vllm` → `sudo systemctl restart gpu-rebar gpu-memoc` → `docker start fnext-vllm` |
| `BAR … no space` / `failed to assign`，或 `NVRM: Fatal Error while attempting to resize PCIe BARs`（[X16]） | 检查 BIOS 的 Above 4G / ReBAR → Profile 1 → Profile 2 → §3 第 4 步里的升级顺序。注：[X16] 是基于 595 驱动的讨论，610.57.04 是否包含相关改动需要另行确认 |
| 冷启动少卡 | 整机全部 PSU 断电，等 10 秒，同步重新上电。别指望 `pci rescan`。总是同一张卡缺失时，交换 PSU / 线 / 转接板，看问题跟着哪个部件走 |
| 链路掉到 Gen2 / Gen3，或 AER 持续增长 | 换短线，确认线和转接板与卡同一卖家（[R03]）；BIOS 强制 Gen4；仍不行再加 retimer |
| `Xid 109`（CTX SWITCH TIMEOUT），接着 `Xid 175 / 154`、`Reset required`，`nvidia-smi` 该卡显示 `[N/A]` | 2026-10-31 核心 +300 MHz 时 GPU0 出现过。先确认核心偏移是 0，然后整机重启。这次关机到重新开机约 11 分钟，要有心理准备，原因没有查明 |
| 容器 running 但 `/health` 一直不通，日志停在 `Autotuning process starts`，反复出现 `shm_broadcast … No available`；只有 GPU0 利用率 100%、约 115W，其余 3 张在 P8；无 Xid | 沿用旧容器时命中 autotune 缓存就会卡死，`docker restart` 能复现，全新容器正常。`launch.sh` 已用 `--tmpfs` 清空缓存。临时恢复：`docker rm -f fnext-vllm` 后重新执行 `launch.sh`。根因未查明（10-30 原配置重启时没有卡住） |
| 运行中 `Xid 79`（掉卡） | 先查那台 PSU 是否触发了过流 / 过功率保护，再查 12V-2x6 接头 |
| 整机无故断电或重启 | 先怀疑 PSU-H Super Flower：它是主控，又没有 ATX 3.x 瞬时余量。给 GPU3 设上限（400–450W）复测；可临时拔掉 GPU3 复测；仍断电再查同步板和 240V 链路 |
| 某张卡 Max Power Limit 只有约 450W | 转接线只接了 3 个 8-pin，或有一个没插到底（§2.6） |
| 从电源不跟随启动 / 少卡 | 先按 §2.5 单独测试同步板（带指示灯的 BQZYX+ 能直接看出哪路没起来）；换备件后再测 |
| Z690 识别不到 switch 下的设备，或 BAR 怎么都分不到 | 把 switch 卡、线、转接板整体搬到 X870E 的 PCIEX16_1（M.2_2/3 不插）。AM5 + 88096 有成功案例（[M04]） |
| G4 内存不够（OOM / 持续 swap） | 同上，搬到 X870E；插满 4×48GB DDR5，两套时序不同，要手动取两套中较松的时序，从 5200 起步并跑 MemTest（调法见完整版附录 C） |
| P2P 始终起不来 | 先确认 ACSCtl 和 IOMMU 设置（§3 第 4 步）；仍不行就临时改用 TP2×PP2 或 TP2×DP2，同时回到完整版重新评估平台 |
| 构建镜像报 `nightly-eed1f3d0… not found` | 基础镜像已下架，按 §3 第 5 步用 v0.29.0 + wheel 重建 |
| `flashinfer-cubin version … does not match flashinfer version` | 三个 flashinfer 包要同一版本；cubin 和 jit-cache 从 GitHub Release 下载（[X36]） |
| 重启后 vLLM 没有启动，`docker ps` 里没有容器 | 手动 `docker stop` 过：`docker start fnext-vllm`。如果是 `gpu-rebar` 失败，先按上面处理 |
| 日志有 `CUDACachingAllocator … failed with OOM`，但请求正常返回 | 分配器重试成功，可以不管（§4.2） |
| 请求返回 500，日志有 `Traceback` / `torch.OutOfMemoryError`，或容器在重启 | 真正的显存不足：`launch.sh` 里 `KV_BYTES` 降到 5500000000，重建容器 |
| 并发超过 8 路时变慢 | 正常排队（`--max-num-seqs 8`），确认这个参数还在：`docker inspect fnext-vllm --format "{{json .Args}}"` |
| 超频后 tok/s 反而下降、回答出错或出现 Xid | `sudo systemctl stop gpu-memoc` 恢复默认频率后复测（§3 第 4 步"显存超频"） |
| 开思考时答案为空，思考用满了 `max_tokens`（v1.9 补充） | 温度 0 或很低时更容易出现（§4.4）。改用 0.6，或加大 `max_tokens`。Basalt 有思考预算会强制收尾，r10 没有 |
| 测 Basalt 时显存不足，或测完 r10 没起来（v1.9 补充） | 两者都要用 GPU 0,1，不能同时跑：先 `docker stop fnext-vllm`，Basalt 退出后再 `docker start fnext-vllm`。Basalt 启动前要 `sudo prlimit --memlock=unlimited:unlimited --pid $$`，否则锁不住内存（§4.3） |
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
| [X34] | linux-pci 邮件列表，Matt Protacio，2026-10-25："[REGRESSION] PCI: sibling bridge windows undersized after rescan since f909e3ee3ed1"。PEX88096 + ASUS Z790 + 4×V100（32G + 32M）：BIOS 窗口太小且零碎，GPU 开机通电会卡 POST；6.17 下重新扫描得到 192G 窗口，v7.0–7.3 失败。
| [X35] | vLLM eed1f3d0 per-commit wheel（wheels.vllm.ai） |
| [X36] | FlashInfer v0.6.18.post1 GitHub Release（cubin、jit-cache） |
| [X37] | NVIDIA Container Toolkit 安装文档 |
| [X38] | Basalt 源码仓库（jesdga95/basalt） |
| [X39] | Basalt 模型包：Qwen3.8-Flash-Next-Basalt（NVFP4、IQ3 等包，质量表） |
| [X40] | Basalt issue #193：同 commit 的 2×5090 community 跑分 553.6 |
| [X41] | Basalt issue #80：4×5080 community 跑分 2 卡 286 → 4 卡 343 |
| [X42] | Basalt issue #52：同一台 4×5080 客户端实测 126.7 → 156.8，命中率 69% → 89–94% |
| [X43] | Qwen3.8-Flash-Next 官方模型卡（推荐采样参数） |
| [X44] | Wait, Wait, Wait... Why Do Reasoning Models Loop?（arXiv 2512.12895） |
| [X45] | QwenCloud：Latest model: Qwen3.8-Flash（思考模式 temperature 默认且最低 0.6） |

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
[X35]: https://wheels.vllm.ai/eed1f3d0c6043bd494424a22443ee198dd56f657/vllm/
[X36]: https://github.com/flashinfer-ai/flashinfer/releases/tag/v0.6.18.post1
[X37]: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
[X38]: https://github.com/jesdga95/basalt
[X39]: https://huggingface.co/jesdga/Qwen3.8-Flash-Next-Basalt
[X40]: https://github.com/jesdga95/basalt/issues/193
[X41]: https://github.com/jesdga95/basalt/issues/80
[X42]: https://github.com/jesdga95/basalt/issues/52
[X43]: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
[X44]: https://arxiv.org/abs/2512.12895
[X45]: https://docs.qwencloud.com/developer-guides/getting-started/latest-model

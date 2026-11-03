# 4×RTX 5090 + PEX88096 实施计划（精简版）

依据：[5090-multi-gpu-plan-v3.9.md](5090-multi-gpu-plan-v3.9.md)（2026-10-06）。论证、备选平台、8 卡扩展和完整来源都在完整版里，本文只保留 4 卡 88096 的执行方案。

---

## 0. 方案一览

| 项目 | 决定 |
|---|---|
| 推理服务器 | Z790-A D4 + i7-12700K + 4×32GB DDR4（同一套装，128GB），**纯 Ubuntu Server** |
| 日常机 | X870E + 9950X3D 继续跑 Win10，不改动 |
| GPU fabric | PEX88096 **分体 kit**：switch 卡插在 Z790 的 PCIEX16_1；每张 GPU 用 2 根 SFF-8654 8i 线接一块带 12V 输入的 x16 转接板 |
| 链路 | 上行 1×Gen4 x16，下行 4×Gen4 x16，4 张卡在同一 switch 内（PIX） |
| 软件 | aikitoria P2P 驱动 610.57.04 + QWEN-PEDIA r10 配方（vLLM overlay，TP4 + EP，NVFP4） |
| 供电 | 4 台 PSU，**每张卡的转接板 12V 和 12V-2x6 来自同一台 PSU**，全部同步上电 |
| 新增花费 | 约 $0.7k–1.15k（不含 retimer） |
| 回退方案 | 内存不够，或 switch 在 Z790 上识别不到设备时，把 kit 整体搬到 X870E（4×48GB = 192GB，AM5 已有成功案例） |

**为什么不用一体背板**：ADT-Link 5 槽背板槽距只有 40.6mm，4 张 5090 放不下（[X11]）；c-payne 背板写明不兼容 Intel 消费级平台（[X12]）；而且一体背板的槽供电通常共用一个入口，做不到"同卡同源"。

---

## 1. 采购清单

| 项目 | 规格要点 | 预算 |
|---|---|---:|
| PEX88096 switch 卡 | x16 金手指，10×SFF-8654 8i，固件配成 1×x16 上行 + 5×x16 下行（[M09] 卡价约 $446） | 与下两项合计 $575–850 |
| SFF-8654 8i 线 × 8 | 与 switch 卡**同一卖家**，≤50cm，问清阻抗（85Ω / 100Ω） | （含上） |
| x16 设备转接板 × 4 | 双 8i 输入，**每块自带 12V 输入**（6-pin / EPS，[X09], [X10]） | （含上） |
| switch 散热 | 卡上风扇 + 机箱气流；88096 待机也很热（[M04]） | $60–150 |
| PSU 同步线 / 同步板 | 支持 4 台 | $40–150 |
| 矿架 / 测试台 | 转接板按卡厚固定，3 槽卡中心距 ≥ 80mm | 已有或少量 |
| Retimer | **默认不买**，只在 G1 链路不稳时再加 | $0（最坏约 $130 × 链路数） |

**下单前必须拿到卖家书面答复：**

1. 固件 / DIP 支持 **1×Gen4 x16 上行 + 4–5×Gen4 x16 下行同时工作**；提供 DIP 表和固件版本，SPI flash 已烧录。
2. 每块转接板都有独立 12V 输入，并说明接口类型；switch 卡本身由什么接口供电。
3. REFCLK / PERST# / presence 信号由卡和转接板正确处理；便宜的线材可能不传 presence 信号（[X14]）。
4. **在 Intel LGA1700 / Z790 上测试过吗？** 在 RTX 50 系上测试过吗？能否提供 `lspci -vv` 输出？
5. 多台 PSU 时的上电建议。

> 约 $500 的 PEX 卡多为拆机件（[X14]）。选出货量大、可退货的卖家，到货后先跑 G1。

---

## 2. 拓扑与供电

```text
Z790 PCIEX16_1（CPU 直连）
  └─ PEX88096 switch 卡（主机 PSU 供电）
       ├─ 2×8i ─ 转接板0 ─ GPU0 ┐ PSU-1 1600W
       ├─ 2×8i ─ 转接板1 ─ GPU1 ┘
       ├─ 2×8i ─ 转接板2 ─ GPU2 ── PSU-2 1200W（新）
       └─ 2×8i ─ 转接板3 ─ GPU3 ── PSU-3 1000W
```

| PSU | 带什么 | 负载 @400W/卡 | 负载 @575W/卡 |
|---|---|---|---|
| **PSU-H 1200W（旧，无 12V-2x6）** | Z790 主机 + switch 卡；**PS_ON 主控** | ~30% | ~30% |
| PSU-1 1600W | GPU0、GPU1 的 12V-2x6（2 个独立接口）+ 转接板 0/1 的 12V | ~50% | ~72% |
| PSU-2 1200W（新） | GPU2 的 12V-2x6 + 转接板 2 的 12V | ~33% | ~48% |
| PSU-3 1000W | GPU3 的 12V-2x6 + 转接板 3 的 12V | ~40% | ~58% |

**规则：**

- **同卡同源**：一张卡的所有 12V 来自同一台 PSU，避免 12V 倒灌烧卡（[X06]）。
- **同步上电**：PSU-1/2/3 的 PS_ON 接到 PSU-H 上。主机 POST 要几秒才释放 PERST#，GPU 的 12V 早已稳定，满足 PCIe 规范"供电稳定 100ms 后才释放 PERST#"的要求（[X05]）。
- **不单独断电**：运行中任何一台 PSU 都不能单独关；掉了一台就整机断电重启。
- 每张卡用原生 12V-2x6，不用转接线，不用 Y 线（[M47]）。
- **AC 回路（115V）**：回路 1 = PSU-1 + PSU-H，回路 2 = PSU-2 + PSU-3。
  - 400W/卡：回路 1 约 11A，15A 回路可用；
  - 575W/卡：回路 1 约 14A，**必须是 20A 回路**。
- 旧 1200W 上机前先体检：接功率计带主机满载 1 小时，观察 12V 电压。

---

## 3. 实施步骤

### 第 1 步：采购前验证（$0）

1. Z790：装 4×32GB，开 XMP，MemTest86 跑 1 轮；装 Ubuntu Server LTS 最小化。
2. 在 X870E 上用临时 SSD 启动 Ubuntu。现有 2×5090 是 CPU 直连 x8/x8，在这台上装 aikitoria 驱动，跑 `p2pBandwidthLatencyTest` 和 vLLM TP2。
   - P2P 不通 → 先解决驱动或 BIOS，**暂不采购**。

### 第 2 步：采购

按 §1 下单，拿到卖家对 5 条确认项的书面答复。

### 第 3 步：装机

- switch 卡只插 PCIEX16_1。和它共享通道的 M.2 槽不插，以 Z790-A D4 规格页为准（[N10]）。
- 转接板按卡厚固定，8i 线不要硬折，switch 卡要有气流吹过。
- 按 §2 接电，接好同步线，再按 G1 的方法冷启动。

### 第 4 步：BIOS 与系统

```text
BIOS（Z790）：Above 4G = On，Resizable BAR = On，CSM = Off，VT-d = On，
             PCIEX16_1 = Auto（训练不稳时强制 Gen4），ASPM = Off（排障期）
内核参数：    intel_iommu=on iommu=pt
             （passthrough 下 P2P 不通时可改为 intel_iommu=off，[M03]）
```

**驱动**：aikitoria open-gpu-kernel-modules **610.57.04**（[X01]），装好后 `apt-mark hold` 住 nvidia 相关包，防止升级把补丁覆盖掉。

- 确认 BAR1 = **32GiB**（覆盖全部显存）：`nvidia-smi -q -d MEMORY | grep -A3 BAR1`。

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
  - 建 32GB swapfile，只用来扛模型加载时的峰值；
  - r10 配置里的 CPU 侧 KV 缓冲能关就关；
  - mlock 不限额：容器加 `--ulimit memlock=-1:-1`，裸机改 `limits.conf`。
- 服务监听 LAN 地址，用 `ufw` 只放行 X870E；客户端改连 Z790 的 IP。

---

## 4. 验收 Gate（前一级不过，不进下一级）

| Gate | 方法 | 通过标准 |
|---|---|---|
| **G1 链路** | `lspci -vv`（LnkSta）、`nvidia-smi -q -d PCIE`、`dmesg \| grep -i aer` | 上行和 4 条下行都是 16GT/s x16；1h 内 AER 不增长；**连续冷启动 10 次，每次 4 张卡都识别** |
| **G2 P2P** | `nvidia-smi topo -m`、`p2pBandwidthLatencyTest` | 所有卡对为 PIX；单向 ≥ 24 GB/s，双向 ≥ 45 GB/s（社区实测 25–28 / 约 52，[M03], [M04], [M05]） |
| **G3 NCCL** | `all_reduce_perf -b 8M -e 1G -f 2 -g 4` | 记录 busbw；1GB 时低于 15 GB/s 视为异常 |
| **G4 应用** | r10，TP4 + EP，固定 prompt 和功率上限 | ≥ r10 基线的 90%：≥ 95 steps/s，decode ≥ 290 tok/s，prefill ≥ 7,000 tok/s；内存峰值无 OOM，`vmstat` 的 si/so 接近 0 |
| **G5 A/B** | `NCCL_P2P_DISABLE=1` + 关掉 custom AR，重跑 G4 | 记录 P2P 带来的 pp / tg 差值 |
| **G6 稳定性** | 24h 服务压测，`dmesg \| grep -i xid`，红外测温 12V-2x6 接头 | 无 Xid、无掉卡、接头温度正常 |

出现以下任一情况，**先查硬件链路，不要调 vLLM**：单向只有 10–15 GB/s、某张卡明显偏低、拓扑不是 PIX、链路掉到 Gen3/Gen2。

---

## 5. 故障处理与回退

| 现象 | 处理 |
|---|---|
| 冷启动少卡 | 整机全部 PSU 断电，等 10 秒，同步重新上电。别指望 `pci rescan`。总是同一张卡缺失时，交换 PSU / 线 / 转接板，看问题跟着哪个部件走 |
| 链路掉到 Gen2 / Gen3，或 AER 持续增长 | 换短线，确认线和转接板与卡同一卖家（[R03]）；BIOS 强制 Gen4；仍不行再加 retimer |
| 运行中 `Xid 79`（掉卡） | 先查那台 PSU 是否触发了过流 / 过功率保护，再查 12V-2x6 接头 |
| Z790 识别不到 switch 下的设备 | 把 switch 卡、线、转接板整体搬到 X870E 的 PCIEX16_1（M.2_2/3 不插）。AM5 + 88096 有成功案例（[M04]） |
| G4 内存不够（OOM / 持续 swap） | 同上，搬到 X870E；插满 4×48GB DDR5，两套时序不同，要手动取两套中较松的时序，从 5200 起步并跑 MemTest（调法见完整版附录 C） |
| P2P 始终起不来 | 临时改用 TP2×PP2 或 TP2×DP2；同时回到完整版重新评估平台 |

---

## 参考

| ID | 来源 |
|---|---|
| [N03] | QWEN-PEDIA Qwen3.8-Flash-Next r10 配方 |
| [N06] | NVIDIA NCCL 环境变量文档 |
| [N08] | vLLM P2P 检查 RFC |
| [N10] | ASUS Z790-A D4 规格 |
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

[N03]: https://github.com/abtraore/QWEN-PEDIA/blob/main/recipes/qwen3.8-flash-next/README.md
[N06]: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
[N08]: https://github.com/vllm-project/vllm/issues/51513
[N10]: https://rog.asus.com/us/motherboards/rog-strix/rog-strix-z790-a-gaming-wifi-d4-model/spec/
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

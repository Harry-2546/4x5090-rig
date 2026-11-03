# 4×5090 + PEX88096 计划执行核查（对 v1.9）

核查时间：2026-10-31 20:25 EDT（远端 `rig-host` UTC 11-01 00:24，主机 `up 3h04`，boot 21:20:50）
对象：`5090-4gpu-pex88096-plan-lite-v1.9.md` §4 Gate
方法：SSH 只读实测（lspci / sysfs / nvidia-smi / docker / journalctl / vmstat / cgroup），全部数字为本次实测，未采信任何记忆值。

---

## 0. 结论一句话

**G1、G2、G4 通过并有实测支撑；G3 你主动跳过（合理）；G5（P2P on/off A/B）、G6（1h 满载 + 24h + 测温）没做；G1 的"冷启动 10 次"实际只有 7 次。**
新发现一个计划里没有的风险：**PLE 表（67.6GB shmem）没有被 pin，容器已有 9.7GB 被换进 swap**（§3.1）。

---

## 1. Gate 对照

| Gate | 计划要求 | 本次实测证据 | 判定 |
|---|---|---|---|
| **G1 链路** | 上行 + 4 下行 LnkCap/LnkSta 16GT/s ×16；BAR1 32GiB×4；AER 1h 不增；**冷启动 10 次全识别** | sysfs：`02:1c.0`（CPU 槽）、`03:00.0`、`04:10.0`、`06/07:00.0`、`07:10.0`、`0a/0b:00.0` 全部 `current=16.0 GT/s width=16`；4 张 GPU `current 16.0 GT/s ×16`（`max=32 GT/s`=Gen5 卡，按设计跑 Gen4）；**负载下**（我这条请求 10,052 tok/s prefill）`nvidia-smi --query-gpu=pcie.link.gen.current,width.current` = 4 / 16 四张全中；BAR1 Region1 = **32G** 每张；AER `aer_dev_correctable`+`aer_dev_fatal` 全 0（switch 与 4 卡） | ✅ 链路/BAR/AER 通过<br>⚠️ **冷启动次数 7/10**（见 §2） |
| **G2 P2P** | 卡对只允许 PIX/PXB，不能 PHB/NODE/SYS；单向 ≥24、双向 ≥45 GB/s；PEX 所有 function ACSCtl 的 ReqRedir/CmpltRedir/EgressCtrl 为 `-` | `topo -m`：GPU1↔GPU2 = **PIX**，其余卡对 = **PXB**，无 PHB/NODE/SYS → 全部流量不出 switch；`topo -p2p r` = 12 对全 **OK**；`sudo lspci -vvv`：**04:10.0 / 07:00.0 / 07:10.0 / 0b:00.0 / 0b:10.0 / 0f:14.0 / 0f:15.0 的 ACSCtl 全 `-`**（ACSCap 全 `+`，说明是被关掉而不是不支持）；带宽：你 10-30 记录 12 对单向 28.57、双向 56.5 GB/s → 满足 ≥24/≥45 | ✅ 通过（带宽项沿用我的 10-30 记录；本次无法复测，见 §4） |
| **G3 NCCL** | `all_reduce_perf` 1GB busbw ≥15 GB/s | v1.9 §4.1 已写明"G3 跳过（最小化测试，直接用 r10 验证）"；实测 r10 steps/s 114–117、每卡每向 PCIe 约 1.3GB/s（我的 1244 行数据）→ allreduce 不是瓶颈 | ⏭️ 主动豁免，有替代证据 |
| **G4 应用** | ≥r10 基线 90%：≥95 steps/s、decode ≥290、prefill ≥7,000；无 OOM；`vmstat` si/so≈0 | steps/s：live 日志 116.2（`Avg generation throughput` 与 ab/coreper 一致）vs 作者 105.7–106 = **110%** ✅；prefill 12,554–12,673 tok/s（10-30 记录）✅；decode 随 prompt/接受率 247–403，code 类 ≥290，prose/zh 在 250–300 波动 —— **按你自己定的口径（比较性能看 steps/s）算通过**；OOMKill=false，`journald -p err -b 0` 无 vLLM 相关错误；`vmstat 1 3` 后两行 si=0 so=0 ✅ | ✅ 通过（decode 的绝对值受接受率支配，不是硬件项） |
| **G5 A/B** | `NCCL_P2P_DISABLE=1` + 关 custom AR 重跑 G4，记录差值 | 远端 `~/bench/ab-*.log` 全是 **YaRN A/B**（A-native / B1 / B2），不是 P2P A/B；v1.9 §4.1 自己也列在未做清单 | ❌ **未做** |
| **G6 稳定性** | §2.4 有人值守 1h 满载 → 24h 服务压测；无 Xid 无掉卡；PDU ≤24A；红外测温 5 个接头 | 本次 boot：`up 3h04`，`sudo dmesg | grep -ci xid` = **0**，AER = **0**；上一 boot（15:42→21:16，5h34）末尾有 Xid 109/175/154（`core300-xid.txt`，核心 +300 超频触发，已回退 0）；测温/PDU 只有你 10-30 的几分钟短时读数（峰值 1.86kW / 7.6A / 34–40°C） | ⏳ **进行中**（3h/24h，且需换 boot 才干净） |

---

## 2. G1 冷启动：7/18 boot 是 4 卡形态

`journalctl --list-boots` 18 次，逐次数 `nvidia-drm Loading driver`：

```
b-0 Oct31 21:20  4      b-6 Oct30 01:56  4      b-12 Oct29 22:52  1
b-1 Oct31 15:42  4      b-7 Oct30 01:35  2      b-13 Oct29 03:08  1
b-2 Oct30 05:26  4      b-8 Oct30 01:19  2      b-14/15/16        0
b-3 Oct30 05:23  8(双计) b-9 Oct30 00:29  2      b-17              0
b-4 Oct30 02:03  4      b-10 Oct29 23:35 2
b-5 Oct30 02:00  4      b-11 Oct29 23:19 1
```

- **装好 4 卡之后：7 次 boot，7 次全部 4/4 识别，0 次掉卡。** 其中 `last -x` 显示前面都伴随 `shutdown system down` → 是真断电重启，不是单纯 `reboot`。
- b-7/-8/-9（2 卡）是装第 3、4 张卡之前的状态，b-10 以后（1–2 卡）是装机前，不计。
- 计划要 10 次 → **还差 3 次**。零成本，`sudo reboot` ×3 + 每次确认 `nvidia-smi -L | wc -l` 即可（要真"冷"就断电 30 秒再上电）。

---

## 3. 新发现（计划里没有的）

### 3.1 ⚠️ PLE 表没有 pin，9.7GB 已经在 swap 里

| 证据 | 值 |
|---|---|
| vLLM 日志 | `ngram_embedding.py:720 Initialized PLE embedding ... weight_device=cpu, pinned=True` |
| 实际是否 pin | **没有**：4 个 worker `VmPin = 0 kB`；全机 `Mlocked = 27 MB`、`Unevictable = 37 MB` |
| 表在哪 | `Shmem = 67.6 GB`（`IpcMode=host`，4 个 worker 共享一份 → 省了 3×48GB，设计是对的），`/dev/shm` 只有 30MB → 是 memfd/SysV 段，**可换出** |
| 已换出 | 容器 cgroup `memory.swap.current = 9.73 GB`；worker `VmSwap` ≈ 1.0GB ×4 + 1.26 + 0.26；`swapon --show`：`/swap.img 7.7G used`、`/swapfile32 1.4G used` |
| 当前是否痛 | 不痛：`vmstat` si/so = 0，steps/s 116 正常 —— 因为换出去的是冷页 |
| 风险 | `vm.swappiness = 60`、容器 `MemorySwap=0`（=不限）→ 被换出的可能是 PLE 热区。PLE 查找在每步 decode 都要访问，一旦命中 swap 就是毫秒级抖动，且不会报 Xid，只会表现为"偶发某步特别慢"，很难归因 |

计划里"mlock 无限"这一项：ulimit 确实已给（`Ulimits=[memlock=-1:-1]` ✅），但**没有任何东西去 mlock 那张表**，所以这项目前是空的。

可选处理（都未执行，等我决定）：
1. 温和：`vm.swappiness=10`（sysctl，立即生效，不改架构）。
2. 定向：给容器加 `--memory-swap` 硬限或 cgroup `memory.swap.max=0`（需要重建容器，代价 = 一次 4.5 分钟启动）。
3. 一次性把已换出的吸回来：空闲窗口 `sudo swapoff -a && sudo swapon -a`（当前 `MemAvailable = 46GB`，够装回 9.5GB，安全）。
4. 根治：让 PLE 段 `mlock`（要改 r10/overlay 代码，不划算）。

我的建议：先做 1 + 3，观察 24h（正好并入 G6）；2 留到必须重启容器时顺手加。

### 3.2 ACS 是关掉的，但方式和 v1.9 文档写的不一样

文档写 `pex-acs-off.service` + `/usr/local/sbin/pex-acs-off.sh`；机器上**没有这个 unit**（`systemctl list-unit-files` 无 pex-\*）。实际走的是内核参数：

```
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu=pt pcie_aspm=off pci=disable_acs_redir=pci:1000:c010,realloc=off pci=nocrs"
```

实测结果是对的（ACSCtl 全 `-`）。**建议把 v1.9 §3 第 4 步的 ACS 小节改成"用 cmdline `disable_acs_redir`，不需要 service"**，否则下次照文档排查会找不到东西。
存在的 unit：`gpu-rebar`（active ✅，这就是 4×32G BAR1 的来源）、`gpu-memoc`（active ✅，显存 +4000 持久化）、`gpu-manager`（enabled）、`nvidia-cdi-refresh`（v1.9 的 Ordering 补丁生效：驱动在 rebar 之后加载，BAR 没被重置回 256M）。

### 3.3 超频回退已落实

`coreper.log` 尾部：`offsets 50/190/145/205` 时 steps/s 冲到 144.7 但脚本 `STOP rc=1`；随后 `reset core offset 0`，`GPU0-3 gpc offset 0, mem offset 4000`。当前实测：4 张卡 `clocks_throttle_reasons.active = 0x0`，SM 2895–3052MHz，显存 15801MHz，功耗 170–214W（idle），功率上限 600W，本 boot Xid=0 → 与 v1.9"决定：不超频"一致 ✅

### 3.4 小项

- `systemctl get-default` = `graphical.target`，但没装任何 DM/X（`gdm/sddm/lightdm` 全无，`xserver-xorg-core` 未安装，无 Xorg 进程）→"无桌面"实质满足；要干净就 `sudo systemctl set-default multi-user.target`。
- 网口已按 MAC 匹配（`enp22s0` UP，192.168.1.OBFUSCATED/24，metric 100）→ v1.9 记的 netplan 修复生效 ✅
- 空口状态：`0b:10.0` = 2.5GT/s width 0（E 口那一对没接线）→ 与"还没做：E 口、转接板 5、线 9/10 单独测试"一致。
- 启动期错误日志只有 HID/PAM/agetty 噪声，无 PCIe、无 DMAR、无 NVRM 错误。
- v1.9 自己列的待撤销项仍未做：`/etc/sudoers.d/90-USER-nopasswd` **还在**（我这次核查就是靠它跑 `sudo lspci`）。

---

## 4. 本次没能复测的项，以及怎么复测

`nvbandwidth` 现在跑不了：vLLM 把显存吃到每卡只剩 **473–729 MiB**，`cudaSetDevice(1)` 直接 `out of memory`。要复测 G2 带宽必须先停服务（约 4.5 分钟冷启动）：

```bash
sudo docker stop fnext-vllm && cd ~/nvidia/nvbandwidth/build && \
  ./nvbandwidth -t device_to_device_memcpy_read_ce device_to_device_bidirectional_memcpy_read_ce ; \
  sudo dmesg | grep -iE "xid|aer" ; sudo docker start fnext-vllm
# 期望：单向每对约 28.5 GB/s，双向约 56.5 GB/s
```

顺带能把 **G5** 和 **G3** 一起补掉（G5 需要同一份 prompt 跑两轮；G3 需要 nccl-tests，容器里可能已有 `all_reduce_perf`）。

---

## 5. 剩余清单（按代价排序）

| 项 | 代价 | 说明 |
|---|---|---|
| G1 冷启动再 3 次 | 15 分钟 | 每次断电 30s → 上电 → `nvidia-smi -L` |
| swappiness=10 + swap 吸回 | 1 分钟（需空闲窗口） | §3.1 |
| G5 P2P on/off A/B | 需停服务 2 次 | 一次带 P2P、一次 `NCCL_P2P_DISABLE=1` 且关 custom AR |
| G3 `all_reduce_perf` | 与 G5 同一窗口 | 1GB busbw 记录即可 |
| G2 带宽复测 | 与上同窗口 | 现有数据是 10-30 的，够用作通过依据 |
| G6 24h + 1h 满载 + 红外测温 5 点 | 1 天 + 人在场 | 当前 boot 已 3h，Xid 0 |
| E 口 / 转接板5 / 线 9、10 单测 | 需拆机挪线 |  spare 件验证 |
| 撤销免密 sudo | 10 秒 | 部署真结束后 |

---

*核查人：my agent stack（只读实测，未对远端做任何修改）。数据源：`ssh user@HOSTOBFUSCATED`，2026-10-31 20:25 EDT。*

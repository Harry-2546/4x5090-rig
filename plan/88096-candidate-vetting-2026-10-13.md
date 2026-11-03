# 5090 ×4 PEX88096 — 5 个候选核验（2026-10-13）

配套：[计划](5090-4gpu-pex88096-plan-lite.md) · [Reddit 卖家调研](88096-reddit-sellers-2026-10-13.md)

所有数据来自本次实际打开的页面（eBay / Amazon / AliExpress），非记忆推断。抓取时间 2026-10-13。

---

## 1. 候选对照表

| # | 链接 | 报价 | 页面写明内容 | 卖家 / 渠道 | 保障 |
|---|---|---|---|---|---|
| A | eBay [358723321300](https://www.ebay.com/itm/358723321300) | **$799.88**，运费 $0 | 标题：PLX88096 card + **5×Baseplate + 10×Cable X16** | `xzkjshop1`，注册 **2026-01**，1,012 反馈 99.9%，2.6K 卖出；该品 23 sold / 11 有货 | 卖家写 **No returns**；eBay Money Back Guarantee 仍覆盖"与描述不符"（官方原文：*even if the seller does not offer returns*） |
| B | eBay [127932057763](https://www.ebay.com/itm/127932057763) | **$899.88**，运费 $0 | 标题：PLX88096 card 10×SFF-8654 8i + **10×Baseboard + 10×Cable X8X8** | `zxl-2026`（store `xiaolong1988`），注册 **2016-07**，12,930 反馈 **100%**，101K 卖出；该品 12 sold / 6 有货 | 同上：No returns + eBay MBG |
| C | eBay [407128974102?var=677301812921](https://www.ebay.com/itm/407128974102?var=677301812921) | **$799.98 + $60** 运费（SpeedPAK） | 卖家自己的 listing 图写明 **X16 expansion kit = 8654 wire ×10 + 8654 base plate ×5 + 88096 card ×1**；并有**实物实拍**（见 §7）→ 内容已确定，正好 4 卡 + 1 备用 | `EBL-2377`，注册 2023-05，5,700 反馈 99.8%，19K 卖出，标称 <24h 回复 | No returns + MBG；已有买家反馈因**下拉选项**买错（以为含卡，实际只含线） |
| D | Amazon [B0GGZXVF56](https://www.amazon.com/dp/B0GGZXVF56) | **$659.90**，免运费（10/23 到） | **只有 switch 卡**（Unit Count 1）：PEX88096，**10× SFF-8654 8i** 输出，"motherboard does not require splitting"，模式 **20×4 / 10×8 / 5×16 — "Please contact the seller to set up"** | 第三方 `Hairui Servers Parts`（A3Q155P46REC4Q），7 件剩货 | **30 天 refund/replacement** + Amazon A-to-z（保障最好） |
| E | AliExpress [3256812493065132](https://www.aliexpress.us/item/3256812493065132.html) | **kit-A/B $742.08 / kit-C/D $777.12**；单卖：16x→8654 板内接 $46.08 / 外接 $49.68、8654 线 $25.68；运费 ~$7.47（10/21–29） | 变体只给图，**kit-A/B/C/D 含什么没有文字说明**；描述称 1-to-4 / 1-to-5 full speed | `ADT-Link PCIe Store (Trader)`，但 Specifications 里 **Brand Name = SPEEDIER**（店名≠品牌）；16 sold / 1 rating / 794 有货 | **Free returns within 90 days** + 未送达 35 天退款 ← 五个里唯一有明确退货期 |

补充（同一搜索结果里更便宜、但**不满足 x16 下行**的同类）：
- eBay 358430794487 `card + 6×Baseplate + 6×Cable X8X8` **$459.88** 免运费 → 每 GPU 只有 1 条 8i = **x8**，达不到计划要求的 4×x16。
- eBay 147473131682 `card 5×16`（10×SFF-8654）**$498** 免运费 → 只有卡。
- eBay 137746275254 `External PLX88096 Quad, SFF-8654 → 4×PCI-E X16` **$559.88** → 外置盒形态，和计划的机内分体 kit 不是一回事。

---

## 2. 关键风险 / 红旗

1. **A、B 的 kit 内容与"每卡 2×8654 → x16"是否一致，页面无法证明**（A/B 只有营销合成图，A 的图还带别人家的 `JOY` 水印）。C 已用实拍回答，见 §7。 标题写 `10*Cable X16` vs `10*Cable X8X8` —— 这两种叫法可能对应：(a) 转接板是双 8654、每卡 2 条 8i 线 → 真 x16；(b) 转接板单 8654 → 实际 x8。**这是下单前必须书面确认的第一项**，因为它直接决定 G2（≥24 GB/s）能不能过。
2. **转接板是否自带独立 12V 输入**（计划要求每卡同源供电）—— 5 个页面都没写。
3. **lane 配置是卖家固件预设**：D 明确写"contact the seller to set up 20×4 / 10×8 / 5×16"，E 写 1-to-5 / 1-to-4。→ 下单时必须指定 **1 up x16 + 4 down x16**，否则可能收到 20×4（每口 x4）的版本。Reddit 有人买到 `PEX88096 cut down to only 3 x16`。
4. **E 的品牌不一致**（店名 ADT-Link，规格表 SPEEDIER）+ Reddit 警告 `ADT is known to use non-standard sideband connections. I have had no success mixing any of their products with other brands` → E 只能整套买、不能和别家混。
5. **A 的卖家 2026-01 才注册**（1,012 反馈 / 2.6K 卖出，增长快但不是老店）；其负面反馈 1 条，是别的品（买 2 张网卡抱怨描述不符：`Vorsicht!!!`）。B 的负面计数 ~8 / 12,930；C 的负面计数 ~11 / 5,700。都不算异常，但样本里没有一条是关于 88096 kit 的实质评价 —— **A/B 的该品反馈全是 eBay 自动好评**（"Order delivered on time"），没有技术反馈。
6. **C 的下拉选项陷阱已被买家点名**（买成只含线）。
7. D 的规格表质量差：`Hardware Interface: PCIE x 8`、`Number of Items: 100`、分类 **Parallel Port Cards**、Model `NV9541-4ir`、Manufacturer `hr`、Warranty `2`（单位不明）→ listing 不上心，不能当技术依据。

---

## 3. 价格 vs 计划预算（$575–850 for switch + cables + 4 boards）

| 方案 | 实付 | 相对预算 |
|---|---|---|
| E kit-A/B | $742.08 + $7.47 = **$749.55** | 在区间内 |
| E kit-C/D | **$784.59** | 在区间内（上沿） |
| A（card+5 板+10 线，免运费含关税） | **$799.88** | 在区间内（上沿） |
| C（+ $60 运费） | **$859.98** | 高出上限 $10 |
| B（card+10 板+10 线） | **$899.88** | 高出 $50（多 6 块板 = 浪费） |
| D + E 的板/线自配（659.90 + 4×46.08 + 8×25.68 + 7.47） | **$1,057.13** | 高出 $207，且**违反"同店同批"规则** |

---

## 4. 排序与结论

1. **首选 A（eBay 358723321300，$799.88）** — 唯一"卡 + 5 块板 + 10 条线"一次到位、免运费含关税、数量正好够 4 卡带 1  spare；eBay MBG 兜底（即使卖家写 no returns，与描述不符仍可退）。风险：卖家新（2026-01）、该品无技术反馈 → 必须先拿到 §5 的书面答复。
2. **次选 E（AE kit-C/D $777.12 或 kit-A/B $742.08）** — **90 天免费退货**是五个里最强的试错保障，且能单买板/线补齐；风险：店铺几乎无信誉记录（16 sold / 1 rating）、店名与品牌不一致、kit 内容只有图。**如果 G1/G2 失败要退，只有这家真正退得掉。**
3. **B（$899.88）** — 卖家最可信（2016 年店、12,930 反馈 100%、该品已卖 12 套），若 A 拒绝回答 §5，就用 B；代价是多 $100 且 6 块板用不上。
4. **C（$859.98）** — 只在 A/B 都确认不了内容时才考虑；kit 内容不明 + 有下拉选项事故史。
5. **D（Amazon $659.90）不作为主渠道** — 只有卡，补齐要 ~$1,057 且跨店混买（违反同店原则 + ADT 侧带风险）。价值在于：它的"contact seller to set up 5×16"是五个里唯一把 lane 配置写明白的，可当问话模板。

**无论选哪家，计划的 G1（链路 16GT/s ×16 + 冷启动 10 次全识别）和 G2（P2P PIX 单向 ≥24 GB/s）都不能跳。** Reddit 上至今没有 "Z790 + 88096 kit + 4×5090 全 Gen4 x16 + P2P 成功" 的完整先例，店铺评分不能替代 gate。

---

## 5. 下单前必须拿到的书面答复（直接粘给卖家）

> Before I order a 4-GPU kit, please confirm in writing:
> 1. The switch is pre-configured to **1 upstream x16 + 4 downstream x16** (not 20×4 or 10×8). Please confirm the downstream ports are full x16 and that all 4 are enabled.
> 2. Each GPU baseplate/adapter has **dual SFF-8654 8i inputs** (2 cables per GPU = x16), and **its own 12V power input** — which connector (SATA power / 6-pin / Molex)?
> 3. Cable length and gauge (we need **≤30 cm, 30 AWG**), and whether cards, baseplates and cables in one order come from the **same batch**.
> 4. Please send a photo of the **DIP switch setting** on the baseplate you ship, and an **`lspci -vv` / `lspci -t` output** of this exact kit running 4 GPUs (a real photo of the screen, not the product page table).
> 5. Does the kit work on a **consumer Intel platform (Z790, no PCIe bifurcation in BIOS)**? Any known issue with ReBAR/BAR1 size?
> 6. If the card does not train to 16GT/s x16 on all four ports, what is your replacement/refund process?

对 E 额外问：kit-A / kit-B / kit-C / kit-D 各自**具体含几个卡、几块板、几条线**（文字清单），以及品牌到底是 ADT-Link 还是 SPEEDIER。
对 C 额外问：变体 "X16 Expansion Kit" 的**件数清单**。

---

## 6. 下一步（等我的指示再动）

- 我把 §5 发给哪一家？（默认建议：A 和 E 同时发，谁先给完整书面答复就下单谁。）
- 下单前不动 Z790 平台的任何配置；第 1 步零成本验证（Z790 插 4×32GB MemTest、X870E 上现有 2×5090 跑 p2pBandwidthLatencyTest + vLLM TP2）仍未执行。

---

## 7. EBL-2377 实拍图判读（补充，2026-10-13）

来自 EBL-2377 自己 listing 的照片（泡沫垫上实拍 + 带 `EBL-2377` 水印，即卖家自有库存照片）。对比：A（358723321300）用的是营销合成图，且带别人家的 `JOY` 水印 → **就"图是原图、能当证据"这一点，EBL 明显更实。**

### 7.1 转接板（base plate）

| 读到的 | 值 |
|---|---|
| 型号贴纸 | `Model No: RBS-1664-2P54` / `P/N: 97.R246V11` / `S/N: YIR260714011889` / `Made in China` |
| 丝印 | `RBS1662M5-V130`、`PCIE1`、`BP1`、`BP2`、`1V8`、`GPU`、CE、`PASS` QC 贴 |
| SFF-8654 输入 | **2 个**（丝印 `1`、`2`）→ 每卡 2 条 8i = **真 x16** ✅ |
| PCIe 侧 | 全尺寸 **x16 女槽**（GPU 直接插板上），板 3 个安装孔 → 装在机箱槽位，替代母板槽 |
| 供电 | **独立电源座存在** ✅：左侧白色 4-pin 座（丝印 `BP1`）+ 右边缘一个**直角多 pin 电源座**（丝印 `GPU`/`1V8` 附近）→ 满足"每卡同源 12V"的前提；**接口线型（SATA/Molex/小 4-pin）仍需卖家确认** |
| 日期码 | S/N 前缀 `2607` → 约 **2026-07 生产**，新料不是拆机 |

→ §2 的第 1、2 条红旗，对 C 已经**基本消掉**。

### 7.2 switch 卡（88096 card）

| 读到的 | 值 |
|---|---|
| 板名 | 丝印 `ME164V1` |
| 芯片/散热 | PEX88096 + 铝散热片 + **离心小风扇**（有热和噪音问题要处理） |
| 上行 | 金手指 **x16**（带分段缺口） |
| 下行 | **10 个 SFF-8654 8i**，丝印分组 `A1/A2 B1/B2 C1/C2 D1/D2 E1/E2` = **5 对 = 5×x16** 或 10×x8 → 与 Amazon 那张"20×4 / 10×8 / 5×16"的说明一致；4 卡只用 4 对 |
| 配置方式 | 板左下角有 **焊盘/跳线阵列，丝印 `FS1`、`F13 F12 F11 F10`、`F9 F8 F7 F6`、`F1 CN1`、`ON/OFF`、`24X4/12V`** → lane fan-out **可在板上设** |

⚠️ 这正是 Reddit 警告的点：`有人遇到"板上 DIP 表与实际行为不符"`。丝印表不等于实际固件行为 → **必须让卖家拍"这块卡已设为 1×16 up + 4×16 down"的实物近照 + 该机 `lspci -tv` / `lspci -vv` 截图**，不接受产品页表格。

---

## 8. 修订后的排序（v2）

| 排名 | 候选 | 价格 | 理由 |
|---|---|---|---|
| **1** | **C** eBay 407128974102 var=X16 Expansion Kit | **$859.98**（含 $60 运费、已含关税） | 内容已由卖家自己的图确定（卡 + 5 板 + 10 线）；**双 8654 板 + 独立电源座**由实拍证实；有自有库存实拍 + 型号/S/N 贴纸；卖家 5,700 反馈 99.8%、标称 <24h 回复、该品 5 sold、负面 ~11/5,700 |
| **2** | **E** AliExpress kit-A/B 或 kit-C/D | **$749.55 / $784.59** | 便宜 ~$80–110，且 **90 天免费退货**（唯一真退得掉的）；风险：店几乎无信誉（16 sold / 1 rating）、店名 ADT-Link 与规格 Brand=SPEEDIER 不一致、**kit 内容无文字** |
| **3** | **A** eBay 358723321300 | $799.88 | 价格/数量合适、免运费含关税，但只有带水印的营销图，内容全靠标题；卖家 2026-01 注册 |
| **4** | **B** eBay 127932057763 | $899.88 | 卖家最可信（2016 店 / 12,930 反馈 100% / 该品 12 sold），但要为用不上的 6 块板付钱 |
| **5** | **D** Amazon B0GGZXVF56 | $659.90 | 只有卡，补齐 ~$1,057 且跨店混买 → 违反同店同批 + ADT 侧带风险 |

**买法建议（两套并行，按 Gate 结果留一套）：**
- 主力 **C**（$859.98）：证据最全、卖家响应快。
- 若想要退货权 → 同时考虑 **E**（$749.55，90 天可退），但要先拿到 kit 内容的文字清单。
- 预算上限按计划 $850，C 高 $10 —— 属于可接受范围（且免关税、含 5 块板）。

## 9. 下一步（v2）

1. 向 C（EBL-2377）发 §5 的 6 条，**外加 3 条**：
   - `F1–F13 / FS1` 该 kit 出厂的实际拨位，并拍实物近照；
   - 转接板 `BP1` 电源座配什么线（SATA？Molex？小 4-pin？给照片）；
   - 线缆长度与 AWG（要 ≤30 cm / 30 AWG），以及 10 条线是否同批。
2. 问 E 要 kit-A/B/C/D 的文字件数清单 + 品牌到底是 ADT-Link 还是 SPEEDIER。
3. 两家都回完再决定下单；G1/G2 仍是硬 gate，不过就退（E 有 90 天退货兜底）。

---

*Changelog — v2 (Harry): 依据 EBL-2377 实拍图确认 kit 内容与转接板规格（RBS-1664-2P54，双 SFF-8654，独立电源座）；C 由备选上调为首选；新增 §7 实拍判读、§8 修订排序、§9 下一步。*

*— Harry*


# 4×RTX 5090 on a Consumer Intel Board

> ▶ **Live demo** (terminal replay of the build): https://harry-2546.github.io/4x5090-rig/ — PEX88096 Build & Post-Mortem

A complete, dated engineering record of building a **4×RTX 5090 (128 GB VRAM) LLM inference rig** on an ASUS ROG STRIX **Z690-A** (Intel consumer platform) with a Broadcom **PEX88096** PCIe switch — a combination the public record said was uncharted (every documented 88096 success I could find was AM5 / EPYC / Threadripper).

This repo is written as a **journey, not a highlight reel**: every revision of the plan is kept, and the 16 measurements we got wrong along the way are listed with their corrections.

## Why this exists

- 3 of 4 GPUs would not POST. Root cause: the BIOS reserves a **256 GB 64-bit MMIO window**; each 5090 consumes ~64 GB of it (32 GiB BAR1 × 32 GB alignment + BAR3). Solution: BIOS Re-Size BAR off + `pci=nocrs` + a boot service that reprograms each card's BAR1 to 32 GiB via `setpci` and re-enumerates the switch tree before the driver loads.
- P2P over the switch measured **28.6 GB/s per pair unidirectional / 56.5 bidirectional** (copy engine), 4/4 links Gen4 ×16, Xid/AER/DMAR zero.
- Serving [Qwen3.8-Flash-Next NVFP4 (QWEN-PEDIA r10)](https://github.com/abtraore/QWEN-PEDIA) on vLLM TP4+EP: **116 steps/s vs the author's 106 baseline**, ~1,200 tok/s at 8-way concurrency. Full benchmark methodology lives in the companion repo [`llm-inference-bench`](https://github.com/Harry-2546/llm-inference-bench).

## Contents

| Path | What it is |
|---|---|
| `plan/pc2-4x5090-journey-*.md` | The narrative: what we hit, what we did, what the numbers were, what we said wrong and fixed (828 lines, dated) |
| `plan/5090-4gpu-pex88096-plan-lite-v*.md` | Full revision history of the implementation plan, v1.0 → v1.9 (10 versions; every superseded claim kept) |
| `plan/88096-candidate-vetting-*.md`, `88096-reddit-sellers-*.md` | Hardware vetting: seller forensics, DIP settings, PSU/power-tree design ("same-card-same-source" rule) |
| `research/report.md` | Companion survey: **1,096 deduped sources** (GitHub/Reddit/HF) on what 128 GB of Blackwell can run — methodology stated, gaps marked as gaps |
| `scripts/` | `gpu-rebar` (the BAR fix), `gpu-memoc` (VRAM offset), `pex-acs-off`, cdi-refresh ordering drop-in |
| `demo/` | Interactive HTML visual explainer of the topology and numbers |

## The honest part

A full table of *our own wrong conclusions and how measurement killed them* is in the journey doc (`plan/pc2-4x5090-journey-*.md`, §"errors and corrections"): a bottleneck attribution we revised twice, a YaRN configuration that had silently never been active, benchmark scores whose test order created the effect, and headline numbers whose composition we had to decompose before trusting. We keep them in because a build log without its corrections is advertising.

## Safety notes

The electrical section (`plan/...v1.9.md` §2.2–2.5: 240 V via NEMA 10-30, PDU, synchronized multi-PSU start, and its **known risks and accepted tradeoffs**) is reproduced verbatim with its warnings. It documents *our* installation; it is not advice for yours.

*Hostnames, IPs, MACs and local usernames are redacted in this public copy.*

— Harry · built Oct 6 – Nov 3, 2026 · rig running continuously since

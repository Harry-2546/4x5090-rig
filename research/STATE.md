# 4x5090 (128GB VRAM) deep research — STATE

## Mission
What can 4x RTX 5090 (4x32GB=128GB VRAM, PEX88096 island, single box) run, and which models are best?
Angles: LLM serving (vLLM/SGLang/TensorRT-LLM/llama.cpp/Strata/ExLlama), quants (NVFP4/FP8/int),
model classes that fit 128GB (MoE 100-600B, dense 70B, long-context), image/video/audio gen,
multi-instance configs, measured tok/s, TP4/EP recipes, known 5090/SM120 pitfalls.

## Completion contract (Harry)
>=500 independent sources cross-verified; EVERY conclusion has a link; full report written.
Source = distinct URL (repo/thread/model card/PR/issue/discussion); dedupe by URL in sources.jsonl.

## Layout
- sources.jsonl   one JSON per line: {id,url,type,topic,date,title,claim,quality}
- findings.md     distilled conclusions per topic, each cited [Sxxx]
- report.md       final deliverable (only assemble at the end)
- harvest_github.py  GitHub repo+code+issue search harvester (run: python harvest_github.py "q1" "q2" ...)

## Status
round 1: DONE (GitHub x3 batches, Reddit x2 rounds)
sources so far: 938 — TARGET MET (gh 683 / reddit 215 / hf 140; comments/ has 5 archived comment trees) (265 gh + 81 reddit)
keyword queue (initial): see harvest queries in git log of this file; derive new keywords from findings.md gaps each round.

## Round-2 keyword queue (derived from round-1 vocabulary)
DIRECT-CONFIG (missing, must find or mark GAP): "qwen3.5-397b 4x5090", "deepseek v4.1 flash 4 gpu", "glm 5.3 flash 4x5090", "vllm tp4 5090 deepseek", "sglang ep 5090"
MODEL FIT (verify sizes on HF model cards): qwen3.5-397b GGUF size ladder, glm-5.3-flash quant sizes, kimi k3, minimax, lfm2.5
OTHER-WORKLOAD: flux.2 4gpu, video generation multi-gpu, fine-tuning 70B 4x5090 (qlora/fp8), lora team serving, embedding+rerank fleet, ASR fleet
COMMUNITY: comment trees of top threads (1wuvbe5 team-of-50 build, 1rtrdsv 282t/s, 1rrfqlu SM120 bakeoff, 1x99oeu Oct survey, 1vlurlv 8x5090 quant bench, 1s32orn 397B single-5090)
GITHUB round-2: sglang+5090, deepseek-v4+4gpu, qwen3.5+397b, flux+4gpu, fine-tune+4x5090

## Round-4 DONE (YaRN/community round): 1074 sources, 8 comment trees, findings C13-C14, report sections 8-9 added.
Contract stays met. Idle unless new topic.

Round-5 DONE (subagent concurrency): 1137 sources, 11 trees, finding C15.

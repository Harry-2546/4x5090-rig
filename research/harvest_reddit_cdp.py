"""Reddit harvester over the logged-in mirror Chrome CDP (read-only fetch in page).
Modes:
  search q1 q2 ...        -> search.json per query, append sources.jsonl (dedup), compact stdout
  thread <permalink> ...  -> full comment tree saved to comments/<id>.json, digest of numeric lines to stdout
"""
import asyncio, json, os, re, sys, urllib.request
import websockets

R = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(R, 'sources.jsonl')
CDOM = 'http://127.0.0.1:9222'

def page_ws():
    tabs = json.loads(urllib.request.urlopen(CDOM + '/json', timeout=10).read().decode())
    for t in tabs:
        if t.get('type') == 'page' and 'reddit.com' in (t.get('url') or ''):
            return t['webSocketDebuggerUrl']
    raise SystemExit('no reddit tab open on 9222')

def load_ids():
    ids = set()
    if os.path.exists(SRC):
        for l in open(SRC, encoding='utf-8'):
            try: ids.add(json.loads(l)['url'])
            except: pass
    n = max((int(json.loads(l)['id'][1:]) for l in open(SRC, encoding='utf-8') if l.strip()), default=0)
    return ids, n

KEEP = ['LocalLLaMA','LocalLLM','LocalAI','LocalAIStack','Vllm','StableDiffusion','ComfyUI','unsloth',
        'Qwen','DeepSeek','r14','local_llama','singularity','LocalAIServers','hermesagent','ollabla','huggingface']

async def evaluate(ws, expr, mid=[0]):
    mid[0] += 1
    await ws.send(json.dumps({'id': mid[0], 'method': 'Runtime.evaluate',
        'params': {'expression': expr, 'awaitPromise': True, 'returnByValue': True,
                   'timeout': 240000}}))
    while True:
        msg = json.loads(await asyncio.wait_for(ws.recv(), 300))
        if msg.get('id') == mid[0]:
            r = msg.get('result', {})
            if 'exceptionDetails' in r: raise RuntimeError(str(r['exceptionDetails'])[:300])
            return r.get('result', {}).get('value')

async def main():
    mode = sys.argv[1]
    ws = await websockets.connect(page_ws(), max_size=60_000_000)
    if mode == 'search':
        qs = sys.argv[2:]
        ids, n = load_ids()
        for q in qs:
            expr = (f"(async()=>{{const r=await fetch(`https://www.reddit.com/search.json?q={q}&sort=relevance&t=all&limit=25&raw_json=1`,"
                    "  {headers:{accept:'application/json'}});const j=await r.json();"
                    "return (j.data&&j.data.children||[]).map(c=>({t:c.data.title,sub:c.data.subreddit,"
                    "u:c.data.permalink,s:c.data.score,c:c.data.num_comments,d:new Date(c.data.created_utc*1000).toISOString().slice(0,10)}));})()")
            try:
                items = await evaluate(ws, expr) or []
            except Exception as e:
                print('ERR', q, e); await asyncio.sleep(5); continue
            added = 0
            with open(SRC, 'a', encoding='utf-8') as f:
                for it in items:
                    if not (it.get('sub') and any(k in it['sub'] for k in KEEP)): continue
                    u = 'https://www.reddit.com' + it['u']
                    if u in ids: continue
                    ids.add(u); n += 1; added += 1
                    f.write(json.dumps({'id': f'S{n:04d}', 'url': u, 'type': 'reddit-post', 'date': it['d'],
                        'topic': 'reddit-r3', 'title': (it['t'] or '')[:120], 'claim': (it['t'] or '')[:120],
                        'quality': f"{it['sub']} {it['s']}up/{it['c']}c"}, ensure_ascii=False) + '\n')
            print(f'q={q} hits={len(items)} added={added} total={len(ids)}')
            await asyncio.sleep(3)
    elif mode == 'thread':
        os.makedirs(os.path.join(R, 'comments'), exist_ok=True)
        for perm in sys.argv[2:]:
            pid = perm.rstrip('/').split('/')[-1]
            p2 = perm.rstrip('/') + '.json'
            expr = (f"(async()=>{{const r=await fetch(`https://www.reddit.com{p2}?raw_json=1&limit=500`,"
                    "  {headers:{accept:'application/json'}});const j=await r.json();"
                    "const out=[];const walk=(arr,depth)=>{for(const c of arr||[]){if(c.kind!=='t1')continue;"
                    "const d=c.data;out.push({d:depth,b:(d.body||'').slice(0,3000),s:d.score});walk(d.replies&&d.replies.data&&d.replies.data.children,depth+1);}};"
                    "walk(j[1]&&j[1].data&&j[1].data.children,0);return out;})()")
            try:
                comments = await evaluate(ws, expr) or []
            except Exception as e:
                print('ERR', perm, e); await asyncio.sleep(5); continue
            with open(os.path.join(R, 'comments', pid + '.json'), 'w', encoding='utf-8') as f:
                json.dump(comments, f, ensure_ascii=False)
            # digest: lines that contain performance numbers / model names
            pat = re.compile(r'\b(tok(?:en)?s?/s|t/s|pp/s|tgs|pps|GB|VRAM|5090|PRO 6000|NVFP4|nvfp4|FP8|MTP|spec|TP\d|EP|prefill|decode|Q[2-6]|GGUF)\b', re.I)
            hits = [c for c in comments if pat.search(c['b']) and c['s'] >= 2]
            print(f'== {perm} comments={len(comments)} numeric_hits={len(hits)}')
            for c in hits[:14]:
                line = re.sub(r'\s+', ' ', c['b'])[:220]
                print(f"  [{c['s']}] {line}")
            await asyncio.sleep(3)
    await ws.close()

asyncio.run(main())

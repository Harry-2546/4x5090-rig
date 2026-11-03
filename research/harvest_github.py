import sys, json, os, time, urllib.request

R = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(R, 'sources.jsonl')

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'hermes-agent','Accept':'application/vnd.github+json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

def load_ids():
    ids=set()
    if os.path.exists(SRC):
        for l in open(SRC,encoding='utf-8'):
            try: ids.add(json.loads(l)['url'])
            except: pass
    return ids

def main():
    ids = load_ids(); n=0
    with open(SRC,'a',encoding='utf-8') as f:
        for q in sys.argv[1:]:
            try:
                d = get(f'https://api.github.com/search/repositories?q={q}&per_page=20&sort=updated')
                for r in d['items']:
                    u=r['html_url']
                    if u in ids: continue
                    ids.add(u); n+=1
                    f.write(json.dumps({'id':f'S{n:04d}','url':u,'type':'gh-repo','date':r['pushed_at'][:10],
                        'title':r['full_name'],'claim':(r.get('description') or '')[:300],
                        'quality':f"*{r['stargazers_count']}",'topic':q},ensure_ascii=False)+'\n')
            except Exception as e: print('REPO ERR',q,e)
            time.sleep(3)
            try:
                d = get(f'https://api.github.com/search/issues?q={q}&per_page=20&sort=updated')
                for r in d['items']:
                    u=r['html_url']
                    if u in ids: continue
                    ids.add(u); n+=1
                    f.write(json.dumps({'id':f'S{n:04d}','url':u,'type':'gh-issue','date':r['updated_at'][:10],
                        'title':r['title'][:150],'claim':(r.get('body') or '')[:200].replace('\n',' '),
                        'quality':f"comments={r['comments']}",'topic':q},ensure_ascii=False)+'\n')
            except Exception as e: print('ISSUE ERR',q,e)
            time.sleep(3)
    print('added',n,'total',len(ids))

main()

#!/usr/bin/env python3
"""Save full public WordPress writings to data/*.json for an offline GitHub Pages archive.
Run: python3 -m pip install requests beautifulsoup4
     python3 scripts/snapshot.py
"""
import json,re,sys,time
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
BASE=Path(__file__).resolve().parents[1]
posts=json.loads((BASE/'posts.json').read_text())
s=requests.Session();s.headers.update({'User-Agent':'ShayaraPersonalArchive/1.0 (+personal content backup)'})

def extract(post):
    slug=post['slug']
    candidates=[f'https://thecomearound.wordpress.com/wp-json/wp/v2/posts?slug={slug}&_embed=1', f'https://public-api.wordpress.com/rest/v1.1/sites/thecomearound.wordpress.com/posts/slug:{slug}']
    for i,url in enumerate(candidates):
        try:
            r=s.get(url,timeout=30);r.raise_for_status();d=r.json()
            if i==0:
                x=d[0] if isinstance(d,list) and d else None
                if not x or not x.get('content',{}).get('rendered'):continue
                media=x.get('_embedded',{}).get('wp:featuredmedia',[])
                return {'title':BeautifulSoup(x['title']['rendered'],'html.parser').get_text(' ',strip=True),'date':post['date'],'content':x['content']['rendered'],'image':media[0].get('source_url') if media else None,'source':post['url']}
            if isinstance(d,dict) and d.get('content'):
                return {'title':d.get('title',post['title']),'date':post['date'],'content':d['content'],'image':d.get('featured_image'),'source':post['url']}
        except Exception as e:print('API failed:',str(e)[:125])
    # Final option: parse the public HTML as a fallback.
    r=s.get(post['url'],timeout=30);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    node=soup.select_one('.entry-content') or soup.select_one('article .wp-block-post-content') or soup.select_one('main article .post-content')
    if not node:raise RuntimeError('Could not find post body in source HTML')
    for el in node.select('script,style,.sharedaddy,.jp-relatedposts,.post-tags,.wp-block-post-author'):
        el.decompose()
    return {'title':post['title'],'date':post['date'],'content':str(node),'image':None,'source':post['url']}

failed=[]
for p in posts:
    dest=BASE/'data'/f"{p['id']}.json"
    try:
        obj=extract(p)
        # The supplied HTML is preserved when online extraction fails; all others are fetched.
        dest.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        print('SAVED',p['title'],len(obj['content']),'characters')
    except Exception as e:
        failed.append(p['title']);print('FAILED',p['title'],e,file=sys.stderr)
    time.sleep(.25)
print(f'Complete: {len(posts)-len(failed)}/{len(posts)}. Failed: {", ".join(failed) or "none"}')
if failed:sys.exit(1)

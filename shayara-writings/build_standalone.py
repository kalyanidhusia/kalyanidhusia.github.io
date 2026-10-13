#!/usr/bin/env python3
"""Create a standalone, file://-friendly Shayara HTML from posts.json and data/*.json.

Place this file in the shayara-writings directory and run:
    python3 build_standalone.py
Creates standalone.html with all article bodies embedded directly.
"""
from pathlib import Path
import json, re, sys

root = Path(__file__).resolve().parent
index_file = root / 'index.html'
manifest_file = root / 'posts.json'
if not index_file.is_file() or not manifest_file.is_file():
    sys.exit('ERROR: Place build_standalone.py beside index.html and posts.json in shayara-writings.')
posts = json.loads(manifest_file.read_text(encoding='utf-8'))
inline = {}
missing = []
for p in posts:
    path = root / 'data' / (p['id'] + '.json')
    if not path.exists():
        missing.append(str(path))
        continue
    doc = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(doc.get('content'),str) or not doc['content'].strip():
        missing.append(str(path)+' (empty content)')
        continue
    inline[p['id']] = doc
if missing:
    sys.exit('ERROR: Missing content files:\n  ' + '\n  '.join(missing) + '\nRun python3 scripts/snapshot.py first.')

html = index_file.read_text(encoding='utf-8')
if "const BASE='https://thecomearound.wordpress.com';" not in html:
    sys.exit('ERROR: index.html does not match the expected Shayara template.')

# Escape script termination and HTML-special JS separators to safely embed arbitrary content.
def javascript_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')

needle = "const BASE='https://thecomearound.wordpress.com';let posts=[],chosen=null,fontSize=17;"
replacement = needle + '\nconst EMBEDDED_POSTS=' + javascript_json(posts) + ';\nconst EMBEDDED_CONTENT=' + javascript_json(inline) + ';'
html = html.replace(needle,replacement,1)

load_needle = 'async function loadPost(p){'
if load_needle not in html: sys.exit('ERROR: Cannot locate loadPost() in index.html')
html = html.replace(load_needle, 'async function loadPost(p){if(EMBEDDED_CONTENT[p.id])return EMBEDDED_CONTENT[p.id];',1)

init_old = "function init(){fetch('posts.json').then(r=>r.json()).then(d=>{posts=d;drawTabs();navigate(location.hash.slice(1)||posts[0].id)}).catch(()=>{$('content').innerHTML='<div class=\"notice\">Unable to load the archive. Host this directory on GitHub Pages or a local HTTP server, rather than opening index.html as a file.</div>'});}"
init_new = "function init(){posts=EMBEDDED_POSTS;drawTabs();navigate(location.hash.slice(1)||posts[0].id)}"
if init_old not in html: sys.exit('ERROR: Cannot locate init() in index.html')
html = html.replace(init_old,init_new,1)

out = root / 'standalone.html'
out.write_text(html,encoding='utf-8')
print(f'Created {out} ({out.stat().st_size:,} bytes)')
print(f'Embedded {len(inline)}/{len(posts)} writings:')
for p in posts: print('  OK',p['title'],f"({len(inline[p['id']]['content']):,} HTML characters)")
print('Open standalone.html directly, or rename it to index.html for GitHub Pages.')

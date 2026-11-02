#!/usr/bin/env python3
"""Assemble the AI-901 Grand Prix site: wraps src/*.html fragments in the shared shell (topbar, mast, TOC, pager, footer)."""
import json, re, os, html
ROOT=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(ROOT,"src")
SITE={"name":"AI-901 Grand Prix","tag":"Velocity Motors · Microsoft Foundry labs","repo":"https://github.com/varoonsahgal/az901","url":"https://varoonsahgal.github.io/az901/"}
LABS=[
 {"id":"lab0","n":"Lap 0","short":"Pit lane","title":"Pit lane · set up your garage","color":"#94A3B8","time":"30 min","icon":"🏎️","start":"09:00"},
 {"id":"lab1","n":"Lap 1","short":"Race rules","title":"Race rules · AI concepts, models and responsible AI","color":"#EF4444","time":"60 min","icon":"⚖️","start":"09:30"},
 {"id":"lab2","n":"Lap 2","short":"Pole position","title":"Pole position · prompts, playground and your first chat app","color":"#22C55E","time":"60 min","icon":"🎙️","start":"10:45"},
 {"id":"lab3","n":"Lap 3","short":"Pit crew","title":"Pit crew · build and test an agent","color":"#F59E0B","time":"60 min","icon":"🔧","start":"11:45"},
 {"id":"lab4","n":"Lap 4","short":"Radio check","title":"Radio check · text analysis and speech","color":"#38BDF8","time":"60 min","icon":"📻","start":"13:30"},
 {"id":"lab5","n":"Lap 5","short":"Eyes on track","title":"Eyes on the track · vision and image generation","color":"#A78BFA","time":"50 min","icon":"📸","start":"14:30"},
 {"id":"lab6","n":"Lap 6","short":"Paperwork","title":"Paperwork · information extraction with Content Understanding","color":"#14B8A6","time":"50 min","icon":"🗂️","start":"15:30"},
 {"id":"lab7","n":"Lap 7","short":"Checkered flag","title":"Checkered flag · practice exam and cool-down lap","color":"#FACC15","time":"40 min","icon":"🏁","start":"16:20"},
]
EXTRA=[{"id":"instructor","n":"Race control","short":"Instructor","title":"Race control · instructor setup, costs and cleanup","color":"#E10600","time":"","icon":"🎛️","start":""}]
ALL=LABS+EXTRA
LOGO='<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#0B1220"/><path d="M6 10h20M6 16h20M6 22h20" stroke="#fff" stroke-width="1.2" opacity=".25"/><path d="M8 20c2-6 6-9 11-9h5l-3 5H13c-2 0-3 1-5 4z" fill="#E10600"/><circle cx="12" cy="22" r="2.4" fill="#FACC15"/><circle cx="22" cy="22" r="2.4" fill="#FACC15"/></svg>'
FAVICON="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230B1220'/%3E%3Cpath d='M8 20c2-6 6-9 11-9h5l-3 5H13c-2 0-3 1-5 4z' fill='%23E10600'/%3E%3Ccircle cx='12' cy='22' r='2.4' fill='%23FACC15'/%3E%3Ccircle cx='22' cy='22' r='2.4' fill='%23FACC15'/%3E%3C/svg%3E"
def slug(s): return re.sub(r"[^a-z0-9]+","-",re.sub(r"<[^>]+>","",s).lower()).strip("-")
def nav(cur):
    items=['<a href="index.html" class="home"%s>Start here</a>' % (' aria-current="page"' if cur=="index" else "")]
    for l in LABS:
        items.append(f'<a href="{l["id"]}.html" data-lab="{l["id"]}" style="--d:{l["color"]}" title="{html.escape(l["title"])}"{" aria-current=page" if cur==l["id"] else ""}><span class="dot"></span><b>{l["n"]}</b><span class="lbl-long">{l["short"]}</span><span class="done" aria-label="completed">★</span></a>')
    items.append(f'<a href="instructor.html" class="rc"{" aria-current=page" if cur=="instructor" else ""}>🏁 Race control</a>')
    return "\n      ".join(items)
def head(title, desc, page):
    return f'''<!doctype html>
<html lang="en" data-page="{page}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {SITE["name"]}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0B1220">
<meta property="og:title" content="{html.escape(title)} · {SITE["name"]}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="website"><meta property="og:image" content="{SITE["url"]}images/og.png">
<script>try{{var t=localStorage.getItem('ai901-gp:theme');if(t)document.documentElement.setAttribute('data-theme',JSON.parse(t))}}catch(e){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/site.css">
<link rel="icon" href="{FAVICON}">
'''
def topbar(page):
    return f'''<a class="skip" href="#main">Skip to content</a>
<div id="readbar" aria-hidden="true"></div>
<header class="topbar">
<div class="topbar-in">
  <a class="brand" href="index.html">{LOGO}<span class="bn">{SITE["name"]}</span><span class="bt">{SITE["tag"]}</span></a>
  <div class="tools">
    <span class="race-progress" id="race-progress" title="Laps completed in this browser"></span>
    <label class="pitboard" id="pitboard" title="Your student number drives every resource name on this site"><span>Pit board</span><input id="student" type="text" maxlength="3" value="s07" aria-label="Your student number, like s07" placeholder="s07"><em class="nudge" aria-hidden="true">your number</em></label>
    <button class="iconbtn" id="theme" type="button" aria-label="Switch theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z"/></svg></button>
  </div>
</div>
<div class="lapstrip"><nav class="nav" aria-label="Laps">
      {nav(page)}
</nav></div>
</header>
'''
def footer():
    return f'''<footer>
  <div>{SITE["name"]} · a one-day, car-themed path through Microsoft exam AI-901 · built for Velocity Motors (a fictional company). Not affiliated with Microsoft.</div>
  <div><a href="{SITE["repo"]}">Source on GitHub</a> · <a href="https://learn.microsoft.com/credentials/certifications/resources/study-guides/ai-901">Official AI-901 study guide</a> · <a href="instructor.html">Race control</a> · <a href="credits.html">Photo credits</a></div>
</footer>
<script src="assets/site.js"></script>
'''
def lapart(meta, lab):
    """The masthead card on every lap page: lap number, the track strip, what you build, what is next."""
    if not lab or lab["id"] not in [l["id"] for l in LABS]: return meta.get("art","")
    i=[l["id"] for l in LABS].index(lab["id"]); nxt=LABS[i+1] if i+1<len(LABS) else None
    segs="".join(f'<i style="--d:{l["color"]}" class="{"cur" if l["id"]==lab["id"] else ("past" if k<i else "")}" title="{l["n"]} · {l["short"]}"></i>' for k,l in enumerate(LABS))
    build="".join(f'<li>{b}</li>' for b in meta.get("build",[]))
    foot=f'<span>⏱ {lab["time"]}</span>'+(f'<span>Next · {nxt["n"]} {nxt["short"]}</span>' if nxt else '<span>Final lap</span>')
    return f'''<div class="lapart" style="--d:{lab["color"]}">
  <div class="lapart-top"><div class="lapart-num"><small>Lap</small><b>{i}</b><small>of 7</small></div><div class="lapart-ico" aria-hidden="true">{lab["icon"]}</div></div>
  <div class="lapart-name">{lab["short"]}</div>
  <div class="segs" aria-label="Lap {i} of 7">{segs}</div>
  {('<div class="lapart-lbl">You build</div><ul class="build">'+build+'</ul>') if build else ''}
  <div class="lapart-foot">{foot}</div>
</div>'''
def mast(meta, lab):
    chips="".join(f'<span class="chip"><b>{html.escape(k)}</b> {v}</span>' for k,v in meta.get("chips",[]))
    objs="".join(f'<li>{html.escape(o)}</li>' for o in meta.get("objectives",[]))
    art=meta.get("art") or lapart(meta, lab)
    return f'''<section class="mast"><canvas class="mast-fx" aria-hidden="true"></canvas><div class="mast-in">
  <div>
    <p class="eyebrow">{meta.get("eyebrow", (lab["n"]+" of 7 · "+lab["short"]) if lab else "")}</p>
    <h1>{meta["h1"]}</h1>
    <p class="lede">{meta["lede"]}</p>
    <div class="mast-meta">{chips}</div>
    {('<div class="objs"><span class="objs-lbl">🎯 Skills measured in this lap</span><ul>'+objs+'</ul></div>') if objs else ''}
  </div>
  <div class="mast-art">{art}</div>
</div></section>
'''
def toc(body):
    hs=re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(hs)<3: return ""
    def txt(t): return re.sub(r"<[^>]+>","",re.sub(r'<span class="pn">(Part \d+)</span>', r'\1 · ', t))
    return '<details class="toc" open><summary>On this page</summary><ol>'+"".join(f'<li><a href="#{i}">{txt(t)}</a></li>' for i,t in hs)+'</ol></details>\n'
def add_ids(body):
    body=re.sub(r'<h2>(.*?)</h2>', lambda m: f'<h2 id="{slug(m.group(1))}">{m.group(1)}</h2>', body)
    return re.sub(r'(<h2 id="[^"]+">)(Part \d+) · ', r'\1<span class="pn">\2</span>', body)
def pager(idx):
    if idx is None: return ""
    prev=ALL[idx-1] if idx>0 else None; nxt=ALL[idx+1] if idx+1<len(ALL) else None
    a=f'<a href="{prev["id"]}.html"><small>◀ Previous</small>{prev["n"]} · {prev["short"]}</a>' if prev else '<a href="index.html"><small>◀ Back</small>Start here</a>'
    b=f'<a href="{nxt["id"]}.html" style="text-align:right"><small>Next ▶</small>{nxt["n"]} · {nxt["short"]}</a>' if nxt else '<a href="index.html" style="text-align:right"><small>Finish</small>Back to the start</a>'
    return f'<nav class="pager" aria-label="Lap navigation">{a}{b}</nav>'
def build(page):
    src=open(os.path.join(SRC,page+".html")).read()
    m=re.match(r'\s*<!--META\s*(\{.*?\})\s*-->', src, re.S); meta=json.loads(m.group(1)); body=src[m.end():]
    lab=next((l for l in ALL if l["id"]==page), None); idx=ALL.index(lab) if lab else None
    body=add_ids(body)
    hue=f"hue-{page}" if lab else "hue-instructor"
    out=head(meta["title"], meta["desc"], page)+ (meta.get("head","")) + f'</head>\n<body data-page="{page}" class="{hue}">\n'+topbar(page)
    out+=meta.get("mast_html") or mast(meta, lab)
    out+='<main id="main" class="labwrap">\n'+(toc(body) if meta.get("toc",True) else "")+body+pager(idx)+'\n</main>\n'+footer()+'</body>\n</html>\n'
    open(os.path.join(ROOT,page+".html"),"w").write(out); print(f"built {page}.html ({len(out)//1024} KB)")
if __name__=="__main__":
    import sys
    pages=sys.argv[1:] or [f[:-5] for f in sorted(os.listdir(SRC)) if f.endswith(".html")]
    for p in pages: build(p)

#!/usr/bin/env python3
"""把 data/hooks-*.json 渲染成"短剧钩子库"网页 index.html(卡片平铺,含每日题材与钩子统计)。"""
import json, glob
from pathlib import Path
from collections import Counter

B = Path(__file__).parent
days = {}
for f in sorted(glob.glob(str(B / "data/hooks-*.json"))):
    d = json.load(open(f, encoding="utf8"))
    its = d["items"]
    stats = {
        "scanned": d.get("scanned", len(its)), "kept": len(its),
        "route": Counter(i["route"] for i in its).most_common(),
        "hook_type": Counter(t for i in its for t in i["hook_type"].split("/")).most_common(6),
        "genre": Counter(i["genre"] for i in its if i["genre"]).most_common(8),
    }
    days[d["date"]] = {"items": its, "stats": stats}

html = r'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>短剧钩子库</title><style>
body{font-family:-apple-system,"PingFang SC",sans-serif;margin:0;background:#fff;color:#222}
header{background:#fff;color:#1f2937;padding:18px 24px 6px}h1{margin:0;font-size:20px}header p{margin:6px 0 0;opacity:.88;font-size:13px;line-height:1.6}
.bar{display:flex;flex-wrap:wrap;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid #eef0f4;align-items:center;position:sticky;top:0;z-index:2}
select,input{padding:6px 10px;border:1px solid #cfd7e3;border-radius:6px;font-size:14px}
.chip{padding:4px 12px;border-radius:14px;background:#eaf0f8;cursor:pointer;font-size:13px;white-space:nowrap}.chip.on{background:#2E6DB4;color:#fff}
.wrap{max-width:1240px;margin:0 auto;padding:18px 24px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:18px}
.box{background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px #0001}.box h3{margin:0 0 10px;font-size:14px;color:#2E6DB4}
.row{display:flex;align-items:center;gap:8px;font-size:12.5px;margin:5px 0}.row span:first-child{width:118px;flex:none;color:#33405a}
.row i{display:block;height:8px;background:#2E6DB4;border-radius:4px}.row b{font-weight:500;color:#6b7686}
.big{font-size:26px;font-weight:700;color:#1b2a41}.sub{font-size:12px;color:#6b7686;margin-top:4px;line-height:1.6}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(285px,1fr));gap:14px}
.card{background:#fff;border-radius:10px;padding:16px;display:flex;flex-direction:column;gap:9px;border:1px solid #eef0f4;border-top:3px solid #2E6DB4}
.card.c中{border-top-color:#e0a21b}.card.c低{border-top-color:#b8c0cc}
.top{display:flex;justify-content:space-between;font-size:12px;color:#6b7686}
.hook{font-size:17px;line-height:1.55;font-weight:700;color:#1b2a41}
.title{font-size:13px;color:#2E6DB4;font-weight:600}.meta{font-size:12px;color:#8a94a3}
.cf{font-size:13px;color:#3b4658;line-height:1.6}
.tags{display:flex;flex-wrap:wrap;gap:6px}.tag{padding:1px 8px;border-radius:10px;font-size:12px;background:#eaf0f8;color:#2E6DB4}
.高{background:#dff5e3;color:#1b7a36}.中{background:#fff3d6;color:#9a6a00}.低{background:#eee;color:#666}
.hl{font-size:13px;color:#1f2937;line-height:1.6;background:#fafbfc;border-radius:6px;padding:6px 9px}.hl .tag{margin-left:6px}
.v30{font-size:12px;color:#33507a;background:#f1f6fd;border-radius:6px;padding:6px 9px}
.foot{margin-top:auto;font-size:12px;display:flex;justify-content:flex-end}.foot a{color:#2E6DB4;text-decoration:none}
footer{text-align:center;color:#8a94a3;font-size:12px;padding:20px;line-height:1.7}</style></head><body>
<header><h1>短剧钩子库</h1></header>
<div class="bar"><select id="d"></select><input id="q" placeholder="搜索剧名或钩子"><span id="cats"></span></div>
<div class="wrap"><main id="list"></main></div>
<footer>数据来源:红果短剧官网公开榜单。剧名与链接归原平台所有,点击“官网查看”可看原剧。</footer>
<script>const D=__DATA__;let cat="全部";const $=i=>document.getElementById(i);
const ds=Object.keys(D).sort().reverse();$("d").innerHTML=ds.map(x=>`<option>${x}</option>`).join("");
function pl(x){return x.platform=="红果短剧"?"红果短剧":"海外短剧"}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function bars(title,arr){const m=Math.max(...arr.map(a=>a[1]));return `<div class="box"><h3>${title}</h3>`+arr.map(([k,v])=>`<div class="row"><span>${esc(k)}</span><i style="width:${Math.round(v/m*120)}px"></i><b>${v}</b></div>`).join("")+`</div>`}
function draw(){const day=D[$("d").value],it=day.items,st=day.stats,q=$("q").value.trim();
const cs=["全部",...new Set(it.map(x=>x.route))];
$("cats").innerHTML=cs.map(c=>`<span class="chip ${c==cat?"on":""}" onclick="cat='${c}';draw()">${c}</span>`).join(" ");
$("list").innerHTML=it.filter(x=>(cat=="全部"||x.route==cat)&&(!q||x.hook.includes(q)||x.title.includes(q)||(x.title_cn||"").includes(q)||x.highlight.includes(q))).map(x=>
`<div class="card c${x.adapt}"><div class="top"><span>#${x.rank}</span><span class="tag ${x.adapt}">前贴适配度:${x.adapt}</span></div>
<div class="hook">【${esc(x.hook)}】</div>
<div><div class="title">《${esc(x.title_cn||x.title)}》</div><div class="meta">${esc(pl(x))} · ${esc(x.board)}${x.heat?" · "+esc(x.heat):""} · ${esc(x.genre)}</div></div>
<div class="hl"><b>高光时刻</b>:${esc(x.highlight)}${x.basis=="剧名推断"?'<span class="tag 中">依据剧名推断</span>':""}</div>
<div class="cf"><b>核心冲突</b>:${esc(x.conflict)}</div>
<div class="tags"><span class="tag">${esc(x.route)}</span>${x.hook_type.split("/").map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div>
<div class="v30"><b>30秒前贴</b>:${esc(x.video30)}</div>
<div class="foot"><a href="${esc(x.url)}" target="_blank" rel="noopener">官网查看 →</a></div></div>`).join("")}
$("d").onchange=()=>{cat="全部";draw()};$("q").oninput=draw;draw();</script></body></html>'''
(B / "library.html").write_text(html.replace("__DATA__", json.dumps(days, ensure_ascii=False)), encoding="utf8")
print("ok", list(days))

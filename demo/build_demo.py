#!/usr/bin/env python3
"""生成 AI前贴原型 demo 页面(白色主题),输出到仓库根目录 index.html。
文字类结果来自 content.py(预先生成);视频生成步骤只做模拟。"""
import json, re
from pathlib import Path
from content import SAMPLES, ROLE_COLORS, PROMPT_VIRAL

HERE = Path(__file__).parent
ROOT = HERE.parent
PROMPT_FILE = ROOT.parent / "AI前贴_整合版提示词_第三版.txt"

# 从方案文档的提示词文件里按标题切出各提示词
txt = PROMPT_FILE.read_text(encoding="utf8")
marks = [("P-A", "一、P-A"), ("P-H", "二、P-H"), ("P-R", "三、P-R"), ("P-C", "四、P-C")]
prompts = {}
for i, (k, m) in enumerate(marks):
    a = txt.index(m)
    b = txt.index(marks[i + 1][1]) if i + 1 < len(marks) else len(txt)
    prompts[k] = txt[a:b].strip()
prompts["P-B"] = PROMPT_VIRAL.strip()
names = {"P-A": "分析原片", "P-H": "钩子库·提取高光钩子", "P-R": "推荐钩子", "P-C": "生成创作思路", "P-B": "爆款拆解与仿写"}

DATA = {"samples": SAMPLES, "colors": ROLE_COLORS, "prompts": prompts, "pnames": names}

HTML = r'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI前贴 · 原型演示</title><style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#fff;color:#1f2937;font-size:14px}
.top{display:flex;align-items:center;gap:28px;padding:0 32px;height:58px;border-bottom:1px solid #eef0f4;position:sticky;top:0;background:#fff;z-index:5}
.logo{font-weight:700;font-size:17px;color:#2E6DB4}.nav a{margin-right:22px;color:#4b5563;text-decoration:none;padding:18px 0;border-bottom:2px solid transparent;cursor:pointer}
.nav a.on{color:#2E6DB4;border-bottom-color:#2E6DB4;font-weight:600}
.wrap{max-width:1180px;margin:0 auto;padding:24px 32px 60px}
.steps{display:flex;gap:0;margin:4px 0 26px}.st{flex:1;display:flex;align-items:center;gap:10px;color:#9ca3af;font-size:13px;cursor:pointer}
.st i{font-style:normal;width:26px;height:26px;border-radius:50%;border:1.5px solid #d1d5db;display:flex;align-items:center;justify-content:center;font-size:12px;flex:none;background:#fff}
.st:after{content:"";flex:1;height:1.5px;background:#e5e7eb;margin-right:10px}.st:last-child:after{display:none}
.st.done i{background:#2E6DB4;border-color:#2E6DB4;color:#fff}.st.now{color:#2E6DB4;font-weight:600}.st.now i{border-color:#2E6DB4;color:#2E6DB4}
.card{border:1px solid #eef0f4;border-radius:10px;padding:20px 22px;margin-bottom:16px;background:#fff}
.card h3{margin:0 0 14px;font-size:15px}.muted{color:#6b7280;font-size:12.5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
label.f{display:block;font-size:12.5px;color:#4b5563;margin:0 0 6px}select,input[type=text],textarea{width:100%;padding:8px 10px;border:1px solid #d9dee7;border-radius:6px;font:inherit;background:#fff;color:#1f2937}
textarea{min-height:64px;resize:vertical}
.up{border:1.5px dashed #cfd6e2;border-radius:10px;padding:22px;text-align:center;color:#6b7280;background:#fafbfd}
.up b{color:#1f2937}.opt{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;justify-content:center}
.pill{padding:6px 14px;border:1px solid #d9dee7;border-radius:16px;cursor:pointer;font-size:13px;background:#fff}.pill.on{border-color:#2E6DB4;color:#2E6DB4;background:#f0f6fe;font-weight:600}
.btn{padding:9px 20px;border-radius:7px;border:1px solid #2E6DB4;background:#2E6DB4;color:#fff;font:inherit;cursor:pointer}.btn:hover{background:#255d9c}
.btn.ghost{background:#fff;color:#2E6DB4}.btn:disabled{opacity:.45;cursor:not-allowed}
.acts{display:flex;gap:10px;justify-content:flex-end;margin-top:6px}
.kv{display:grid;grid-template-columns:110px 1fr;gap:8px 14px;font-size:13.5px;line-height:1.6}.kv dt{color:#6b7280}.kv dd{margin:0}
.role{display:flex;gap:12px;padding:12px;border:1px solid #eef0f4;border-radius:8px}
.av{width:46px;height:46px;border-radius:50%;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;flex:none}
.tag{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;background:#f0f6fe;color:#2E6DB4;margin-right:4px}
.tag.y{background:#fff6e0;color:#9a6a00}.tag.g{background:#e8f7ee;color:#1b7a36}
.hk{border:1px solid #eef0f4;border-radius:8px;padding:12px 14px;cursor:pointer;position:relative}.hk.on{border-color:#2E6DB4;background:#f7fbff}
.hk .h{font-weight:600;line-height:1.55}.hk .t{font-size:12px;color:#2E6DB4;margin-top:6px}
.ver{border:1px solid #eef0f4;border-radius:10px;padding:16px;cursor:pointer;display:flex;flex-direction:column;gap:8px}.ver.on{border-color:#2E6DB4;box-shadow:0 0 0 3px #e3eefb}
.ver .tt{font-weight:700;font-size:15px;line-height:1.5}.score{color:#E0A21B;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{border-bottom:1px solid #f0f2f5;padding:9px 8px;text-align:left;vertical-align:top}th{color:#6b7280;font-weight:500;background:#fafbfd}
td textarea{min-height:52px;font-size:13px}
.video{aspect-ratio:9/16;max-height:440px;border-radius:10px;background:linear-gradient(160deg,#eef3fb,#dfe8f6);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#2E6DB4;position:relative;overflow:hidden}
.video .play{width:58px;height:58px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 2px 10px #2e6db433}
.video .cap{position:absolute;bottom:14px;left:14px;right:14px;font-size:12px;color:#33507a;text-align:center}
.tl{display:flex;height:34px;border-radius:6px;overflow:hidden;margin:12px 0;font-size:12px;color:#fff}.tl div{display:flex;align-items:center;justify-content:center}
.spin{width:34px;height:34px;border:3px solid #dbe6f5;border-top-color:#2E6DB4;border-radius:50%;animation:s 1s linear infinite}@keyframes s{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.spin{animation:none}}
pre{white-space:pre-wrap;font:12.5px/1.7 ui-monospace,Menlo,monospace;background:#fafbfd;border:1px solid #eef0f4;border-radius:8px;padding:14px;max-height:520px;overflow:auto;margin:0}
details.pv{margin-top:10px}details.pv summary{cursor:pointer;color:#2E6DB4;font-size:12.5px}
.plist a{display:block;padding:9px 12px;border-radius:6px;color:#374151;cursor:pointer;text-decoration:none}.plist a.on{background:#f0f6fe;color:#2E6DB4;font-weight:600}
.roles{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.rc{border:1px solid #eef0f4;border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.rc .ph{aspect-ratio:3/4;background:#f5f7fa;position:relative;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#9ca3af}.rc .ph img{width:100%;height:100%;object-fit:cover;object-position:top}
.rc .chg{position:absolute;right:8px;bottom:8px;background:#fffffff0;color:#2E6DB4;font-size:12px;padding:3px 9px;border-radius:12px;cursor:pointer}
.rc.empty{border-style:dashed}.up2{cursor:pointer}.up2 span{font-size:30px;line-height:1}.up2 em{font-style:normal;font-size:12px;margin-top:4px}
.rc .ri{padding:10px 12px;font-size:13px;line-height:1.6}.rc .ri .muted{font-size:12px}
@media(max-width:900px){.roles{grid-template-columns:repeat(2,1fr)}}
iframe{width:100%;height:calc(100vh - 110px);border:0}
.ok{color:#1b7a36;font-weight:600}
</style></head><body>
<div class="top"><div class="logo">AI前贴</div><div class="nav" id="nav"></div></div>
<div id="page"></div>
<script>
const D=__DATA__;
const $=s=>document.querySelector(s);const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const TABS=[["origin","原片理解"],["viral","爆款复刻"],["lib","短剧高光钩子库"],["prompt","提示词"]];
let tab="origin";
const S={origin:{step:0,sample:0,lang:"中文",dur:30,cap:5,hooks:[],ver:null,edits:null,model:"即梦",bgm:"紧张悬疑",gen:0,mirror:[]},
         viral:{step:0,sample:1,dur:30,gen:0,mirror:[],edits:null}};
function nav(){$("#nav").innerHTML=TABS.map(([k,n])=>`<a class="${k==tab?"on":""}" onclick="tab='${k}';render()">${n}</a>`).join("")}
function steps(names,cur,key){return `<div class="steps">`+names.map((n,i)=>`<div class="st ${i<cur?"done":i==cur?"now":""}" onclick="if(${i}<=${cur}){S.${key}.step=${i};render()}"><i>${i<cur?"✓":i+1}</i>${n}</div>`).join("")+`</div>`}
let CUR=null;const UP={};
function img(id){const k=(CUR?CUR.id:"")+id;if(UP[k])return UP[k];const r=CUR&&CUR.roles.find(x=>x.id==id);return r&&r.img}
function av(id,size){const z=size||46,u=img(id);return u?`<img class="av" src="${u}" style="width:${z}px;height:${z}px;object-fit:cover;object-position:top">`:`<div class="av" style="background:${D.colors[id]||"#9ca3af"};width:${z}px;height:${z}px;font-size:${z/2.8}px">${id}</div>`}
function upRole(k,inp){const f=inp.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{UP[k]=e.target.result;render()};r.readAsDataURL(f)}
function pv(k){return `<details class="pv"><summary>查看本步提示词 ${k}</summary><pre>${esc(D.prompts[k])}</pre></details>`}
function sampleSel(st){return D.samples.map((s,i)=>`<span class="pill ${st.sample==i?"on":""}" onclick="S.${st===S.origin?"origin":"viral"}.sample=${i};render()">${esc(s.name)}</span>`).join("")}
function cur(st){return D.samples[st.sample]}

/* ---------- 原片理解 ---------- */
function origin(){const st=S.origin,s=cur(st);let h=steps(["上传原片","分析原片并推荐钩子","生成创作思路","人工确认、调整","生成前贴并拼接原片"],st.step,"origin");
if(st.step==0){h+=`<div class="card"><h3>上传原片</h3><div class="up"><b>点击或拖入原片视频</b><div class="muted" style="margin-top:6px">不超过 25 分钟 · 来源:kalos 剧库 / 导入司南 / 本地上传</div><div class="muted" style="margin-top:14px">演示用原片</div><div class="opt">${sampleSel(st)}</div></div>
<div class="grid3" style="margin-top:18px"><div><label class="f">前贴目标语言</label><select onchange="S.origin.lang=this.value">${["中文","英语","西班牙语","葡萄牙语","日语"].map(x=>`<option ${x==st.lang?"selected":""}>${x}</option>`).join("")}</select></div>
<div><label class="f">前贴时长(秒)</label><select onchange="S.origin.dur=+this.value">${[10,15,20,30].map(x=>`<option ${x==st.dur?"selected":""}>${x}</option>`).join("")}</select></div>
<div><label class="f">主要角色上限</label><input type="text" value="5 个(默认)" disabled></div></div>
<div class="grid2" style="margin-top:14px"><div><label class="f">处理的集数</label><input type="text" value="第1集"></div><div><label class="f">投放后台标签(选填)</label><input type="text" placeholder="二创模版、剧ID、素材指派组等"></div></div></div>
<div class="acts"><button class="btn" onclick="S.origin.step=1;render()">开始分析</button></div>`}
if(st.step==1){const a=s.analysis;h+=`<div class="card"><h3>原片分析 · ${esc(s.name)} <span class="muted">${esc(s.meta)}</span></h3><dl class="kv">${["一句话剧情","核心冲突","男女主人设","身份反差","原片主题","最大卖点","原片开头"].map(k=>`<dt>${k}</dt><dd>${esc(a[k])}</dd>`).join("")}<dt>衔接点</dt><dd>${a["衔接点"].map(esc).join("<br>")}</dd></dl>${pv("P-A")}</div>
<div class="card"><h3>角色与资产图 <span class="muted">主要角色上限 5 个,已识别 ${s.roles.length} 个</span></h3><div class="roles">${s.roles.map(r=>`<div class="rc"><div class="ph">${img(r.id)?`<img src="${img(r.id)}">`:""}<label class="chg">更换<input type="file" accept="image/*" hidden onchange="upRole('${s.id+r.id}',this)"></label></div><div class="ri"><div><b>角色${r.id}</b> <span class="tag">${esc(r.pos)}</span><span class="tag ${r.conf=="高"?"g":"y"}">把握:${r.conf}</span></div><div class="muted">名字:${esc(r.name)}</div><div class="muted">${esc(r.identity)}</div><div class="muted">${esc(r.look)}</div><div class="muted">出镜:${esc(r.times)}</div></div></div>`).join("")}${Array.from({length:5-s.roles.length},(_,i)=>{const id="ABCDE"[s.roles.length+i],k=s.id+id;return `<div class="rc empty"><label class="ph up2">${UP[k]?`<img src="${UP[k]}">`:`<span>+</span><em>上传角色图</em>`}<input type="file" accept="image/*" hidden onchange="upRole('${k}',this)"></label><div class="ri"><div><b>角色${id}</b> <span class="tag y">未识别</span></div><div class="muted">未能从原片提取,可手动上传</div><input type="text" placeholder="角色名字 / 定位" style="margin-top:6px"></div></div>`}).join("")}</div></div>
<div class="card"><h3>推荐钩子 <span class="muted">来自短剧高光钩子库,可多选,也可以不选</span></h3><div class="grid3">${s.hooks.map((k,i)=>`<div class="hk ${st.hooks.includes(i)?"on":""}" onclick="tg(${i})"><div class="h">【${esc(k.hook)}】</div><div class="t">《${esc(k.title)}》</div><div class="muted" style="margin-top:6px">${esc(k.why)}</div></div>`).join("")}</div>${pv("P-R")}</div>
<div class="acts"><button class="btn ghost" onclick="S.origin.step=0;render()">上一步</button><button class="btn" onclick="S.origin.step=2;render()">生成创作思路</button></div>`}
if(st.step==2){h+=`<div class="grid3">${s.versions.map((v,i)=>`<div class="ver ${st.ver===i?"on":""}" onclick="S.origin.ver=${i};S.origin.edits=null;render()"><div class="muted">${v.name} ${v.recommend?'<span class="tag g">推荐</span>':""}</div><div class="tt">【${esc(v.title)}】</div><div><span class="tag">${esc(v.route)}</span></div><div class="muted">钩子:${esc(v.hook_type)} · 吸引力 <span class="score">${v.score}</span> 分</div><div style="line-height:1.6">${esc(v.summary)}</div><div class="muted"><b>放大卖点</b>:${esc(v.sell)}</div><div class="muted"><b>衔接</b>:${esc(v.link.way)}<br>${esc(v.link.end)}</div><div style="display:flex;gap:6px;align-items:center">${v.cast.map(c=>av(c,28)).join("")}<span class="muted">出场角色</span></div></div>`).join("")}</div>${pv("P-C")}
<div class="acts" style="margin-top:16px"><button class="btn ghost" onclick="S.origin.step=1;render()">上一步</button><button class="btn ghost" onclick="alert('将重新调用创作思路提示词生成 3 个新版本')">都不满意,重新生成</button><button class="btn" ${st.ver===null?"disabled":""} onclick="S.origin.step=3;render()">选这个版本</button></div>`}
if(st.step==3){const v=s.versions[st.ver];if(!st.edits)st.edits=v.beats.map(b=>[...b]);h+=editor(v,st,"origin")}
if(st.step==4){const v=s.versions[st.ver];h+=genView(v,st,"origin",s)}
return h}
function tg(i){const a=S.origin.hooks;a.includes(i)?a.splice(a.indexOf(i),1):a.push(i);render()}

function editor(v,st,key){return `<div class="card"><h3>${v.name||"仿写"} · 【${esc(v.title)}】</h3><table><tr><th style="width:80px">时间</th><th>画面描述</th><th style="width:30%">台词或旁白</th></tr>${st.edits.map((b,i)=>`<tr><td>${esc(b[0])}</td><td><textarea oninput="S.${key}.edits[${i}][1]=this.value">${esc(b[1])}</textarea></td><td><textarea oninput="S.${key}.edits[${i}][2]=this.value">${esc(b[2])}</textarea></td></tr>`).join("")}</table>
${v.prompt?`<div style="margin-top:14px"><label class="f">视频生成提示词(修改台词后同步更新)</label><textarea style="min-height:90px">${esc(v.prompt)}</textarea></div>`:""}</div>
<div class="card"><h3>资产图与参数</h3><div style="display:flex;gap:14px;margin-bottom:16px">${v.cast.map(c=>`<div style="text-align:center">${av(c,52)}<div class="muted" style="margin-top:4px">角色${c}</div><a class="muted" style="color:#2E6DB4;cursor:pointer">更换</a></div>`).join("")}<div class="up" style="padding:12px 18px;display:flex;align-items:center">+ 补传场景图</div></div>
<div class="grid3"><div><label class="f">前贴时长(秒)</label><select>${[10,15,20,30].map(x=>`<option ${x==st.dur?"selected":""}>${x}</option>`).join("")}</select></div><div><label class="f">BGM</label><select>${["紧张悬疑","爽感燃","虐心抒情","轻快"].map(x=>`<option>${x}</option>`).join("")}</select></div><div><label class="f">视频模型</label><select>${["即梦","可灵","seedance 2.0","Veo"].map(x=>`<option>${x}</option>`).join("")}</select></div></div></div>
<div class="acts"><button class="btn ghost" onclick="S.${key}.step--;render()">上一步</button><button class="btn" onclick="S.${key}.step++;S.${key}.gen=0;render()">确认,去生成</button></div>`}

function genView(v,st,key,s){let h=`<div class="grid2"><div class="card"><h3>前贴视频</h3>`;
if(st.gen==0)h+=`<div class="video"><div class="muted" style="margin-bottom:14px">尚未生成</div><button class="btn" onclick="S.${key}.gen=1;render();setTimeout(()=>{S.${key}.gen=2;render()},1800)">模拟已生成视频</button><div class="cap">视频生成步骤在原型中为模拟</div></div>`;
if(st.gen==1)h+=`<div class="video"><div class="spin"></div><div style="margin-top:12px">正在生成前贴…</div></div>`;
if(st.gen==2)h+=`<div class="video"><div class="play">▶</div><div style="margin-top:12px;font-weight:600">【${esc(v.title)}】</div><div class="cap">模拟视频 · ${st.dur||30} 秒 · 9:16</div></div><div class="acts"><button class="btn ghost" onclick="S.${key}.step--;render()">不满意,返回修改</button><button class="btn ghost" onclick="S.${key}.gen=0;render()">重新生成</button></div>`;
h+=`</div><div class="card"><h3>拼接原片</h3>`;
if(st.gen<2)h+=`<div class="muted">前贴生成后可拼接</div>`;
else{h+=`<div class="tl"><div style="width:22%;background:#2E6DB4">前贴 ${st.dur||30}s</div><div style="width:78%;background:#94a3b8">原片 · ${esc(s.name)}</div></div>
<dl class="kv"><dt>字幕</dt><dd><label><input type="checkbox" checked> 按确认后的台词添加字幕</label></dd><dt>规格</dt><dd>统一分辨率 1080×1920 · 30fps · 音量标准化</dd><dt>衔接</dt><dd>${esc(v.link? v.link.end : (v.linkText||""))}</dd></dl>
<h3 style="margin-top:20px">镜像前贴 <span class="muted">相同内容,换字幕语言</span></h3><div class="opt" style="justify-content:flex-start">${["英语","西班牙语","葡萄牙语","日语","印尼语"].map(l=>`<span class="pill ${st.mirror.includes(l)?"on":""}" onclick="mi('${key}','${l}')">${l}</span>`).join("")}</div>
${st.mirror.length?`<div class="muted" style="margin-top:10px">${st.mirror.map(l=>`<div>✓ ${l}镜像前贴 · 字幕已翻译(模拟)</div>`).join("")}</div>`:""}
<div class="acts" style="margin-top:18px"><button class="btn" onclick="this.outerHTML='<span class=ok>✓ 成片已确认(模拟)</span>'">确认成片</button></div>`}
return h+`</div></div>`}
function mi(k,l){const a=S[k].mirror;a.includes(l)?a.splice(a.indexOf(l),1):a.push(l);render()}

/* ---------- 爆款复刻 ---------- */
function viral(){const st=S.viral,s=cur(st),vr=s.viral;let h=steps(["上传爆款与原片","分析原片与爆款","生成爆款仿写","人工确认、调整","生成前贴并拼接原片"],st.step,"viral");
if(!vr){return h+`<div class="card">该原片暂无爆款复刻演示</div>`}
const rw={...vr.rewrite,name:"爆款仿写",linkText:vr.rewrite.link,prompt:""};
if(st.step==0){h+=`<div class="grid2"><div class="card"><h3>上传爆款视频</h3><div class="up"><b>点击或拖入爆款视频</b><div class="muted" style="margin:10px 0">或粘贴抖音视频链接</div><input type="text" placeholder="https://v.douyin.com/..."></div><div class="muted" style="margin-top:10px">演示:${esc(vr.source)}</div></div>
<div class="card"><h3>上传原片</h3><div class="up"><b>点击或拖入原片视频</b><div class="muted" style="margin-top:14px">演示用原片</div><div class="opt"><span class="pill on">${esc(s.name)}</span></div></div></div></div>
<div class="acts"><button class="btn" onclick="S.viral.step=1;render()">开始分析</button></div>`}
if(st.step==1){h+=`<div class="card"><h3>爆款拆解</h3><table><tr><th style="width:80px">时间</th><th style="width:110px">作用</th><th>画面要点</th></tr>${vr.structure.map(r=>`<tr><td>${r[0]}</td><td><span class="tag">${esc(r[1])}</span></td><td>${esc(r[2])}</td></tr>`).join("")}</table></div>
<div class="card"><h3>原片分析 · ${esc(s.name)}</h3><dl class="kv">${["一句话剧情","核心冲突","最大卖点","原片开头"].map(k=>`<dt>${k}</dt><dd>${esc(s.analysis[k])}</dd>`).join("")}</dl><div style="display:flex;gap:10px;margin-top:12px">${s.roles.map(r=>`<div style="display:flex;gap:6px;align-items:center">${av(r.id,30)}<span class="muted">${esc(r.pos)}</span></div>`).join("")}</div>${pv("P-A")}</div>
<div class="acts"><button class="btn ghost" onclick="S.viral.step=0;render()">上一步</button><button class="btn" onclick="S.viral.step=2;render()">生成爆款仿写</button></div>`}
if(st.step==2){h+=`<div class="card"><h3>【${esc(rw.title)}】</h3><div style="display:flex;gap:6px;align-items:center;margin-bottom:12px">${rw.cast.map(c=>av(c,28)).join("")}<span class="muted">出场角色</span></div><table><tr><th style="width:80px">时间</th><th>画面描述</th><th style="width:30%">台词或旁白</th></tr>${rw.beats.map(b=>`<tr><td>${b[0]}</td><td>${esc(b[1])}</td><td>${esc(b[2])}</td></tr>`).join("")}</table><div class="muted" style="margin-top:12px"><b>衔接</b>:${esc(rw.link)}</div>${pv("P-B")}</div>
<div class="acts"><button class="btn ghost" onclick="S.viral.step=1;render()">上一步</button><button class="btn" onclick="S.viral.step=3;S.viral.edits=null;render()">确认,去调整</button></div>`}
if(st.step==3){if(!st.edits)st.edits=rw.beats.map(b=>[...b]);h+=editor(rw,st,"viral")}
if(st.step==4){h+=genView(rw,st,"viral",s)}
return h}

/* ---------- 提示词 ---------- */
let pk="P-A";
function prompt(){const ks=Object.keys(D.prompts);return `<div style="display:grid;grid-template-columns:200px 1fr;gap:20px"><div class="plist">${ks.map(k=>`<a class="${k==pk?"on":""}" onclick="pk='${k}';render()">${k} ${esc(D.pnames[k])}</a>`).join("")}</div><pre style="max-height:none">${esc(D.prompts[pk])}</pre></div>`}

function render(){nav();let h;CUR=tab=="viral"?cur(S.viral):cur(S.origin);
if(tab=="lib"){$("#page").innerHTML=`<iframe src="library.html"></iframe>`;return}
h=tab=="origin"?origin():tab=="viral"?viral():prompt();
if(tab=="viral"&&S.viral.step==0)h=h.replace("</h3><div class=\"up\"><b>点击或拖入原片视频","</h3><div class=\"up\"><b>点击或拖入原片视频");
$("#page").innerHTML=`<div class="wrap">${h}</div>`;window.scrollTo(0,0)}
render();
</script></body></html>'''

(ROOT / "index.html").write_text(HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)), encoding="utf8")
print("demo ok")

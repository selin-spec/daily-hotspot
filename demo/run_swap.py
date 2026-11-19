#!/usr/bin/env python3
"""把两组演示样例的爆款视频对换,通过本机程序的接口重新完整分析(原片分析 + 爆款拆解)。
只调用本机程序已有的接口,不修改本机程序。输出新任务编号到 public_data/swap_jobs.json。"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

B = "http://127.0.0.1:8765"
JOBS = Path(__file__).resolve().parents[2] / "qiantie_app" / "jobs"
PAIRS = [  # (原片文件, 原片显示名, 爆款文件, 爆款显示名, 模型, 时长)
    (JOBS / "74bee1fb5cdf" / "source.mp4", "解说素材测试-剧情跳跃3.mp4", JOBS / "e9097d1f7a81" / "viral.mp4", "20261105-AI前贴.mp4", "seedance 2.5", 30),
    (JOBS / "e9097d1f7a81" / "source.mp4", "高光_Destined to Love.mp4", JOBS / "74bee1fb5cdf" / "viral.mp4", "解说素材测试-剧情跳跃1.mp4", "seedance 2.0", 15),
]


def req(method, path, data=None, ctype=None):
    r = urllib.request.Request(B + path, data=data, method=method, headers={"Content-Type": ctype} if ctype else {})
    return json.load(urllib.request.urlopen(r, timeout=600))


out = []
for src, sname, vsrc, vname, model, secs in PAIRS:
    st = req("PUT", "/api/upload?mode=viral&name=" + urllib.parse.quote(sname), src.read_bytes())
    jid = st["id"]
    req("PUT", f"/api/job/{jid}/viral?name=" + urllib.parse.quote(vname), vsrc.read_bytes())
    req("POST", f"/api/job/{jid}/start", json.dumps({"model": model, "seconds": secs, "mode": "viral"}).encode(), "application/json")
    t0 = time.time()
    while True:
        time.sleep(10)
        t = req("GET", f"/api/job/{jid}")["tasks"]["analyze"]
        print(f"  {jid} {int(time.time() - t0)}s {t.get('status')} {t.get('stage', '')}", flush=True)
        if t["status"] in ("done", "error"):
            break
    if t["status"] == "error":
        raise SystemExit(jid + " 分析失败:" + t.get("error", ""))
    out.append(jid)
    print(sname, "+", vname, "→", jid, flush=True)

(Path(__file__).parent / "public_data" / "swap_jobs.json").write_text(json.dumps(out), encoding="utf8")
print("完成", out)

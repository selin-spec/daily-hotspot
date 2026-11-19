#!/usr/bin/env python3
"""生成线上演示版 index.html(发布到 GitHub Pages)。
界面与本机版一致;没有后台,所以文字结果用本机版对样例原片真实跑出的结果,视频为模拟。
只读取本机程序的任务数据,不修改本机程序。"""
import json, glob, shutil, sys, re
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent                        # hotspot 仓库根目录
APP = ROOT.parent / "qiantie_app"
sys.path.insert(0, str(APP))
import prompts, pipeline                  # noqa: E402
from viral_prompt import P_B              # noqa: E402
from creative_prompt import P_C            # noqa: E402
from hook_prompt import P_R                # noqa: E402
from prompts_v4 import PAGE                # noqa: E402

ASSETS = ROOT / "demo_assets"
SAMPLES = {
    "origin": [("cd23ea23928b", "解说素材测试-剧情跳跃2"), ("44c3a84736f6", "高光 Destined to Love")],
    # 2026-11-19 对换了两组的爆款视频,测试爆款与原片完全不相关时的效果
    "viral": [("fa5f07843f15", "原片:剧情跳跃3 + 爆款:AI前贴"), ("2717693739b2", "原片:高光 Destined to Love + 爆款:剧情跳跃1")],
}
NAMES = {"a.mp4": "解说素材测试-剧情跳跃3.mp4", "viral.mp4": "解说素材测试-剧情跳跃1.mp4", "剧情跳跃2.mp4": "解说素材测试-剧情跳跃2.mp4"}


def library():
    d = json.load(open(ROOT / "data" / "master.json", encoding="utf8"))  # 跨天去重后的总库
    return {"date": d["updated"], "items": [{"id": i, "hook": x["hook"], "title": (x.get("title_cn") or x["title"]).replace("\ufffd", ""),
            "platform": x["platform"], "highlight": x.get("highlight", ""), "conflict": x.get("conflict", ""),
            "route": x.get("route", ""), "adapt": x.get("adapt", "")} for i, x in enumerate(d["items"])]}


def copy_img(jid, u):
    if not u:
        return ""
    rel = re.sub(r"^/files/[0-9a-f]+/", "", u).split("?")[0]
    src = APP / "jobs" / jid / rel
    dst = ASSETS / jid / Path(rel).name
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy(src, dst)
    return f"demo_assets/{jid}/{dst.name}"


def job(jid, mode):
    st = json.loads((APP / "jobs" / jid / "state.json").read_text(encoding="utf8"))
    m = st["meta"]
    meta = {k: m.get(k) for k in ("duration", "width", "height", "has_audio", "model", "seconds")}
    meta.update(name=NAMES.get(m["name"], m["name"]), mode=mode)
    if m.get("viral"):
        v = m["viral"]; meta["viral"] = {"name": NAMES.get(v["name"], v["name"]), "duration": v["duration"], "has_audio": v["has_audio"]}
    roles = [dict(r, img=copy_img(jid, r.get("img"))) for r in st.get("roles", [])]
    if mode == "viral":
        creative = [json.loads((HERE / "public_data" / f"rewrite-{jid}.json").read_text(encoding="utf8"))]
    else:
        cf = HERE / "public_data" / f"creative-{jid}.json"
        if cf.exists():
            cd = json.loads(cf.read_text(encoding="utf8")); creative = cd["creative"]; st["hooks"] = cd["hooks"]
        else:
            creative = st.get("creative", [])
    for v in creative:
        for b in v.get("脚本节拍", []):
            nums = re.findall(r"\d+(?:\.\d+)?", b.get("时间", ""))
            b["_start"], b["_end"] = (float(nums[0]), float(nums[1])) if len(nums) >= 2 else (0, 0)
    teaser = ASSETS / jid / "teaser.mp4"
    teaser.parent.mkdir(parents=True, exist_ok=True)
    pipeline.simulate_video(teaser, creative[0].get("标题钩子", ""), creative[0].get("脚本节拍", []), meta["seconds"], True)
    shutil.rmtree(teaser.parent / "sim", ignore_errors=True)
    return {"id": jid, "meta": meta, "tasks": {}, "analysis": st["analysis"], "roles": roles, "hooks": st.get("hooks", []),
            "breakdown": st.get("breakdown"), "creative": creative, "teaser_url": f"demo_assets/{jid}/teaser.mp4", "mirrors": []}


def main():
    shutil.rmtree(ASSETS, ignore_errors=True); ASSETS.mkdir()
    jobs = {}
    for mode, L in SAMPLES.items():
        for jid, _ in L:
            jobs[jid] = job(jid, mode)
    demo = {
        "config": {"models": prompts.MODELS},
        "library": library(),
        "prompts": dict(PAGE),
        "jobs": jobs,
        "samples": {m: [{"id": j, "label": lab} for j, lab in L] for m, L in SAMPLES.items()},
    }
    html = (HERE / "public_app.html").read_text(encoding="utf8")
    html = html.replace("__DEMO__", json.dumps(demo, ensure_ascii=False).replace("</", "<\\/"))
    html = html.replace("<iframe src=\"/library.html\">", "<iframe src=\"library.html\">")
    (ROOT / "index.html").write_text(html, encoding="utf8")
    print("ok", {k: len(v) for k, v in SAMPLES.items()}, "钩子", len(demo["library"]["items"]))


if __name__ == "__main__":
    main()

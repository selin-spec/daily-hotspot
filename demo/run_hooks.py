#!/usr/bin/env python3
"""用第二版推荐钩子提示词(只推荐和原片主角人设对得上的钩子),为线上演示版的原片样例重新挑 3 条钩子。
只读取本机程序的任务数据和调用模型的工具函数,不修改本机程序。
用法: run_hooks.py 任务编号 [任务编号...]"""
import json, sys, glob
from pathlib import Path

HERE = Path(__file__).parent
APP = HERE.parents[1] / "qiantie_app"
sys.path.insert(0, str(APP))
import llm  # noqa: E402
from hook_prompt import P_R  # noqa: E402

d = json.load(open(sorted(glob.glob(str(HERE.parent / "data" / "hooks-*.json")))[-1], encoding="utf8"))
items = [{"id": i, "hook": x["hook"], "title": (x.get("title_cn") or x["title"]).replace("\ufffd", ""), "platform": x["platform"],
          "highlight": x.get("highlight", ""), "conflict": x.get("conflict", ""), "route": x.get("route", ""), "adapt": x.get("adapt", "")}
         for i, x in enumerate(d["items"])]
lines = "\n".join(f"{x['id']} | {x['hook']} | {x['highlight']} | {x['conflict']}" for x in items)

for jid in sys.argv[1:]:
    st = json.loads((APP / "jobs" / jid / "state.json").read_text(encoding="utf8"))
    a, roles = st["analysis"], st["roles"]
    p = llm.fill(P_R, 一句话剧情=a["一句话剧情"], 原片开头=a["原片开头"],
                 角色人设="\n".join(f"{r['code']}:{r['pos']};人设:{r['persona']}" for r in roles),
                 衔接点="\n".join(f"{l['方式']}:{l['说明']}" for l in a["衔接点"]), 钩子库=lines)
    for attempt in range(3):
        try:
            r = llm.ask(p, APP / "jobs" / jid); break
        except Exception as e:
            print(jid, "第", attempt + 1, "次格式不对,重试:", str(e)[:80])
    else:
        raise SystemExit(jid + " 连续3次失败")
    out = []
    for x in r.get("推荐", []):
        i = int(x["编号"])
        if 0 <= i < len(items) and all(o["id"] != i for o in out):
            out.append(dict(items[i], reason=x.get("人设对应", "") or x.get("理由", "")))
    out = out[:3]
    (HERE / "public_data" / f"hooks-{jid}.json").write_text(json.dumps({"主角": r.get("原片主角", ""), "hooks": out}, ensure_ascii=False, indent=1), encoding="utf8")
    print(jid, "主角:", r.get("原片主角"))
    for h in out:
        print("   ", h["highlight"][:30], "|", h["reason"])

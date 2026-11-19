#!/usr/bin/env python3
"""用第二版爆款仿写提示词,基于本机已分析好的任务数据,重新生成线上演示版的爆款仿写。
只读取本机程序的任务数据和调用模型的工具函数,不修改本机程序。
用法: run_viral.py 任务编号 [任务编号...]"""
import json, sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "qiantie_app"
sys.path.insert(0, str(APP))
import llm  # noqa: E402
from viral_prompt import P_B  # noqa: E402

OUT = Path(__file__).parent / "public_data"; OUT.mkdir(exist_ok=True)

for jid in sys.argv[1:]:
    st = json.loads((APP / "jobs" / jid / "state.json").read_text(encoding="utf8"))
    a, roles, bd, meta = st["analysis"], st["roles"], st["breakdown"], st["meta"]
    p = llm.fill(P_B, 爆款内容=bd["一句话内容"], 爆款钩子=bd["开头钩子"], 爆款爽点=bd["爽点"],
                 爆款结构="\n".join(f"{x['时间']} {x['作用']}:{x['画面要点']}" for x in bd["结构"]),
                 一句话剧情=a["一句话剧情"], 原片开头=a["原片开头"],
                 角色人设="\n".join(f"{r['code']}:{r['pos']};人设:{r['persona']}" for r in roles),
                 衔接点="\n".join(f"{l['方式']}:{l['说明']}" for l in a["衔接点"]),
                 模型=meta["model"], 时长=meta["seconds"])
    v = llm.ask(p, APP / "jobs" / jid, timeout=1200)
    (OUT / f"rewrite-{jid}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf8")
    print(jid, v.get("标题钩子"), "|", v.get("保留的爆款剧情"))

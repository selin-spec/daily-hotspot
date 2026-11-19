#!/usr/bin/env python3
"""用第二版创作思路提示词,基于本机已分析好的任务数据和它的 3 条推荐钩子,重新生成线上演示版的创作思路。
只读取本机程序的任务数据和调用模型的工具函数,不修改本机程序。
用法: run_creative.py 任务编号 [任务编号...]"""
import json, sys
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "qiantie_app"
sys.path.insert(0, str(APP))
import llm  # noqa: E402
from creative_prompt import P_C  # noqa: E402

OUT = Path(__file__).parent / "public_data"; OUT.mkdir(exist_ok=True)

for jid in sys.argv[1:]:
    st = json.loads((APP / "jobs" / jid / "state.json").read_text(encoding="utf8"))
    a, roles, hooks, meta = st["analysis"], st["roles"], st["hooks"], st["meta"]
    hf = OUT / f"hooks-{jid}.json"
    if hf.exists():  # 优先用按主角人设重新挑选的钩子
        hooks = json.loads(hf.read_text(encoding="utf8"))["hooks"]
    ht = "\n".join(f"钩子{i + 1}:【{h['hook']}】\n  高光时刻:{h.get('highlight', '')}\n  核心冲突:{h.get('conflict', '')}"
                   for i, h in enumerate(hooks))
    p = llm.fill(P_C, 钩子=ht, 一句话剧情=a["一句话剧情"], 原片开头=a["原片开头"],
                 角色人设="\n".join(f"{r['code']}:{r['pos']};人设:{r['persona']}" for r in roles),
                 衔接点="\n".join(f"{l['方式']}:{l['说明']}" for l in a["衔接点"]),
                 模型=meta["model"], 时长=meta["seconds"])
    for attempt in range(3):
        try:
            r = llm.ask(p, APP / "jobs" / jid, timeout=1500)
            break
        except Exception as e:  # 模型偶尔输出不合格的 JSON,重试
            print(jid, "第", attempt + 1, "次格式不对,重试:", str(e)[:80])
    else:
        raise SystemExit(jid + " 连续3次失败")
    vs = r.get("创作思路", [])[:3]
    (OUT / f"creative-{jid}.json").write_text(json.dumps({"hooks": hooks, "creative": vs}, ensure_ascii=False, indent=1), encoding="utf8")
    for v, h in zip(vs, hooks):
        print(jid, "| 钩子:", h["highlight"][:28], "\n   →", v.get("标题钩子"), "|", v.get("保留的钩子剧情"))

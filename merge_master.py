#!/usr/bin/env python3
"""把每天的钩子快照 data/hooks-日期.json 合并成总库 data/master.json,跨天去重。

去重规则:同一平台的同一部剧只算一次。
  红果按官网的剧集编号(series_id),海外平台按剧的网址,都没有时退回到剧名。
已经在总库里的剧不会重复入库;它第一次入库的日期和卡片内容保持不变,
只更新"最近一次在榜的日期"、热度和榜单名次。
总库每次都从全部每日快照重新合并,重复运行结果一样。

用法:
  merge_master.py           合并并写出 data/master.json
  merge_master.py --known   只输出总库里已有剧的标识(给每日任务判断哪些剧不用再写卡片)"""
import json, glob, re, sys
from pathlib import Path

B = Path(__file__).parent


def key(x):
    url = x.get("url") or ""
    m = re.search(r"series_id=(\d+)", url)
    if m:
        return f"{x.get('platform', '')}|{m.group(1)}"
    if url:
        return f"{x.get('platform', '')}|{url.split('?')[0].rstrip('/')}"
    return f"{x.get('platform', '')}|{(x.get('title') or '').replace(chr(0xfffd), '').strip()}"


def merge():
    master, latest = {}, ""
    for f in sorted(glob.glob(str(B / "data" / "hooks-*.json"))):
        d = json.load(open(f, encoding="utf8"))
        day = d["date"]; latest = max(latest, day)
        for x in d["items"]:
            k = key(x)
            if k not in master:
                card = {kk: (vv.replace("\ufffd", "") if isinstance(vv, str) else vv) for kk, vv in x.items() if kk != "rank"}
                master[k] = dict(card, key=k, first_date=day, last_date=day)
            else:
                m = master[k]
                m["last_date"] = max(m["last_date"], day)
                if day >= m["last_date"]:
                    m["heat"], m["board"] = x.get("heat", m.get("heat", "")), x.get("board", m.get("board", ""))
    items = list(master.values())
    for x in items:
        x["on_board"] = x["last_date"] == latest
    order = {"高": 0, "中": 1, "低": 2}
    items.sort(key=lambda x: (x["first_date"], order.get(x.get("adapt"), 3)), reverse=False)
    items.sort(key=lambda x: x["first_date"], reverse=True)
    return {"updated": latest, "items": items}


if __name__ == "__main__":
    m = merge()
    if "--known" in sys.argv:
        print("\n".join(sorted(x["key"] for x in m["items"])))
        sys.exit(0)
    (B / "data" / "master.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf8")
    new = sum(1 for x in m["items"] if x["first_date"] == m["updated"])
    off = sum(1 for x in m["items"] if not x["on_board"])
    print(f"总库 {len(m['items'])} 部(不重复),{m['updated']} 新增 {new} 部,已下榜 {off} 部")

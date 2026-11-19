"""钩子库入库去重(所有日期合在一起判断,同一部剧、同一场面、同一说法都只收一条)。

三层规则,命中任意一层就算重复:
  1. 同一部剧:去掉标点、第几部/季/集后,剧名前7个字相同(含续集、改名版)。
  2. 同一场面:两条“高光时刻”的文字相似度达到 SCENE_SIM 以上。
  3. 同一说法:两条“前贴钩子”完全相同,或文字相似度达到 HOOK_SIM 以上。
拿不准时按重复处理,宁可少收。
"""
import re, json, glob

SCENE_SIM = 0.42
HOOK_SIM = 0.5


def drama_key(item):
    t = item.get("title_cn") or item["title"]
    t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t)
    t = re.sub(r"第[0-9一二三四五六七八九十]+[部季集]", "", t)
    t = re.sub(r"[0-9]+$", "", t)
    return t[:7]


def _grams(s):
    s = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def sim(a, b):
    ga, gb = _grams(a), _grams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def duplicate_of(item, others):
    """返回 (对方, 层级) ;不重复返回 None。"""
    for o in others:
        if drama_key(item) == drama_key(o):
            return o, "同一部剧"
        if item["hook"] == o["hook"] or sim(item["hook"], o["hook"]) >= HOOK_SIM:
            return o, "同一说法"
        if sim(item["highlight"], o["highlight"]) >= SCENE_SIM:
            return o, "同一场面"
    return None


def load_earlier(date, base):
    out = []
    for f in sorted(glob.glob(str(base / "data/hooks-*.json"))):
        d = json.load(open(f, encoding="utf8"))
        if d["date"] < date:
            out += d["items"]
    return out


def dedupe(items, existing):
    """items 已按优先级排好;已入库的 existing 优先保留。返回 (保留, [(被删, 对方, 层级)])。"""
    kept, dropped = [], []
    for it in items:
        r = duplicate_of(it, existing + kept)
        if r:
            dropped.append((it, r[0], r[1]))
        else:
            kept.append(it)
    return kept, dropped

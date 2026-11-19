#!/usr/bin/env python3
"""抓取短剧平台的公开剧目信息,存到 raw/dramas-日期.json。
来源:红果短剧官网榜单 + 海外短剧平台首页推荐(ReelShort、DramaBox、ShortMax、GoodShort、FlexTV、NetShort)。
只抓公开文字:剧名、简介、链接,不抓视频。简介只存在本地 raw/ 里供分析,不发布到公开网页。"""
import json, re, html, datetime, urllib.request, urllib.parse, time
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path(__file__).parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
PER_SITE = 15

# 名称, 首页, 详情页链接的正则
OVERSEAS = [
    ("ReelShort", "https://www.reelshort.com", r'href="(/movie/[^"?#]+)"|href="(/episodes/episode-1-[^"?#]+)'),
    ("DramaBox", "https://www.dramaboxdb.com", r'href="(/movie/\d+/[^"?#]+)"'),
    ("ShortMax", "https://www.shortmax.app", r'href="(/drama/[^"?#]+-\d+)"'),
    ("GoodShort", "https://www.goodshort.com", r'href="(/drama/[^"?#]+-\d{8,})"'),
    ("FlexTV", "https://www.flextv.cc", r'href="(/(?:detail|series|video|watch)/[^"?#]+)"'),
    ("NetShort", "https://www.netshort.com", r'href="(/drama/[^"?#]+-\d{10,})"'),
]
HONGGUO = "https://www.hongguoduanju.com"
HONGGUO_RANKS = [("真人剧", "/rank/hot-real-drama"), ("AI剧", "/rank/hot-ai-drama"),
                 ("漫剧", "/rank/hot-comic-drama"), ("总榜", "/rank/hot-drama")]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf8", "ignore").replace("\ufffd", "")


def meta(t, *names):
    for n in names:
        m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="([^"]*)"' % re.escape(n), t) or \
            re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="%s"' % re.escape(n), t)
        if m and m.group(1).strip():
            return html.unescape(m.group(1).strip())
    return ""


def hongguo():
    out, seen = [], set()
    for name, path in HONGGUO_RANKS:
        soup = BeautifulSoup(get(HONGGUO + path), "lxml")
        rank = 0
        for a in soup.select('a[href*="detail?series_id"]'):
            title = a.get_text(strip=True)
            sid = re.search(r"series_id=(\d+)", a["href"]).group(1)
            if not title or title.isdigit():
                continue
            rank += 1
            if sid in seen:
                continue
            card = a
            for _ in range(4):
                card = card.parent
            parts = card.get_text("|", strip=True).split("|")
            heat = next((p for p in parts if p.endswith("热度")), "")
            tagline = next((p for p in parts if " · " in p), "")
            syn = max(parts, key=len) if parts else ""
            seen.add(sid)
            out.append({"platform": "红果短剧", "board": f"{name}榜第{rank}名", "title": title, "heat": heat,
                        "genre": tagline.split(" · ")[0] if tagline else "", "lang": "zh",
                        "synopsis": syn if len(syn) >= 30 else "", "url": f"{HONGGUO}/detail?series_id={sid}"})
    return out


def overseas(name, home, pattern):
    t = get(home)
    paths = []
    for m in re.finditer(pattern, t):
        p = next(g for g in m.groups() if g)
        if p not in paths:
            paths.append(p)
    out = []
    for i, p in enumerate(paths[:PER_SITE], 1):
        url = urllib.parse.urljoin(home, p)
        try:
            d = get(url)
        except Exception:
            continue
        title = meta(d, "og:title", "twitter:title") or re.sub(r"\s+", " ", (re.findall(r"<title[^>]*>(.*?)</title>", d, re.S) or [""])[0])
        syn = meta(d, "og:description", "description", "twitter:description")
        out.append({"platform": name, "board": f"首页推荐第{i}位", "title": title.replace("\xa0", " ").strip(), "heat": "", "genre": "",
                    "lang": "en", "synopsis": syn, "url": url})
        time.sleep(0.5)
    return out


def main():
    day = datetime.date.today().isoformat()
    items, log = [], []
    try:
        r = hongguo(); items += r; log.append(f"红果短剧: {len(r)} 部")
    except Exception as e:
        log.append(f"红果短剧: 失败 {e}")
    for name, home, pat in OVERSEAS:
        try:
            r = overseas(name, home, pat); items += r; log.append(f"{name}: {len(r)} 部")
        except Exception as e:
            log.append(f"{name}: 失败 {e}")
    (BASE / "raw").mkdir(exist_ok=True)
    (BASE / "raw" / f"dramas-{day}.json").write_text(json.dumps({"date": day, "items": items}, ensure_ascii=False, indent=1), encoding="utf8")
    print("\n".join(log))


if __name__ == "__main__":
    main()

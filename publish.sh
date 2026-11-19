#!/bin/zsh
# 渲染"短剧钩子库"网页并发布到 GitHub Pages(pages 分支)
cd "$(dirname "$0")" || exit 1
python3 merge_master.py || exit 1
python3 render_hooks.py || exit 1
git add library.html data
git commit -qm "更新短剧钩子库 $(date +%F)" || exit 0
git push -q origin pages

"""Publish every scheduled blog post whose date has come (Central time).

scheduled/YYYY-MM-DD/<slug>.html  -> blog/<slug>.html
scheduled/YYYY-MM-DD/card.html    -> inserted at the top of the cards on blog/index.html
sitemap.xml gets the new URL. The folder is removed. ONE folder per run at most,
oldest first, so two posts can never go out on the same day.
"""
import datetime, io, os, shutil, sys
from zoneinfo import ZoneInfo

force = os.environ.get("PUBLISH_DATE")  # test hook: pretend today is this date
if force:
    today = datetime.date.fromisoformat(force)
else:
    today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()

root = "scheduled"
if not os.path.isdir(root):
    print("nothing scheduled"); sys.exit(0)
due = sorted(d for d in os.listdir(root)
             if len(d) == 10 and d <= today.isoformat() and os.path.isdir(os.path.join(root, d)))
if not due:
    print(f"nothing due on {today}"); sys.exit(0)

d = due[0]
folder = os.path.join(root, d)
posts = [f for f in os.listdir(folder) if f.endswith(".html") and f != "card.html"]
assert len(posts) == 1, f"{folder} must hold exactly one post and card.html"
slug = posts[0][:-5]
assert not os.path.exists(f"blog/{slug}.html"), f"blog/{slug}.html already exists"

card = io.open(os.path.join(folder, "card.html"), encoding="utf-8").read()
idx = io.open("blog/index.html", encoding="utf-8").read()
marker = '<div class="cards">\n'
assert idx.count(marker) == 1, "cards marker not found once in blog/index.html"
idx = idx.replace(marker, marker + card, 1)

sm = io.open("sitemap.xml", encoding="utf-8").read()
url = f"  <url><loc>https://www.thetradegoat.com/blog/{slug}.html</loc><lastmod>{today}</lastmod></url>\n"
assert sm.count("</urlset>") == 1
sm = sm.replace("</urlset>", url + "</urlset>", 1)

shutil.move(os.path.join(folder, posts[0]), f"blog/{slug}.html")
io.open("blog/index.html", "w", encoding="utf-8", newline="").write(idx)
io.open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm)
shutil.rmtree(folder)
with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as fh:
    fh.write(f"slug={slug}\n")
print(f"published {slug} (scheduled {d})")

#!/usr/bin/env python3
"""Rebuild the "What's new" list on the home page.

Collects the newest papers (research.html), talks (talks.html), blog posts
(RSS feed) and extra items (whats-new.txt), mixes them by date, and writes
the result between the whats-new markers in index.html.

Runs automatically on GitHub (see .github/workflows/whats-new.yml).
To run it by hand:  python3 scripts/build_feed.py
Uses only the Python standard library.
"""

import datetime as dt
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---- Settings -------------------------------------------------------------

BLOG_RSS = "https://rss.beehiiv.com/feeds/MekPEcmUqs.xml"
BLOG_NAME = "professing linguistics"

MAX_PAPERS = 3      # newest papers to show
MAX_TALKS = 2       # newest talks to show
MAX_BLOG = 1        # newest blog posts to show
NEWS_MAX_AGE_DAYS = 400   # items from whats-new.txt older than this are hidden

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
RESEARCH = ROOT / "research.html"
TALKS = ROOT / "talks.html"
NEWS = ROOT / "whats-new.txt"

START = re.compile(r"(<!-- whats-new:start[^>]*-->)")
END = "<!-- whats-new:end -->"

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]
TODAY = dt.date.today()


# ---- Helpers --------------------------------------------------------------

def text(fragment):
    """HTML fragment -> plain text with tidy spaces."""
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def year_only_date(year):
    """Best guess for sorting when only the year is known: mid-year, never in the future."""
    return min(dt.date(year, 7, 1), TODAY)


def item(date, label, title, detail, link):
    return {"date": date, "label": label, "title": title,
            "detail": detail, "link": link}


# ---- Sources --------------------------------------------------------------

def papers():
    page = RESEARCH.read_text(encoding="utf-8")
    found = []
    for m in re.finditer(r'class="citation-title">\s*<a href="([^"]+)">(.*?)</a>',
                         page, re.S):
        href, inner = m.group(1), m.group(2)
        ym = re.search(r"\.\s*(\d{4})\.", inner)
        if not ym:
            continue  # "To appear" and undated items stay off the home page
        year = int(ym.group(1))
        authors = text(inner[:ym.start()])

        bm = re.search(r"<b>(.*?)</b>", inner, re.S)
        if not bm:
            continue
        title = text(bm.group(1)).rstrip(".")
        after = inner[bm.end():]
        im = re.search(r"<i>(.*?)</i>", after, re.S)
        if im:
            venue = text(im.group(1))
        else:
            venue = text(after).split(".")[0].strip(" ()")

        coauthors = coauthor_names(authors)
        detail = (f"With {join_names(coauthors)} · " if coauthors else "") + venue
        found.append(item(year_only_date(year), f"Paper · {year}", title,
                          detail, href))
    # newest year first; within a year keep the order on the Research page
    found.sort(key=lambda x: -x["date"].year)
    return found[:MAX_PAPERS]


def coauthor_names(authors):
    """'Clem, Emily, and Amy Rose Deal' -> ['Emily Clem']"""
    m = re.match(r"([^,]+),\s*([^,]+?)(?:,|$)(.*)", authors)
    if not m:
        return []
    names = [f"{m.group(2).strip()} {m.group(1).strip()}"]
    names += [n.strip() for n in re.split(r",|\band\b", m.group(3)) if n.strip()]
    return [n for n in names if n != "Amy Rose Deal"]


def join_names(names):
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def talks():
    page = TALKS.read_text(encoding="utf-8")
    found = []
    year = None
    for m in re.finditer(r'<h3[^>]*>\s*(\d{4})\s*</h3>|<li class="talk">(.*?)</li>',
                         page, re.S):
        if m.group(1):
            year = int(m.group(1))
            continue
        if year is None:
            continue
        inner = m.group(2)
        hm = re.search(r'<a href="(https?://[^"]+)"', inner)
        link = hm.group(1) if hm else "talks.html"

        t = text(inner)
        t = re.sub(r"\(\s*[^()]*?(handout|article|slides|version)[^()]*\)", "", t, flags=re.I)
        t = re.sub(r"\[[^\]]*\]", "", t)              # [A.R. Deal and J. Royer]
        t = re.sub(r"\((with [^)]*)\)", r"", t, flags=re.I)
        t = re.sub(r"\s+", " ", t).strip().rstrip(".")
        title, _, rest = t.partition(". ")
        rest = re.sub(r"\s*\.\s*", ". ", rest).strip(" .")

        date = year_only_date(year)
        label = f"Talk · {year}"
        mm = re.search(r"\b(" + "|".join(MONTHS) + r")\s+(\d{4})", rest, re.I)
        if mm:
            month = MONTHS.index(mm.group(1).lower()) + 1
            date = dt.date(int(mm.group(2)), month, 15)
            label = f"Talk · {mm.group(1)[:3].title()} {mm.group(2)}"
            rest = re.sub(r",?\s*" + re.escape(mm.group(0)), "", rest).strip(" ,")
        found.append(item(date, label, title, rest, link))
    return found[:MAX_TALKS]


def blog():
    req = urllib.request.Request(BLOG_RSS, headers={"User-Agent": "whats-new-builder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    found = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        try:
            date = dt.datetime.strptime(pub[:16], "%a, %d %b %Y").date()
        except ValueError:
            continue
        found.append(item(date, f"Blog · {date:%b %Y}", title, BLOG_NAME, link))
    found.sort(key=lambda x: x["date"], reverse=True)
    return found[:MAX_BLOG]


def news():
    found = []
    if not NEWS.exists():
        return found
    for line in NEWS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 5:
            print(f"whats-new.txt: skipping line (needs 5 parts): {line}", file=sys.stderr)
            continue
        when, label, title, detail, link = parts
        nums = [int(n) for n in when.split("-")]
        if len(nums) == 1:
            date, shown = year_only_date(nums[0]), str(nums[0])
        else:
            date = dt.date(nums[0], nums[1], nums[2] if len(nums) > 2 else 15)
            shown = f"{date:%b %Y}"
        if (TODAY - date).days > NEWS_MAX_AGE_DAYS:
            continue
        found.append(item(date, f"{label} · {shown}", title, detail, link))
    return found


# ---- Build ----------------------------------------------------------------

def render(items):
    out = ['<ul class="feed">']
    for x in items:
        out.append(
            '    <li><a href="{link}"><span class="kind">{label}</span>'
            '<span class="item"><span class="title">{title}</span>'
            '<span class="meta">{detail}</span></span></a></li>'.format(
                **{k: html.escape(str(v)) for k, v in x.items()}))
    out.append("</ul>")
    indent = " " * 16
    return "\n".join(indent + line for line in out)


def main():
    try:
        blog_items = blog()
    except Exception as exc:  # network trouble: leave the page as it is
        print(f"Could not read the blog feed ({exc}); leaving the page unchanged.",
              file=sys.stderr)
        return 0

    items = papers() + talks() + blog_items + news()
    items.sort(key=lambda x: x["date"], reverse=True)

    page = INDEX.read_text(encoding="utf-8")
    m = START.search(page)
    end = page.find(END)
    if not m or end < 0:
        print("index.html: whats-new markers not found", file=sys.stderr)
        return 1
    new_page = page[:m.end()] + "\n" + render(items) + "\n" + " " * 16 + page[end:]
    if new_page != page:
        INDEX.write_text(new_page, encoding="utf-8")
        print(f"Updated What's new with {len(items)} items.")
    else:
        print("What's new is already up to date.")
    for x in items:
        print(f"  {x['date']}  {x['label']:<18} {x['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

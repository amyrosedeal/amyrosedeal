#!/usr/bin/env python3
"""Rebuild the website's lists from the CV.

Reads cv/cv-full.tex (plus cv/website-only.tex) and writes:
  - the paper list on research.html   (between the papers: markers)
  - the talk list on talks.html       (between the talks: markers)
  - the "What's new" list on index.html (papers + talks + blog + whats-new.txt)

Runs automatically on GitHub (.github/workflows/update-site.yml).
By hand:  python3 scripts/build_site.py
Uses only the Python standard library.
"""

import datetime as dt
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cvparse  # noqa: E402

# ---- Settings -------------------------------------------------------------

BLOG_RSS = "https://rss.beehiiv.com/feeds/MekPEcmUqs.xml"
BLOG_NAME = "professing linguistics"

FEED_PAPERS = 3     # newest papers on the home page
FEED_TALKS = 2      # most recent talks on the home page
FEED_BLOG = 1       # newest blog posts on the home page
NEWS_MAX_AGE_DAYS = 400

ROOT = Path(__file__).resolve().parent.parent
CV = ROOT / "cv" / "cv-full.tex"
EXTRA_PAPERS = ROOT / "cv" / "website-only.tex"   # papers shown on the site but not in the CV
TALKS_FROM = 2016                                 # earliest year of talks listed on the site
INDEX = ROOT / "index.html"
RESEARCH = ROOT / "research.html"
TALKS = ROOT / "talks.html"
NEWS = ROOT / "whats-new.txt"

TODAY = dt.date.today()
MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
              "Oct", "Nov", "Dec"]


# ---- Helpers --------------------------------------------------------------

def replace_between(path, name, content, indent=""):
    """Swap the text between <!-- name:start ... --> and <!-- name:end -->."""
    page = path.read_text(encoding="utf-8")
    m = re.search(r"<!-- " + name + r":start[^>]*-->", page)
    end = page.find("<!-- " + name + ":end -->")
    if not m or end < 0:
        raise SystemExit(f"{path.name}: {name} markers not found")
    new = page[:m.end()] + "\n" + content + "\n" + indent + page[end:]
    if new != page:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def esc(s):
    return html.escape(str(s), quote=True)


def mid_year(year):
    return min(dt.date(year, 7, 1), TODAY)


# ---- Research page --------------------------------------------------------

def research_html(pubs):
    rows = []
    for p in sorted((p for p in pubs if not p["hide"]), key=lambda p: -p["year_value"]):
        title = p["title"]
        title = title + ("" if title.endswith(("?", "!", "?</i>")) else ".")
        cite = f'{p["authors"]}. {p["year"]}. <b>{title}</b> {p["rest"]}'.strip()
        if p["link"]:
            cite = f'<a href="{esc(p["link"])}">{cite}</a>'
        doi = f' <a class="citation-doi" href="{esc(p["doi"])}">DOI</a>' if p["doi"] and p["doi"] != p["link"] else ""
        classes = " ".join(["paper", "citation-item"] + p["tags"])
        rows.append(
            f'                    <div class="{classes}">\n'
            f'                        <div class="citation-block">\n'
            f'                            <span class="citation-title">{cite}{doi}</span>\n'
            f'                        </div>\n'
            f'                    </div>\n')
    return "\n".join(rows)


# ---- Talks page -----------------------------------------------------------

def talk_line(t):
    title = "Title to be announced" if t["tba"] else t["title"]
    head = title if title.endswith(("?", "!")) else title + "."
    extra = []
    if t["with"]:
        extra.append(f'with {", ".join(t["with"])}')
    if t["handout"]:
        extra.append(f'<a href="{esc(t["handout"])}">handout</a>')
    if extra:
        head += f' <span class="talk-note">({"; ".join(extra)})</span>'
    month_end = re.compile(r"\b(" + "|".join(cvparse.MONTHS) + r")\.?(\s*\([^)]*\))?$", re.I)
    venues = "".join(
        f"<span>{month_end.sub(lambda m: m.group(1) + ' ' + str(t['year']) + (m.group(2) or ''), v)}</span>"
        for v in t["venues"])
    return head + (f'<span class="talk-venues">{venues}</span>' if venues else "")


TALK_STYLE = """                    <style>
                        li.talk h4 { line-height: 1.45; margin-bottom: 14px; }
                        .talk-note { color: #666; font-size: .9em; }
                        .talk-venues { display: block; margin-top: 2px; color: #666; font-size: .88em; }
                        .talk-venues span { display: block; }
                    </style>"""


def talks_html(talks):
    now = (TODAY.year, TODAY.month)
    shown = [t for t in talks if not t["hide"]]
    upcoming = sorted((t for t in shown if t["latest"] > now), key=lambda t: t["latest"])
    past = sorted((t for t in shown if t["latest"] <= now), key=lambda t: t["latest"], reverse=True)

    groups = []
    if upcoming:
        groups.append(("Upcoming", upcoming))
    years = []
    for t in past:
        y = t["latest"][0]
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(t)
    groups.extend((str(y), ts) for y, ts in years)

    out = [TALK_STYLE]
    for label, ts in groups:
        out.append(f'                    <h3 class="text-uppercase">{label}</h3>')
        out.append('                    <ul class="course">')
        for t in ts:
            out.append(f'                        <li class="talk"><h4>{talk_line(t)}</h4></li>')
        out.append('                    </ul>')
        out.append('                    <div class="h-30"></div>')
    return "\n".join(out)


# ---- What's new (home page) ----------------------------------------------

def item(date, label, title, detail, link):
    return {"date": date, "label": label, "title": title, "detail": detail, "link": link}


def coauthors(authors_html):
    """'Clem, Emily and Amy Rose Deal' -> ['Emily Clem']"""
    a = cvparse.plain(authors_html)
    m = re.match(r"([^,]+),\s*([^,]+?)(?:,|\band\b|$)(.*)", a)
    if not m:
        return []
    first = f"{m.group(2).strip()} {m.group(1).strip()}"
    others = [n.strip() for n in re.split(r",|\band\b|&", m.group(3)) if n.strip()]
    return [n for n in [first] + others if n != "Amy Rose Deal"]


def join_names(names):
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def feed_papers(pubs):
    dated = [p for p in pubs if not p["hide"] and p["year_value"] != 9999]
    dated.sort(key=lambda p: -p["year_value"])
    out = []
    for p in dated[:FEED_PAPERS]:
        im = re.search(r"<i>(.*?)</i>", p["rest"])
        venue = cvparse.plain(im.group(1)) if im else cvparse.plain(p["rest"]).split(".")[0]
        names = coauthors(p["authors"])
        detail = (f"With {join_names(names)} · " if names else "") + venue
        label = "Paper" if p["kind"] != "Manuscript" else "Manuscript"
        out.append(item(mid_year(p["year_value"]), f"{label} · {p['year_value']}",
                        cvparse.plain(p["title"]), detail,
                        p["link"] or "research.html"))
    return out


def feed_talks(talks):
    now = (TODAY.year, TODAY.month)
    past = [t for t in talks if not t["hide"] and not t["tba"] and t["latest"] <= now]
    past.sort(key=lambda t: t["latest"], reverse=True)
    out = []
    for t in past[:FEED_TALKS]:
        y, m = t["latest"]
        date = dt.date(y, m or 7, 15)
        label = f"Talk · {MONTH_ABBR[m]} {y}" if m else f"Talk · {y}"
        venue = cvparse.plain(t["venues"][0]) if t["venues"] else ""
        venue = re.sub(r",?\s*(" + "|".join(cvparse.MONTHS) + r")\b\.?(\s+\d{4})?", "", venue, flags=re.I).strip(" ,")
        if t["with"]:
            venue = f"With {join_names(t['with'])} · {venue}"
        out.append(item(date, label, cvparse.plain(t["title"]), venue, t["handout"] or "talks.html"))
    return out


def feed_blog():
    req = urllib.request.Request(BLOG_RSS, headers={"User-Agent": "site-builder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    found = []
    for it in root.iter("item"):
        pub = (it.findtext("pubDate") or "").strip()
        try:
            date = dt.datetime.strptime(pub[:16], "%a, %d %b %Y").date()
        except ValueError:
            continue
        found.append(item(date, f"Blog · {date:%b %Y}", (it.findtext("title") or "").strip(),
                          BLOG_NAME, (it.findtext("link") or "").strip()))
    found.sort(key=lambda x: x["date"], reverse=True)
    return found[:FEED_BLOG]


def feed_news():
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
            date, shown = mid_year(nums[0]), str(nums[0])
        else:
            date = dt.date(nums[0], nums[1], nums[2] if len(nums) > 2 else 15)
            shown = f"{date:%b %Y}"
        if (TODAY - date).days <= NEWS_MAX_AGE_DAYS:
            found.append(item(date, f"{label} · {shown}", title, detail, link))
    return found


def feed_html(items):
    out = ['                <ul class="feed">']
    for x in items:
        out.append(
            '                    <li><a href="{link}"><span class="kind">{label}</span>'
            '<span class="item"><span class="title">{title}</span>'
            '<span class="meta">{detail}</span></span></a></li>'.format(
                **{k: esc(v) for k, v in x.items()}))
    out.append("                </ul>")
    return "\n".join(out)


# ---- Main -----------------------------------------------------------------

def main():
    pubs, talks = cvparse.load(CV)
    if EXTRA_PAPERS.exists():
        pubs += cvparse.parse_publications(EXTRA_PAPERS.read_text(encoding="utf-8"))
    talks = [t for t in talks if t["latest"][0] >= TALKS_FROM]
    print(f"CV: {len(pubs)} publications, {len(talks)} talks")

    changed = replace_between(RESEARCH, "papers", research_html(pubs), "")
    changed |= replace_between(TALKS, "talks", talks_html(talks), "")

    items = feed_papers(pubs) + feed_talks(talks) + feed_news()
    try:
        items += feed_blog()
        update_feed = True
    except Exception as exc:   # blog unreachable: keep the home page as it is
        print(f"Could not read the blog feed ({exc}); leaving What's new unchanged.",
              file=sys.stderr)
        update_feed = False
    if update_feed:
        items.sort(key=lambda x: x["date"], reverse=True)
        changed |= replace_between(INDEX, "whats-new", feed_html(items), " " * 16)
        for x in items:
            print(f"  {x['date']}  {x['label']:<18} {x['title']}")

    print("Pages updated." if changed else "Pages already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

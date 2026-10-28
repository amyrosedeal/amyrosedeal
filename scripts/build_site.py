#!/usr/bin/env python3
"""Rebuild the website's lists from the CV.

Reads cv/cv-full.tex (plus cv/website-only.tex) and writes:
  - the paper list on research.html   (between the papers: markers)
  - the talk list on talks.html       (between the talks: markers)
  - the "What's new" list on index.html (papers + talks + blog + whats-new.txt)
  - the course list on teaching.html  (between the teaching: markers)

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
TALKS_OPEN_YEARS = 3      # Talks page: this many recent years shown open, older ones folded (None = all open)
INDEX = ROOT / "index.html"
RESEARCH = ROOT / "research.html"
TALKS = ROOT / "talks.html"
TEACHING = ROOT / "teaching.html"
HOME_PLACE = "UC Berkeley"    # Teaching page: courses here don't name the institution
NEWS = ROOT / "whats-new.txt"
ACCEPTED = ROOT / "accepted-dates.txt"           # when each "To appear" paper was first seen (kept by this script)

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

TOPICS = [  # (tag in the CV, label in the dropdown, group)
    ("syntax", "Syntax", "Area"), ("semantics", "Semantics", "Area"),
    ("morphology", "Morphology", "Area"), ("typ", "Typology", "Area"),
    ("nzp", "Nez Perce", "Area"),
    ("case-agr", "Case & agreement", "Topic"), ("extposs", "Possession", "Topic"),
    ("locality", "Locality", "Topic"), ("mass", "Number & countability", "Topic"),
    ("perspective", "Attitudes & perspective", "Topic"), ("modality", "Modality", "Topic"),
]
TOPIC_LABEL = {t: label for t, label, _ in TOPICS}
KIND_LABEL = {"Monograph": "Book", "Journal article": "Journal article",
              "Manuscript": "Manuscript", "Chapter or proceedings paper": "Chapter / proceedings"}


def author_list(authors_html):
    """'Clem, Emily and Amy Rose Deal' -> 'Emily Clem and Amy Rose Deal' ('' if solo)."""
    a = cvparse.plain(authors_html)
    m = re.match(r"([^,]+),\s*([^,]+?)(?:,|\band\b|$)(.*)", a)
    if not m:
        return ""
    names = [f"{m.group(2).strip()} {m.group(1).strip()}"]
    names += [n.strip() for n in re.split(r",|\band\b|&", m.group(3)) if n.strip()]
    if names == ["Amy Rose Deal"]:
        return ""
    return join_names(names)


def link_label(url):
    u = url.lower()
    if "doi.org" in u:
        return "DOI"
    if "lingbuzz" in u:
        return "lingbuzz"
    if u.endswith(".pdf"):
        return "PDF"
    if "escholarship" in u:
        return "eScholarship"
    return "Article"


def pub_entry(p, heading="h3", compact=False):
    """compact: manuscripts in the pipeline show only label, title, authors and link."""
    title = p["title"]
    title_html = f'<a href="{esc(p["link"])}">{title}</a>' if p["link"] else title
    kind = KIND_LABEL.get(p["kind"], p["kind"])
    if p["year_value"] == 9999:
        kind += " · forthcoming"
    authors = author_list(p["authors"])
    venue = p["rest"].strip().rstrip(".")
    links = []
    if p["link"]:
        links.append(p["link"])
    if p["doi"] and p["doi"] not in links:
        links.append(p["doi"])
    chips = "".join(f'<a class="chip" href="{esc(u)}">{link_label(u)}</a>' for u in links)
    topics = ""   # topic tags drive the filter but aren't shown on the cards
    if compact:
        venue, topics = "", ""
    lines = [f'<article class="pub" data-tags="{esc(" ".join(p["tags"]))}">',
             f'  <p class="pub-kind">{kind}</p>']
    lines.append(f'  <{heading} class="pub-title">{title_html}</{heading}>')
    if authors:
        lines.append(f'  <p class="pub-authors">{authors}</p>')
    if venue:
        lines.append(f'  <p class="pub-venue">{venue}</p>')
    if chips or topics:
        lines.append(f'  <p class="pub-links">{chips}'
                     + (f'<span class="pub-topics">{esc(topics)}</span>' if topics else "") + "</p>")
    lines.append("</article>")
    return "\n".join("            " + l for l in lines)


def research_html(pubs):
    shown = [p for p in pubs if not p["hide"]]
    out = []

    selected = [p for p in shown if p["selected"]]
    if selected:
        def place(p):
            try:
                return int(p["selected"])
            except (TypeError, ValueError):
                return 999
        selected.sort(key=place)
        out.append('        <section class="selected-work" aria-labelledby="selected-heading">')
        out.append('            <h2 id="selected-heading">Selected work</h2>')
        out.append('            <div class="selected-grid">')
        out += [pub_entry(p) for p in selected]
        out.append("            </div>")
        out.append("        </section>")

    options = ['                <option value="">All topics</option>']
    for group in ("Area", "Topic"):
        options.append(f'                <optgroup label="{group}">')
        for tag, label, g in TOPICS:
            if g == group:
                options.append(f'                    <option value="{tag}">{esc(label)}</option>')
        options.append("                </optgroup>")
    out.append('        <div class="filter-bar">')
    out.append('            <label for="topic">Filter by topic</label>')
    out.append('            <select id="topic">')
    out += options
    out.append("            </select>")
    out.append('            <span class="filter-count" id="filter-count" aria-live="polite"></span>')
    out.append("        </div>")

    # "In the pipeline": the CV's Manuscripts section plus anything forthcoming
    # (old manuscripts kept in website-only.tex stay under their year)
    manuscripts = [p for p in shown if p["kind"] == "Manuscript"
                   and not cvparse.plain(p["rest"]).lower().startswith("manuscript")]
    forthcoming = [p for p in shown if p["year_value"] == 9999 and p not in manuscripts]
    rest = [p for p in shown if p not in manuscripts and p not in forthcoming]

    groups = []
    if manuscripts or forthcoming:
        groups.append(("In the pipeline", "pipeline",
                       [(p, True) for p in manuscripts] + [(p, False) for p in forthcoming]))
    by_year = {}
    for p in sorted(rest, key=lambda p: -p["year_value"]):
        by_year.setdefault(str(p["year_value"]), []).append((p, False))
    groups += [(k, k, v) for k, v in by_year.items()]

    for label, gid, items in groups:
        out.append(f'        <section class="pub-year" id="y-{gid}">')
        out.append(f"            <h2>{label}</h2>")
        out += [pub_entry(p, compact=c) for p, c in items]
        out.append("        </section>")
    return "\n".join(out)


# ---- Talks page -----------------------------------------------------------

_DATE_END = re.compile(r",?\s*\b(" + "|".join(cvparse.MONTHS) + r")\b\.?(?:\s+(\d{4}))?\s*(\((?:remote|virtual|online)\))?$", re.I)


def split_venue(v, year):
    """'Colloquium, MIT, March' -> ('Colloquium, MIT', 'March 2025', '')."""
    m = _DATE_END.search(v)
    if not m:
        return v, "", ""
    month = m.group(1).capitalize()
    when = f"{month} {m.group(2) or year}"
    return v[:m.start()].rstrip(" ,"), when, (m.group(3) or "").strip("() ")


def merge_same_title(talks):
    """One entry per title per year: the CV may list a talk under both
    'By invitation' and 'By reviewed abstract'."""
    out, seen = [], {}
    for t in talks:
        key = (cvparse.plain(t["title"]).lower(), t["latest"][0])
        if key in seen and not t["tba"]:
            first = seen[key]
            first["venues"] = first["venues"] + t["venues"]
            first["with"] = first["with"] or t["with"]
            first["notes"] = first["notes"] + [n for n in t["notes"] if n not in first["notes"]]
            first["handout"] = first["handout"] or t["handout"]
            first["latest"] = max(first["latest"], t["latest"])
            continue
        seen[key] = t
        out.append(t)
    for t in out:
        t["venues"].sort(key=lambda v: max(cvparse._dates_in(cvparse.plain(v), t["year"]) or [(0, 0)]),
                         reverse=True)
    return out


def talk_html(t, pad):
    if t["tba"]:          # no title yet: show just the date and venue
        lines = [f'{pad}<article class="talk talk-untitled">']
    else:
        lines = [f'{pad}<article class="talk">',
                 f'{pad}  <h3 class="talk-title">{t["title"]}</h3>']
    meta = []
    if t["with"]:
        meta.append("With " + join_names(t["with"]))
    meta += [n[:1].upper() + n[1:] for n in t["notes"]]
    if meta:
        lines.append(f'{pad}  <p class="talk-with">{" · ".join(meta)}</p>')
    if t["venues"]:
        lines.append(f'{pad}  <ul class="talk-venues">')
        for v in t["venues"]:
            place, when, remote = split_venue(v, t["year"])
            if remote:
                place += ' <span class="talk-remote">(remote)</span>'
            lines.append(f'{pad}    <li><span class="talk-date">{when}</span><span class="talk-place">{place}</span></li>')
        lines.append(f'{pad}  </ul>')
    if t["handout"]:
        lines.append(f'{pad}  <p class="pub-links"><a class="chip" href="{esc(t["handout"])}">Handout</a></p>')
    lines.append(f'{pad}</article>')
    return "\n".join(lines)


def talks_html(talks):
    now = (TODAY.year, TODAY.month)
    shown = merge_same_title([t for t in talks if not t["hide"]])

    # A talk given in several years appears under each year, with that year's venues.
    pieces = []
    for t in shown:
        groups = {}
        for v in t["venues"]:
            d = max(cvparse._dates_in(cvparse.plain(v), t["year"]) or [(t["year"], 0)])
            if d[0] < TALKS_FROM:
                continue
            key = "upcoming" if d > now else d[0]
            groups.setdefault(key, []).append((d, v))
        if not t["venues"]:
            groups[t["latest"][0]] = [(t["latest"], None)]
        for key, vs in groups.items():
            piece = dict(t, venues=[v for _, v in vs if v is not None], latest=max(d for d, _ in vs))
            pieces.append(piece)
    upcoming = sorted((t for t in pieces if t["latest"] > now), key=lambda t: t["latest"])
    past = sorted((t for t in pieces if t["latest"] <= now), key=lambda t: t["latest"], reverse=True)

    years = []
    for t in past:
        y = t["latest"][0]
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(t)

    out = []
    pad = "        "
    if TALKS_OPEN_YEARS is None and years:
        jumps = ([('upcoming', 'Upcoming')] if upcoming else []) + [(f"y-{y}", str(y)) for y, _ in years]
        out.append(f'{pad}<nav class="year-nav" aria-label="Years"><span>Jump to</span>'
                   + "".join(f'<a href="#{i}">{label}</a>' for i, label in jumps) + '</nav>')
    if upcoming:
        out.append(f'{pad}<section class="talk-year upcoming" id="upcoming">')
        out.append(f'{pad}    <h2>Upcoming</h2>')
        out += [talk_html(t, pad + "    ") for t in upcoming]
        out.append(f'{pad}</section>')
    open_years = len(years) if TALKS_OPEN_YEARS is None else TALKS_OPEN_YEARS
    for i, (y, ts) in enumerate(years):
        body = [talk_html(t, pad + "    ") for t in ts]
        if i < open_years:
            out.append(f'{pad}<section class="talk-year" id="y-{y}">')
            out.append(f'{pad}    <h2>{y}</h2>')
            out += body
            out.append(f'{pad}</section>')
        else:
            if i == open_years:
                out.append(f'{pad}<h2 class="earlier-head">Earlier talks</h2>')
            n = f'{len(ts)} talk' + ("" if len(ts) == 1 else "s")
            out.append(f'{pad}<details class="talk-year" id="y-{y}">')
            out.append(f'{pad}    <summary><span class="year">{y}</span><span class="count">{n}</span></summary>')
            out += body
            out.append(f'{pad}</details>')
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


def accepted_dates(pubs):
    """Date each "To appear" paper was accepted, for What's new.

    A `% web: accepted=2026-10` line in the CV gives the date directly.
    Otherwise the date is the day the website first saw the paper marked
    "To appear"; those dates are kept in accepted-dates.txt.
    """
    known = {}
    lines = ACCEPTED.read_text(encoding="utf-8").splitlines() if ACCEPTED.exists() else []
    for line in lines:
        if line.strip() and not line.startswith("#") and "|" in line:
            when, title = (x.strip() for x in line.split("|", 1))
            known[title.lower()] = when
    added = []
    out = {}
    for p in pubs:
        if p["year_value"] != 9999 or p["hide"]:
            continue
        title = cvparse.plain(p["title"])
        when = p.get("accepted") or known.get(title.lower())
        if when is None:
            when = TODAY.isoformat()
            known[title.lower()] = when
            added.append(f"{when} | {title}")
        nums = [int(n) for n in re.findall(r"\d+", when)]
        if nums:   # "-" means: accepted before the website kept track; not shown
            out[id(p)] = dt.date(nums[0], nums[1] if len(nums) > 1 else 7, nums[2] if len(nums) > 2 else 15)
    if added:
        if not lines:
            lines = ["# When each \"To appear\" paper was first seen on the website (written automatically).",
                     "# It decides when an accepted paper shows up in What's new. A '-' means the date is unknown",
                     "# and the paper isn't listed there. A `% web: accepted=2026-10` line in the CV overrides this.",
                     ""]
        ACCEPTED.write_text("\n".join(lines + added) + "\n", encoding="utf-8")
        for a in added:
            print(f"  newly accepted: {a}")
    return out


def feed_papers(pubs):
    accepted = accepted_dates(pubs)
    candidates = []      # (date, paper); a stable sort keeps CV order within a year
    for p in pubs:
        if p["hide"]:
            continue
        if p["year_value"] == 9999:
            if id(p) in accepted:
                candidates.append((accepted[id(p)], p))
        else:
            candidates.append((mid_year(p["year_value"]), p))
    candidates.sort(key=lambda x: x[0], reverse=True)
    out = []
    for date, p in candidates[:FEED_PAPERS]:
        im = re.search(r"<i>(.*?)</i>", p["rest"])
        venue = cvparse.plain(im.group(1)) if im else cvparse.plain(p["rest"]).split(".")[0]
        names = coauthors(p["authors"])
        if p["year_value"] == 9999:
            venue = ("To appear in " + venue) if venue else "To appear"
            label = f"Accepted · {date:%b %Y}"
        else:
            label = ("Paper" if p["kind"] != "Manuscript" else "Manuscript") + f" · {p['year_value']}"
        detail = (f"With {join_names(names)} · " if names else "") + venue
        out.append(item(date, label, cvparse.plain(p["title"]), detail, p["link"] or "research.html"))
    return out


def feed_talks(talks):
    now = (TODAY.year, TODAY.month)
    # each talk counts from its most recent venue that has already happened
    # (this month or earlier); talks still titled TBA are left out
    past = []
    for t in talks:
        if t["hide"] or t["tba"]:
            continue
        dated = [(max(cvparse._dates_in(cvparse.plain(v), t["year"]) or [(t["year"], 0)]), v)
                 for v in t["venues"]] or [(t["latest"], "")]
        done = [(d, v) for d, v in dated if d <= now]
        if done:
            past.append((max(done, key=lambda x: x[0]), t))
    past.sort(key=lambda x: x[0][0], reverse=True)
    out = []
    for ((y, m), venue), t in past[:FEED_TALKS]:
        date = dt.date(y, m or 7, 15)
        label = f"Talk · {MONTH_ABBR[m]} {y}" if m else f"Talk · {y}"
        venue = cvparse.plain(venue)
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

# ---- Teaching page --------------------------------------------------------

def teaching_html(courses):
    years = {}
    for i, c in enumerate(courses):
        by_ay = {}
        for o in c["offerings"]:
            by_ay.setdefault(o["ay"], []).append(o)
        for ay, offs in by_ay.items():
            offs.sort(key=lambda o: o["order"])
            years.setdefault(ay, []).append((max(o["order"] for o in offs), -i, c, offs))
    if not years:
        return ""
    order = sorted(years, reverse=True)
    pad = " " * 8
    out = [pad + '<nav class="year-nav" aria-label="Academic years">',
           pad + "    <span>Jump to</span>"]
    for ay in order:
        out.append(f'{pad}    <a href="#y{ay % 100:02d}-{(ay + 1) % 100:02d}">{ay}–{(ay + 1) % 100:02d}</a>')
    out += [pad + "</nav>", "", pad + '<div class="prose">']
    for ay in order:
        out += [f'{pad}    <section class="course-year" id="y{ay % 100:02d}-{(ay + 1) % 100:02d}">',
                f"{pad}        <h2>{ay}–{ay + 1}</h2>",
                f'{pad}        <ul class="courses">']
        for _, _, c, offs in sorted(years[ay], key=lambda x: (x[0], x[1]), reverse=True):
            if c["kind"] == "short":
                meta = "Short course · " + c["detail"]
            else:
                bits = []
                if c["place"] and c["place"] != HOME_PLACE:
                    bits.append(esc(c["place"]))
                bits.append(", ".join(x for x in (c["number"], c["level"]) if x))
                terms = []
                for o in offs:
                    terms.append(o["term"] + (f" (with {esc(o['with'])})" if o["with"] else ""))
                bits.append(" and ".join(terms))
                meta = " · ".join(b for b in bits if b)
            out += [f"{pad}            <li>",
                    f'{pad}                <span class="course-title">{c["title"]}</span>',
                    f'{pad}                <span class="course-meta">{meta}</span>',
                    f"{pad}            </li>"]
        out += [f"{pad}        </ul>", f"{pad}    </section>"]
    out.append(pad + "</div>")
    return "\n".join(out)


def main():
    pubs, talks = cvparse.load(CV)
    if EXTRA_PAPERS.exists():
        pubs += cvparse.parse_publications(EXTRA_PAPERS.read_text(encoding="utf-8"))
    talks = [t for t in talks if t["latest"][0] >= TALKS_FROM]
    print(f"CV: {len(pubs)} publications, {len(talks)} talks")

    changed = replace_between(RESEARCH, "papers", research_html(pubs), "")
    changed |= replace_between(TALKS, "talks", talks_html(talks), "")
    courses = cvparse.parse_teaching(CV.read_text(encoding="utf-8"))
    print(f"CV: {len(courses)} courses")
    changed |= replace_between(TEACHING, "teaching", teaching_html(courses), " " * 8)

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

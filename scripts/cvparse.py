"""Read papers and talks out of the CV's LaTeX source (cv/cv-full.tex).

The CV stays an ordinary LaTeX file. Two optional comment lines, which never
show in the PDF, add website-only details right after an entry:

    % web: link=https://ling.auf.net/lingbuzz/007429; tags=syntax, case-agr
    % web: handout=https://.../handout.pdf          (for talks)
    % web: hide                                      (keep an entry off the website)
    % web: selected   or   % web: selected=1           (show under Selected work)
"""

import html
import re

MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]

PUB_SECTIONS = {
    "monograph": "Monograph",
    "journal articles": "Journal article",
    "manuscripts": "Manuscript",
    "other publications": "Chapter or proceedings paper",
}


# ---------------------------------------------------------------------------
# LaTeX -> HTML for the small subset used in the CV
# ---------------------------------------------------------------------------

ACCENTS = {"'": "\u0301", "`": "\u0300", '"': "\u0308", "^": "\u0302",
           "~": "\u0303", "=": "\u0304", ".": "\u0307", "c": "\u0327",
           "v": "\u030c", "u": "\u0306", "H": "\u030b"}
SYMBOLS = {r"\o": "ø", r"\O": "Ø", r"\ss": "ß", r"\ae": "æ", r"\AE": "Æ",
           r"\aa": "å", r"\AA": "Å", r"\l": "ł", r"\L": "Ł", r"\i": "ı",
           r"\&": "&amp;", r"\%": "%", r"\_": "_", r"\#": "#", r"\$": "$",
           r"\phi": "φ", r"\varphi": "φ", r"\rhd": "", r"\sim": "~",
           r"\ldots": "…", r"\dots": "…"}


def _group(s, i):
    """s[i] == '{' -> (content, index after the matching '}')."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    return s[i + 1:], len(s)


def strip_comments(line):
    """Remove an unescaped % comment from one line."""
    m = re.search(r"(?<!\\)%", line)
    return line[:m.start()] if m else line


def tex_to_html(s, links=None):
    """Convert a CV snippet to HTML. URLs from \\href are appended to `links`."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name.isalpha():      # TeX swallows spaces after a control word
                while i < len(s) and s[i] == " " and name not in ("emph", "textit", "textsl", "textbf"):
                    i += 1
            if name in ("emph", "textit", "textsl"):
                while i < len(s) and s[i] == " ":
                    i += 1
                if i < len(s) and s[i] == "{":
                    inner, i = _group(s, i)
                    out.append("<i>" + tex_to_html(inner, links) + "</i>")
                continue
            if name in ("textbf",):
                inner, i = _group(s, i)
                out.append("<b>" + tex_to_html(inner, links) + "</b>")
                continue
            if name in ("textsc", "textrm", "mbox", "text"):
                inner, i = _group(s, i)
                out.append(tex_to_html(inner, links))
                continue
            if name == "href":
                url, i = _group(s, i)
                label, i = _group(s, i)
                url = re.sub(r"\s+", "", url)
                if links is not None:
                    links.append(url)
                out.append(tex_to_html(label, links))
                continue
            if name == "url":
                url, i = _group(s, i)
                if links is not None:
                    links.append(re.sub(r"\s+", "", url))
                out.append(html.escape(url))
                continue
            if name in ACCENTS and len(name) == 1 or name in ("c", "v", "u", "H"):
                if i < len(s) and s[i] == "{":
                    inner, i = _group(s, i)
                else:
                    while i < len(s) and s[i] == " " and name.isalpha():
                        i += 1
                    inner, i = s[i:i + 1], i + 1
                base = SYMBOLS.get(inner, inner).replace("\\i", "ı")
                if base == "ı":
                    base = "i"
                out.append(base + ACCENTS[name])
                continue
            key = "\\" + name
            if key in SYMBOLS:
                out.append(SYMBOLS[key])
                if name.isalpha() and i < len(s) and s[i] == "{" and s[i + 1:i + 2] == "}":
                    i += 2
                continue
            if name in ("\\", "newline", "par", "medskip", "bigskip", "smallskip"):
                out.append(" ")
                continue
            # \new, \vspace{..}, \hspace{..} and anything unknown: drop it
            if name in ("vspace", "hspace") and i < len(s) and s[i] == "{":
                _, i = _group(s, i)
            continue
        if c in "{}$":
            i += 1
            continue
        if s.startswith("---", i):
            out.append("—"); i += 3; continue
        if s.startswith("--", i):
            out.append("–"); i += 2; continue
        if s.startswith("``", i):
            out.append("“"); i += 2; continue
        if s.startswith("''", i):
            out.append("”"); i += 2; continue
        if c == "~":
            out.append(" "); i += 1; continue
        out.append(html.escape(c))
        i += 1
    text = "".join(out)
    import unicodedata
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def plain(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()


def parse_web(line):
    """'% web: link=...; tags=a, b' -> dict"""
    body = line.split("web:", 1)[1].strip()
    info = {}
    for part in body.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            info[k.strip().lower()] = v.strip()
        else:
            info[part.lower()] = True
    if "tags" in info:
        info["tags"] = [t.strip() for t in info["tags"].replace(",", " ").split() if t.strip()]
    return info


def _block(src, start_pat, end_pat):
    m = re.search(start_pat, src)
    e = re.search(end_pat, src[m.end():])
    return src[m.end(): m.end() + e.start()]


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------

YEAR_RE = re.compile(r"^(.*?)\.\s*((?:\d{4}/)?\d{4}[a-z]?|To appear|In press|In prep\.?|Forthcoming)\.\s*(.*)$",
                     re.S | re.I)


def _split_title(rest):
    """LaTeX after 'Year. ' -> (title_tex, remainder_tex)."""
    rest = rest.strip()
    # A title that is one braced or \emph{...} group ending in a period
    m = re.match(r"(\\emph|\\textit)?\s*\{", rest)
    if m:
        inner, end = _group(rest, m.end() - 1)
        inner_s = inner.rstrip()
        after = rest[end:].lstrip()
        ends_title = inner_s.endswith((".", "!")) or (
            inner_s.endswith("?") and (after == "" or after.startswith(("\\", "In "))))
        if ends_title:
            title = "\\emph{" + inner + "}" if m.group(1) else inner
            return title, rest[end:]
    # Otherwise: up to the first '. ' / '? ' outside braces
    depth = 0
    for j, c in enumerate(rest):
        if c == "{" and (j == 0 or rest[j - 1] != "\\"):
            depth += 1
        elif c == "}" and rest[j - 1] != "\\":
            depth -= 1
        elif depth == 0 and c in ".?!" and (j + 1 == len(rest) or rest[j + 1] in " \n"):
            if c == "." and re.search(r"\b(?:[A-Z]|ed|eds|vol|no|pp|St)$", rest[:j]):
                continue
            if c == "?" and not re.match(r"\s*(\\|In |$)", rest[j + 1:]):
                continue    # "Do all languages ...? Evidence from ..." keeps going
            return rest[:j + (1 if c in "?!" else 0)], rest[j + 1:]
    return rest, ""


DOI_RE = re.compile(r"(?:https?://(?:dx\.)?doi\.org/|\bdoi:\s*)(10\.\d{4,9}/[^\s{}]+)", re.I)


def find_doi(links, tex):
    """A DOI written as \\href, \\url, plain https://doi.org/..., or doi:10.... -> https://doi.org/..."""
    for u in links:
        m = DOI_RE.search(u)
        if m:
            return "https://doi.org/" + m.group(1).rstrip(".,;")
    m = DOI_RE.search(tex.replace("\\_", "_"))
    if m:
        return "https://doi.org/" + m.group(1).rstrip(".,;")
    return None


def _year_value(y):
    m = re.findall(r"\d{4}", y)
    return int(m[-1]) if m else 9999   # "To appear" sorts as newest


def parse_publications(src):
    block = _block(src, r"\\marginhead\{[^\n]*Publications\}", r"\\marginhead\{")
    pubs = []
    section = None
    current = None
    buf = []

    def finish():
        nonlocal current, buf
        if current is not None:
            current["tex"] = " ".join(buf).strip()
            pubs.append(current)
        current, buf = None, []

    for raw in block.splitlines():
        stripped = raw.strip()
        if stripped.startswith("%"):
            if re.match(r"%\s*web:", stripped) and current is not None:
                current["web"].update(parse_web(stripped))
            continue
        line = strip_comments(raw)
        hm = re.search(r"\\noindent\\emph\{\s*([^\\}]+?)\s*(?:\\vspace|\})", line)
        if hm:
            finish()
            name = hm.group(1).strip().lower()
            section = PUB_SECTIONS.get(name)
            continue
        if re.search(r"\\end\{(itemize|enumerate|benumerate)\}", line):
            finish()
            continue
        im = re.search(r"\\item(\[\])?", line)
        if im:
            finish()
            if section:
                current = {"section": section, "web": {}}
                buf = [line[im.end():]]
            continue
        if current is not None:
            buf.append(line)
    finish()

    out = []
    for p in pubs:
        tex = re.sub(r"\\new\b", "", p["tex"]).strip()
        m = YEAR_RE.match(tex)
        if not m:
            import sys
            print(f"CV: skipped an entry it could not read (expected 'Authors. Year. Title. ...'): "
                  f"{plain(tex_to_html(tex))[:90]}", file=sys.stderr)
            continue
        authors_tex, year, rest = m.groups()
        title_tex, remainder = _split_title(rest)

        title_links, rest_links = [], []
        title = tex_to_html(title_tex, title_links).rstrip(".").strip()
        title = re.sub(r"\.(</i>)$", r"\1", title)
        if title.startswith("<i>") and title.endswith("</i>") and p["section"] != "Monograph":
            pass
        rest_html = tex_to_html(remainder, rest_links)
        doi = find_doi(rest_links, remainder)
        if doi:
            # drop the printed DOI from the citation text; the site shows a DOI button
            rest_html = re.sub(r"\s*(?:https?://)?(?:dx\.)?doi\.org/\S+?\.?(?=\s|$)", "", rest_html)
            rest_html = re.sub(r"\s*\bdoi:\s*10\.\S+?\.?(?=\s|$)", "", rest_html, flags=re.I).strip()
        rest_html = re.sub(r"\s+([.,])", r"\1", rest_html).strip()
        web = p["web"]
        doi = web.get("doi") or doi
        link = web.get("link") or (title_links[0] if title_links else None) or doi
        out.append({
            "kind": p["section"],
            "authors": tex_to_html(authors_tex),
            "year": year,
            "year_value": _year_value(year),
            "title": title,
            "rest": rest_html,
            "doi": doi,
            "link": link,
            "tags": web.get("tags", []),
            "hide": bool(web.get("hide")),
            "selected": web.get("selected"),     # True, or a number giving its place
            "accepted": web.get("accepted"),     # optional date a "To appear" paper was accepted
        })
    return out


# ---------------------------------------------------------------------------
# Talks
# ---------------------------------------------------------------------------

def _dates_in(text, default_year):
    """All (year, month) found in a venue string."""
    found = []
    for m in re.finditer(r"\b(" + "|".join(MONTHS) + r")\b\.?(?:\s+(\d{4}))?", text, re.I):
        month = MONTHS.index(m.group(1).lower()) + 1
        year = int(m.group(2)) if m.group(2) else default_year
        found.append((year, month))
    return found


def _looks_like_authors(text):
    """[A.R. Deal and J. Roe] is a list of co-authors; [poster] or [2 lectures] is a note."""
    return bool(re.search(r"\bDeal\b", text) or re.search(r"\b[A-Z]\.\s*[A-Z]?\.?\s*[A-Z][a-z]", text))


def parse_talks(src):
    block = _block(src, r"\\marginhead\{[^\n]*Talks\}", r"\\marginhead\{")
    talks = []
    kind = "Invited"
    current = None
    pending = ""       # a bare \ind or \indd $\rhd$ waiting for its text on the next line
    for raw in block.splitlines():
        stripped = raw.strip()
        if stripped.startswith("%"):
            if re.match(r"%\s*web:", stripped) and current is not None:
                current["web"].update(parse_web(stripped))
            continue
        line = strip_comments(raw).strip()
        if not line:
            continue
        if re.fullmatch(r"\\indd?(\s*\$\\rhd\$)?", line):
            pending = line
            continue
        if pending:
            line, pending = pending + " " + line, ""
        hm = re.search(r"\\noindent\\emph\{\s*([^\\}]+?)\s*(?:\\vspace|\})", line)
        if hm:
            kind = "Invited" if "invitation" in hm.group(1).lower() else "Reviewed abstract"
            continue
        if line.startswith("\\indd"):
            if current is not None:
                venue = tex_to_html(line[len("\\indd"):])
                current["venues"].append(venue)
            continue
        if line.startswith("\\ind"):
            m = re.match(r"\\ind\s+((\d{4})(?:\s*[-–]+\s*(\d{2,4}))?)\.\s*(.*)$", line)
            if not m:
                current = None
                continue
            y1 = int(m.group(2))
            y2 = m.group(3)
            y_end = y1 if not y2 else int(y2) if len(y2) == 4 else int(str(y1)[:2] + y2)
            body = m.group(4)
            title_tex, rest = _split_title(body)
            current = {"years": m.group(1), "year": y_end, "kind": kind, "web": {},
                       "title": tex_to_html(title_tex).rstrip("."),
                       "venues": [tex_to_html(rest)] if rest.strip() else []}
            talks.append(current)
            continue
        if current is not None and not line.startswith("\\"):
            # text continuing on the next line: a first venue, or the rest of the last one
            if current["venues"]:
                current["venues"][-1] += " " + tex_to_html(line)
            else:
                current["venues"].append(tex_to_html(line))

    for t in talks:
        dates = []
        for v in t["venues"]:
            d = _dates_in(plain(v), t["year"])
            dates.extend(d if d else [])
        if not dates:
            dates = [(t["year"], 0)]
        t["latest"] = max(dates)
        t["coauthors"] = ""
        t["notes"] = []
        clean = []
        for v in t["venues"]:
            for bm in list(re.finditer(r"\[([^\]]*)\]", v))[::-1]:
                inside = bm.group(1).strip().rstrip(".")
                if re.fullmatch(r"remote|virtual|online", inside, re.I):
                    repl = f" ({inside})"
                elif _looks_like_authors(inside):
                    t["coauthors"] = inside
                    repl = ""
                else:
                    t["notes"].insert(0, inside)       # [poster], [2 lectures], ...
                    repl = ""
                v = v[:bm.start()].rstrip(" .") + repl + v[bm.end():]
            clean.append(re.sub(r"\s+([.,])", r"\1", v).strip().rstrip("."))
        t["venues"] = [v for v in clean if v]
        # newest venue first
        t["venues"].sort(key=lambda v: max(_dates_in(plain(v), t["year"]) or [(0, 0)]), reverse=True)
        names = [n.strip() for n in re.split(r",|&amp;|\band\b", t["coauthors"]) if n.strip()]
        t["with"] = [n for n in names if not re.search(r"\bDeal\b", n)]
        t["tba"] = t["title"].strip().upper() == "TBA"
        t["handout"] = t["web"].get("handout")
        t["hide"] = bool(t["web"].get("hide"))
    return talks


# ---------------------------------------------------------------------------
# Teaching
# ---------------------------------------------------------------------------

SEASONS = {"fall": 0, "autumn": 0, "winter": 1, "spring": 2, "summer": 3}
TERM_RE = re.compile(r"^(Fall|Autumn|Winter|Spring|Summer)\s+(\d{4})(?:\s+with\s+(.+))?$", re.I)


def _final_parens(line):
    """'Title (a; b)' -> ('Title', 'a; b'); balanced, so titles may contain parentheses."""
    line = line.rstrip(" .")
    if not line.endswith(")"):
        return line, None
    depth = 0
    for i in range(len(line) - 1, -1, -1):
        if line[i] == ")":
            depth += 1
        elif line[i] == "(":
            depth -= 1
            if depth == 0:
                return line[:i].strip(), line[i + 1:-1]
    return line, None


def academic_year(season, year):
    """Fall 2025 -> 2025 (2025-26); Spring 2026 -> 2025; Summer 2026 -> 2025."""
    return year if season == 0 else year - 1


def parse_teaching(src):
    """Courses from the CV's Teaching section.

    Course:       \\ind Title (Ling.~121, undergraduate; Fall 2015, Spring 2016 with Jane Roe)
    Short course: \\ind Title. Venue, Month Year (remote).
    Returns one dict per course or short course, each with a list of offerings.
    """
    block = _block(src, r"\\marginhead\{[^\n]*Teaching\s*\}", r"\\marginhead\{|\\newpage")
    courses = []
    place = ""
    pending = False
    for raw in block.splitlines():
        stripped = raw.strip()
        if stripped.startswith("%"):
            if re.match(r"%\s*web:", stripped) and courses:
                courses[-1]["web"].update(parse_web(stripped))
            continue
        line = strip_comments(raw).strip()
        if not line:
            continue
        hm = re.search(r"\\noindent\\emph\{\s*([^\\}]+?)\s*(?:\\vspace|\})", line)
        if hm:
            place = re.sub(r"^At\s+", "", hm.group(1).strip())
            continue
        if line == "\\ind":
            pending = True
            continue
        if line.startswith("\\ind"):
            line = line[len("\\ind"):].strip()
        elif not pending:
            continue
        pending = False
        title_tex, inside = _final_parens(line)
        if inside is not None and ";" in inside:
            meta, terms_tex = inside.rsplit(";", 1)
            parts = [x.strip() for x in meta.split(",", 1)]
            number = parts[0] if len(parts) > 1 or not re.match(r"(?i)under|grad", parts[0]) else ""
            level = parts[-1] if len(parts) > 1 or not number else ""
            offerings = []
            for term in re.split(r",|\band\b", terms_tex):
                term = term.strip()
                if not term:
                    continue
                m = TERM_RE.match(plain(tex_to_html(term)))
                if not m:
                    print(f"Teaching: could not read the term '{term}' in: {line}")
                    continue
                season = SEASONS[m.group(1).lower()]
                year = int(m.group(2))
                offerings.append({"term": f"{m.group(1).capitalize()} {year}",
                                  "ay": academic_year(season, year),
                                  "order": (year, season if season else 4),
                                  "with": m.group(3) or ""})
            courses.append({"kind": "course", "place": place, "web": {},
                            "title": tex_to_html(title_tex), "number": tex_to_html(number),
                            "level": tex_to_html(level), "offerings": offerings})
        else:
            title_tex, rest = _split_title(line)
            text = plain(tex_to_html(rest)).rstrip(".")
            dm = re.search(r"\b(" + "|".join(MONTHS) + r")\b[^,]*?(\d{4})", text, re.I)
            if not dm:
                print(f"Teaching: no month and year found in: {line}")
                continue
            month, year = MONTHS.index(dm.group(1).lower()) + 1, int(dm.group(2))
            courses.append({"kind": "short", "place": "", "web": {},
                            "title": tex_to_html(title_tex).rstrip("."),
                            "number": "", "level": "", "detail": html.escape(text),
                            "offerings": [{"term": "", "with": "",
                                           "ay": year if month >= 8 else year - 1,
                                           "order": (year, 1 if month < 6 else 3)}]})
    return [c for c in courses if not c["web"].get("hide")]


def load(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    return parse_publications(src), parse_talks(src)

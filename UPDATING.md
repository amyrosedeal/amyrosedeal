# Updating the website

The website follows your CV. Papers, talks, courses, the CV PDF and the home
page's "What's new" list all come from one file: `cv/cv-full.tex`.

## The routine

1. Edit `cv-full.tex` on your computer as you always do.
2. On github.com, open this repository's `cv` folder, choose
   **Add file → Upload files**, drag in `cv-full.tex`, and click **Commit changes**.
3. Within about three minutes GitHub rebuilds the CV PDF, the Research page,
   the Talks page, the Teaching page and "What's new". You don't upload the PDF yourself.

To watch progress, open the **Actions** tab. A green check means the site is
updated; a red X means something went wrong (the CV didn't compile, say).

---

## Adding a paper

### How it works, in short

Each paper is an `\item` in the right section of your CV, written as you
always have. Directly under it you can add **one comment line** starting with
`% web:`. That line is read by the website and never printed in the PDF. It holds
anything the website needs that isn't in the citation itself:

| In the `% web:` line | What it does |
|---|---|
| `tags=syntax, case-agr` | topics for the Research page's "Filter by topic" menu |
| `link=https://...` | where the title links (lingbuzz, a PDF, a publisher page) |
| `doi=https://doi.org/...` | a DOI you don't want printed in the CV |
| `selected=1` | puts the paper in the "Selected work" box at the top |
| `hide` | leaves the paper off the website (it stays in the PDF) |
| `accepted=2026-10` | when a "To appear" paper was accepted (only if you want to set it yourself; see below) |

Separate several with semicolons, all on one line:
`% web: link=https://...; tags=syntax, semantics; selected=2`

A paper with no `% web:` line still appears on the website. It just has no
topics (it shows only under "All topics") and no extra link.

### Where each CV section appears

| CV section | Where it appears on the website |
|---|---|
| Monograph | its year, labelled "Book" |
| Journal articles | its year, labelled "Journal article" |
| Other publications | its year, labelled "Chapter / proceedings" |
| Manuscripts | "In the pipeline", showing only title, authors and link |
| any section, with the year written `To appear` | "In the pipeline", and announced in "What's new" (see below) |

### The one rule for the citation

Each entry must start **Authors. Year. Title.** with a period after each part.

- The year can be `2027`, `To appear`, `In press` or `Forthcoming`.
- The title ends at its first period or question mark. If a title has a period
  or question mark *inside* it, put the whole title in braces with its final
  period inside: `{Why? A question.}`
- If an entry doesn't follow this pattern, it is left off the website, and the
  Actions log says which entry was skipped.

Within a year, papers appear in the order they appear in the CV, so put the
newest first in each section, as you already do.

### Topic tags

| Tag | Shown in the filter as |
|---|---|
| `syntax` | Syntax |
| `semantics` | Semantics |
| `morphology` | Morphology |
| `typ` | Typology |
| `nzp` | Nez Perce |
| `case-agr` | Case & agreement |
| `extposs` | Possession |
| `locality` | Locality |
| `mass` | Number & countability |
| `perspective` | Attitudes & perspective |
| `modality` | Modality |

Tags are used only by the filter; they aren't shown on the paper itself.

---

### Example 1: a journal article with a DOI and several topics

Under **Journal articles**:

```latex
\item Deal, Amy Rose, and Jane Roe. 2027. Title of the article. \emph{Linguistic Inquiry} 58(2): 101--140. \href{https://doi.org/10.1162/ling_a_00600}{https://doi.org/10.1162/ling\_a\_00600}.
% web: tags=syntax, typ, case-agr
```

On the website: under 2027, labelled "Journal article"; the title and a
**DOI** button both go to the DOI. You don't need `doi=` in the comment line,
because the DOI is already in the citation (any of the forms in "DOIs" below works).

If you'd also like a lingbuzz button, with the title linking to lingbuzz:

```latex
% web: link=https://lingbuzz.net/lingbuzz/012345; tags=syntax, typ, case-agr
```

### Example 2: a manuscript with a link and topics

Under **Manuscripts**:

```latex
\item Deal, Amy Rose, and Jane Roe. 2026. Title of the manuscript. Submitted for review.
% web: link=https://lingbuzz.net/lingbuzz/012345; tags=semantics, typ
```

On the website: under "In the pipeline", showing the title (linking to
lingbuzz), the authors and a **lingbuzz** button. Without `link=`, it would
appear with no link at all.

### Example 3: a published chapter or proceedings paper, with topics

Under **Other publications**:

```latex
\item Deal, Amy Rose. 2027. Title of the chapter. In Jane Roe and John Doe (eds.), \emph{Proceedings of NELS 57}, pp. 1--14. Amherst: GLSA. https://doi.org/10.5281/zenodo.1234567
% web: link=https://lingbuzz.net/lingbuzz/012345; tags=semantics, perspective
```

On the website: under 2027, labelled "Chapter / proceedings", with
**lingbuzz** and **DOI** buttons. If there's no DOI, leave it out; if there's no
lingbuzz version, leave out `link=` (with neither, the title isn't linked).

### Example 4: putting a paper in "Selected work" (`selected=`)

```latex
\item Deal, Amy Rose. 2027. Title of the article. \emph{Linguistic Inquiry} 58(2): 101--140. https://doi.org/10.1162/ling\_a\_00600
% web: tags=syntax, typ, case-agr; selected=1
```

The number is its place in the box: `selected=1` comes first. The box
currently holds three papers (`selected=1`, `2` and `3`: the book, *Interaction,
satisfaction, and the PCC* and *Current models of Agree*). So to make a new
paper number 1, also renumber the others in the CV (the book to `selected=2`,
and so on), or delete `selected=...` from the one you want to drop. If two
papers share a number, the one higher in the CV comes first. A paper in
"Selected work" also still appears in its year further down.

### Example 5: keeping a paper off the website (`hide`)

```latex
\item Deal, Amy Rose. 2009. Title of an old squib. \emph{Snippets} 19: 5--6.
% web: hide
```

The paper stays in the CV PDF but doesn't appear anywhere on the website.
`hide` can sit alongside other settings (`% web: tags=syntax; hide`), which is
handy for hiding a paper temporarily: delete `; hide` later and it reappears
with its topics.

---

### DOIs

Write the DOI in the CV however you like; the website finds it in any of these forms:

```latex
\href{https://doi.org/10.1162/ling_a_00529}{https://doi.org/10.1162/ling\_a\_00529}
\url{https://doi.org/10.1162/ling_a_00529}
https://doi.org/10.1162/ling\_a\_00529
doi:10.1162/ling\_a\_00529
```

The website gives the paper a **DOI** button and links its title to the DOI
(unless the comment line has a `link=`, in which case the title goes there
and you get both buttons).

- **A DOI you don't want printed in the CV:** `% web: doi=https://doi.org/10.xxxx/yyyy`
- **Linking the title inside the CV itself** (`\href{url}{Title}`) also works.
- Other links in an entry (to a proceedings volume, say) are ignored.
- The button for `link=` is labelled **lingbuzz**, **PDF** or **Article**,
  depending on the address.

### When a paper is accepted ("To appear")

Change its year to `To appear` (and move it to Journal articles or Other
publications, filling in the venue), then upload the CV as usual:

```latex
\item Deal, Amy Rose, and Jane Roe. To appear. Title of the article. \emph{Linguistic Inquiry}.
% web: link=https://lingbuzz.net/lingbuzz/012345; tags=syntax, case-agr
```

On the website it moves to "In the pipeline" on the Research page, and it is
announced at the top of "What's new" as **Accepted · Oct 2026**, "To appear in
*Linguistic Inquiry*".

The acceptance date is the day you upload the CV with `To appear` in it: the
website notes that date in `accepted-dates.txt` the first time it sees the
paper marked "To appear". You never need to touch that file. If you want a
different date (say you're catching up on an acceptance from March), add it to
the comment line: `% web: accepted=2026-03`.

### When a manuscript or "To appear" paper is published

Move its `\item` to Journal articles (or Other publications) if it isn't
there already, fill in the year, venue and DOI as usual, and keep its `% web:` line under it.
The website moves it out of "In the pipeline" into its year. If its `link=`
points to the lingbuzz version and you'd rather the title go to the published
version, delete `link=...` from the comment line.

---

## Adding a talk

Talks come from the CV's "By invitation" and "By reviewed abstract" sections:

```latex
\ind 2027. Title of the talk. Colloquium, University of Somewhere, March 2027.
```

A talk given in several places:

```latex
\ind 2026-27. Title of the talk.

\indd $\rhd$ Colloquium, University of Somewhere, March 2027.

\indd $\rhd$ Workshop on Something, Paris, October 2026.
```

- Co-authors go in square brackets: `[A.R. Deal and J. Roe]`. `[remote]` is shown as "(remote)".
- Talks dated in the future appear under "Upcoming"; the rest are grouped by year.
  A talk given in several years appears under each of those years.
- `TBA` as the title shows just the date and venue, with no title, until you
  replace it with the real title.
- `% web: handout=https://...` under a talk adds a handout link.
- The Talks page lists talks from 2016 onward.

---

## The home page's "What's new"

"What's new" is a single list, newest first. It always contains:

- the **3 newest papers** from your CV. Papers marked "To appear" count from
  the date they were accepted (see "When a paper is accepted" above); published
  papers count from the middle of their year, since the CV gives only the year,
- the **2 most recent talks** you have already given (from your CV),
- your **latest blog post**,
- any items you add to `whats-new.txt` (from the last year or so).

You never edit the home page itself.

### Getting a new talk into "What's new", step by step

1. **Add the talk to your CV** under "By invitation" or "By reviewed abstract",
   with its month, the way you always do:

   ```latex
   \ind 2026. Title of the talk. Colloquium, University of Somewhere, November.
   ```

   If it's a talk you've given before, add the new venue under the existing
   title instead (a `\indd $\rhd$ ...` line). The website treats that the same way.

2. **Upload the CV** to the repository's `cv` folder on github.com
   (**Add file → Upload files**, then **Commit changes**). See "The routine" above.

3. **Wait for the talk's month.** A talk appears in "What's new" from the first
   day of the month it's dated (November 2026 → from November 1). Until then it
   is listed under "Upcoming" on the Talks page only. You don't need to do
   anything when the month arrives: GitHub rebuilds the site every morning
   (about 7am Pacific), so the talk shows up on its own that day.

4. **Check.** On the home page the talk appears as **Talk · Nov 2026**, with its
   title and venue (and co-authors, if any). It links to the Talks page, or to
   the handout if the CV has a `% web: handout=` line for it.

Things that keep a talk out of "What's new":

- **Its title is still `TBA`.** Replace `TBA` with the real title in the CV.
- **Two more recent talks** are already showing. Only the 2 latest appear; when
  several talks share a month, the one higher in the CV wins.
- **No month in the venue** (e.g. just "2026"). Add the month.
- **A `% web: hide` line** under it.

### Announcing a talk before it happens

Upcoming talks don't appear in "What's new" by themselves. To announce one
early (a keynote, say), add a line to `whats-new.txt`: on github.com, click the
file, then the pencil icon, add the line, and click **Commit changes**.

```
2026-11 | Talk | Title of the talk | Keynote, Conference Name, Paris | https://amyrosedeal.github.io/amyrosedeal/talks.html
```

The five parts are date | label | title | detail | link. Once the talk has
happened it also appears automatically from the CV, so delete this line then to
avoid listing it twice.

### Other news

For anything else (a new journal, an award, a new role), add a line to
`whats-new.txt` the same way. Items drop off by themselves after about a year.

## Adding a course

The Teaching page comes from the CV's Teaching section. Each course is listed
**once**, with every term you've taught it, and an optional description line
underneath that appears only on the website:

```latex
\ind Formal Semantics (Ling.~121, undergraduate; Fall 2022, Fall 2024, Spring 2027)
% web: about=Introduction to formal semantics for undergraduates.
```

The `% web:` line is a LaTeX comment: it never prints in the PDF.

### Step by step: a course you've taught before

1. Open `cv-full.tex` and find the course's `\ind` line in the Teaching section.
2. Add the new term at the end of the list of terms, after a comma:

   ```latex
   \ind Formal Semantics (Ling.~121, undergraduate; Fall 2022, Fall 2024, Spring 2027, Fall 2027)
   ```

3. Leave the `% web: about=` line as it is. The website reuses that
   description for the new term automatically.
4. Upload the CV (see "The routine" at the top). Within a few minutes the
   course appears under its academic year on the Teaching page.

### Step by step: a brand-new course

1. Open `cv-full.tex` and find the right institution heading in the Teaching
   section (for a Berkeley course, the "At UC Berkeley" list).
2. Add a new line for the course, in this exact shape:

   ```latex
   \ind Title of the Course (Ling.~123, graduate; Spring 2028)
   ```

   - Inside the brackets: course number, then a comma, then the level
     (`undergraduate`, `graduate`, `graduate seminar`, ...), then a
     **semicolon**, then the term.
   - A term is Fall, Winter, Spring or Summer plus the year. Separate several
     terms with commas.
   - Co-taught? Put the co-teacher after that term:
     `Spring 2028 with Jane Roe`.
3. Directly under it, add the description for the website (optional, but
   without it the course shows only title, number, level and term):

   ```latex
   % web: about=One or two sentences describing the course.
   ```

   Keep the description on one line. Semicolons, commas and question marks
   are all fine inside it.
4. Upload the CV.

### Step by step: a one-off description for a single term

Use this when one offering is different from the usual course: a special
theme, a second stream, a different focus. The usual `about=` description
stays for every other term; the one-off text replaces it for that term only.

1. Find the course in `cv-full.tex`. Make sure the special term is in its list
   of terms (add it if this is a new offering, as above).
2. Under the course's `% web: about=` line, add a line that starts with that
   term (the same words as in the list of terms) instead of `about`:

   ```latex
   \ind Advanced Syntax II (Ling.~220b, graduate; Spring 2019, Spring 2025, Spring 2027)
   % web: about=The second course in the graduate introduction to syntax series.
   % web: Spring 2025=The second course in the graduate introduction to syntax series. (Theme: long-distance dependencies)
   ```

   Here Spring 2025 shows the theme; Spring 2019 and Spring 2027 show the usual
   description.
3. Write the one-off line as the **full** description you want shown that
   term, not just the extra bit: it replaces `about=` rather than adding to it.
   (That's why the example repeats "The second course in ...".)
4. Add one such line for each special term. Their order doesn't matter.
5. Upload the CV.

### Summer schools and short courses

These go under "Summer schools and short courses" at the end of the Teaching
section, in a different shape: title, period, venue, month and year.

```latex
\ind Title of the Course. LSA Summer Institute, University of Somewhere, July 2027.
```

Add `(remote)` after the year if it was online. They appear on the website
under their academic year, labelled "Short course". A description line
(`% web: about=...`) works for these too.

### Good to know

- The website groups courses by academic year (Fall 2026 and Spring 2027 both
  go under 2026–2027), newest first, and shows the last ten academic years
  (the setting `TEACHING_YEARS` in `scripts/build_site.py`). Older courses
  stay in the CV PDF.
- Courses at UC Berkeley show course number and level; courses elsewhere also
  name the institution, taken from the "At ..." heading above them.
- `% web: hide` under a course leaves it off the website (it stays in the PDF).
- If the website can't read a line (a missing semicolon, say), it is left off
  and the Actions log names the line.

---

## Papers that aren't in the CV

`cv/website-only.tex` holds papers shown on the Research page but not in the
CV (currently two older manuscripts). Same format as the CV; never compiled.

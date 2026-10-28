# Updating the website

The website follows your CV. Papers, talks, the CV PDF and the home page's
"What's new" list all come from one file: `cv/cv-full.tex`.

## The routine

1. Edit `cv-full.tex` on your computer as you always do.
2. On github.com, open this repository's `cv` folder, choose
   **Add file → Upload files**, drag in `cv-full.tex`, and click **Commit changes**.
3. Within about three minutes GitHub rebuilds the CV PDF, the Research page,
   the Talks page and "What's new". You don't upload the PDF yourself.

To watch progress, open the **Actions** tab. A green check means the site is
updated; a red X means something went wrong (the CV didn't compile, say).

---

## Adding a paper

Add it to the right section of your CV, the way you always have:

| CV section | Where it appears on the website |
|---|---|
| Monograph | its year, labelled "Book" |
| Journal articles | its year, labelled "Journal article" |
| Other publications | its year, labelled "Chapter / proceedings" |
| Manuscripts | "In the pipeline", showing only title, authors and link |
| any section, with the year written `To appear` | "In the pipeline" |

The one thing the website relies on is that each entry starts
**Authors. Year. Title.** with a period after each part:

```latex
\item Deal, Amy Rose and Jane Roe. 2027. Title of the paper. \emph{Journal} 12(3): 45--67. ...
```

- The year can be `2027`, `To appear`, `In press` or `Forthcoming`.
- The title ends at its first period or question mark. If a title has a period
  or question mark *inside* it, put the whole title in braces with its final
  period inside: `{Why? A question.}`
- If an entry doesn't follow this pattern, it is left off the website, and the
  Actions log says which entry was skipped.

Within a year, papers appear in the order they appear in the CV, so put the
newest first in each section, as you already do.

### DOIs

Write the DOI in the CV however you like; the website finds it in any of these forms:

```latex
\href{https://doi.org/10.1162/ling_a_00529}{https://doi.org/10.1162/ling\_a\_00529}
\url{https://doi.org/10.1162/ling_a_00529}
https://doi.org/10.1162/ling\_a\_00529
doi:10.1162/ling\_a\_00529
```

The website gives the paper a **DOI** button and links its title to the DOI.
It works the same for journal articles, chapters, proceedings and books.

### A link that isn't a DOI (lingbuzz, a PDF, a publisher page)

Add a comment line directly under the entry:

```latex
\item Deal, Amy Rose. 2027. Title. \emph{Journal} 12: 1--20.
% web: link=https://lingbuzz.net/lingbuzz/012345
```

Comment lines never appear in the PDF. The title then links there, with a
button labelled **lingbuzz**, **PDF** or **Article** depending on the address.

- **Link and DOI together:** if the entry also has a DOI, you get both buttons;
  the title goes to your `link=`. To make the title go to the DOI instead,
  just leave out `link=`.
- **A DOI you don't want printed in the CV:** `% web: doi=https://doi.org/10.xxxx/yyyy`
- **Linking the title inside the CV itself** (`\href{url}{Title}`) also works.
- Other links in an entry (to a proceedings volume, say) are ignored.

### Everything else the comment line can do

Combine as many as you like, separated by semicolons:

```latex
% web: link=https://lingbuzz.net/lingbuzz/012345; tags=syntax, case-agr; selected=2
```

- `tags=` topics for the Research page filter:
  `syntax`, `semantics`, `morphology`, `typ` (Typology), `nzp` (Nez Perce),
  `case-agr` (Case & agreement), `extposs` (Possession), `locality`,
  `mass` (Number & countability), `perspective` (Attitudes & perspective),
  `modality`. A paper with no tags shows only under "All topics".
- `selected=1`, `selected=2`, … puts a paper in "Selected work", in that order.
- `hide` keeps an entry off the website (it stays in the PDF).

### When a manuscript is published

Move its `\item` from Manuscripts to Journal articles (or Other publications),
fill in the year, venue and DOI as usual, and keep its `% web:` line under it.
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

- the **3 newest papers** from your CV,
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

## Papers that aren't in the CV

`cv/website-only.tex` holds papers shown on the Research page but not in the
CV (currently two older manuscripts). Same format as the CV; never compiled.

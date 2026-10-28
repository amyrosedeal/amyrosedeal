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
- `TBA` as the title shows as "Title to be announced".
- `% web: handout=https://...` under a talk adds a handout link.
- The Talks page lists talks from 2016 onward.

---

## The home page's "What's new"

Updates itself: the 3 newest papers, the 2 most recent talks, and your latest
blog post. For other news (a new journal, an award), add a line to
`whats-new.txt` on github.com (click the file, then the pencil icon); the
format is explained at the top of that file.

## Papers that aren't in the CV

`cv/website-only.tex` holds papers shown on the Research page but not in the
CV (currently two older manuscripts). Same format as the CV; never compiled.

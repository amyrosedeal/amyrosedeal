# Updating the website

The website follows your CV. Papers, talks, the CV PDF and the home page's
"What's new" list all come from one file: `cv/cv-full.tex`.

## The usual routine

1. Edit `cv-full.tex` on your computer as you always do.
2. On github.com, open this repository's `cv` folder, choose
   **Add file → Upload files**, drag in `cv-full.tex`, and click **Commit changes**.
3. Within a few minutes GitHub rebuilds `ARDeal.pdf`, the Research page,
   the Talks page and "What's new". You don't need to upload the PDF.

You can watch progress, or rerun the update, under the **Actions** tab.

## Website details in the CV (optional)

A comment line right after an entry adds details that only the website uses.
Comments never appear in the PDF.

```latex
\item Clem, Emily and Amy Rose Deal. 2026. {Dependent case by Agree: ...} ...
% web: link=https://ling.auf.net/lingbuzz/007429; tags=typ, syntax, case-agr
```

- `link=` where the title should point (e.g. lingbuzz or a PDF). Without it,
  the website uses the entry's DOI.
- `tags=` topic filters on the Research page:
  `syntax`, `semantics`, `morphology`, `typ` (Typology), `nzp` (Nez Perce),
  `case-agr` (Case & Agreement), `extposs` (Possession), `locality`,
  `mass` (Number & countability), `perspective` (Attitudes & Perspective),
  `modality`.
- `doi=` a DOI link, if the CV entry doesn't print one.
- For talks: `% web: handout=https://...` adds a handout link.
- `% web: hide` keeps an entry off the website.
- `% web: selected` puts a paper in "Selected work" at the top of the Research
  page. Use `selected=1`, `selected=2`, … to set their order.

Which CV sections are used:
- **Research page:** Monograph, Journal articles, Manuscripts, Other publications.
- **Talks page:** By invitation, By reviewed abstract. Talks dated in the future
  appear under "Upcoming".

## Papers that aren't in the CV

`cv/website-only.tex` lists papers that appear on the Research page but not in
the CV (currently two older manuscripts). It uses the same format as the CV and
is never compiled. Edit it on github.com like any other file.

The Talks page lists talks from 2016 onward (set by `TALKS_FROM` at the top of
`scripts/build_site.py`).

## Other news

For news that isn't a paper, talk or blog post (a new journal, an award),
add a line to `whats-new.txt` on github.com (click the file, then the pencil
icon). The format is explained at the top of that file.

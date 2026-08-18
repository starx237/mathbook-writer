# LaTeX and page-layout contract

## Contents

1. Engine and structure
2. Problem units
3. Boxes and lists
4. Pagination
5. Figures
6. Printable mock papers

## 1. Engine and structure

Use XeLaTeX for Chinese mathematics. Keep reusable style definitions in one package and course
content in chapter files. Use ASCII labels and stable problem IDs. Compile references at least
twice, usually three times for release.

Start from `assets/latex-template/` when building a new project. Rename the generic package and
headings only if necessary; retain the semantic environments so bundled audits work.

## 2. Problem units

Keep this source order:

```latex
\problemstart
\subsection{... \problemid{COURSE-XXXX-X-Q03}}
\paragraph{题目} ...
\begin{examanswer}
...
\end{examanswer}
\begin{idea}
... \knowledgelink{sec:anchor}{知识点名称} ...
\end{idea}
```

Do not interleave another problem. Avoid floating figures inside a problem unit; use anchored
figures or `\includegraphics` with an explicit caption/source note.

## 3. Boxes and lists

Make formal answers visually distinct from motivations. Give paragraphs discernible spacing and a
modest line stretch. Use a breakable box for genuinely long content.

Use a list with an explicit label width for formal steps:

```latex
\begin{examsteps}
  \item ...
  \item ...
\end{examsteps}
```

Do not use a narrow default `enumerate` label inside a framed box for “步骤 10.”. Inspect the
rendered left edge at original resolution.

## 4. Pagination

Reserve a fraction of a page before a short problem with `\Needspace`. Tune the reserve per unit;
do not use one value as proof that the unit will fit.

Priority order:

1. keep statement and formal solution together;
2. keep the full three-part unit together when reasonable;
3. allow a long proof or motivation to cross at a natural paragraph or step boundary;
4. never delete reasoning, proof steps, hypotheses, or figures to avoid a page break.

A compact 9.5–10 pt body and small box text are acceptable if formulas and Chinese remain legible.
Aim for two or three complete short units per page only when content length permits.

## 5. Figures

Include a figure whenever topology, geometry, graph incidence, gluing, orientation, labels, or a
photograph determines the statement. Prefer:

- a traceable crop when fidelity matters;
- TikZ or vector redraw when labels and structure can be reproduced exactly.

Record source file and page. If the archive itself lacks the figure, show a visible missing-source
notice rather than inventing one.

## 6. Printable mock papers

Place answer-free mock papers in a separate section or build target. Permit only:

- title, duration, score, instructions;
- problem numbers, statements, scores;
- necessary figures and assumptions.

Forbid formal answers, motivations, hints, method names, knowledge links, colored correction notes,
and PDF link annotations. The template's `\DeclareMockProblem`, `\PrintMockProblem`, and
`\SolveMockProblem` commands reuse one statement while rendering separate print and solution
forms.

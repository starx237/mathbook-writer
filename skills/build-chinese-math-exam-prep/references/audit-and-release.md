# Audit and release protocol

## Contents

1. Audit layers
2. Static LaTeX audit
3. Mathematical and pedagogical review
4. PDF and visual review
5. Clean build and release package

## 1. Audit layers

Run audits in this order:

1. source completeness and classification;
2. static problem structure;
3. human mathematics and pedagogy;
4. LaTeX compilation and logs;
5. PDF pagination and print leakage;
6. full-page visual inspection;
7. clean rebuild and release integrity.

Passing a later layer does not excuse an earlier failure.

## 2. Static LaTeX audit

Run:

```text
python scripts/audit_latex_exam.py chapter1.tex chapter2.tex --require-links
```

Use its errors to find missing or reversed `examanswer`/`idea` blocks, duplicate IDs, empty
sections, and answer leakage in `mockpaper`. Treat its length and repeated-label reports as review
candidates only.

After compilation run:

```text
python scripts/audit_pdf_problem_paging.py book.pdf chapter1.tex chapter2.tex --min-body-page 10
```

Review every split flag. A natural long proof is not automatically defective; an avoidable
statement/answer split is.

## 3. Mathematical and pedagogical review

Use a per-problem checklist with named reviewer status. Verify definitions, hypotheses, symbols,
proof closure, computations, edge cases, source fidelity, and official-answer correctness.

Then review formal solution and motivation separately:

- Can the formal section be submitted without editorial prose?
- Can a prepared reader reconstruct the method without memorizing the formal text?
- Are paragraphs, cases, and steps natural rather than mechanically uniform?
- Does every used prerequisite exist in the foundations?

Review cheatsheet claims against the body and every problem dependency in the reverse direction.

## 4. PDF and visual review

Create a JSON manifest based on `assets/latex-template/release-manifest.json`, then run:

```text
python scripts/audit_pdf_release.py release-manifest.json
```

Render every page to PNG. Inspect a contact sheet for global anomalies, then original-resolution
pages for:

- first/last page of every section;
- every cross-page problem unit;
- dense aligned formulas and long labels;
- figures, captions, and crops;
- colored or breakable box transitions;
- all answer-free mock pages.

Check that printable ranges contain no answer labels, motivations, hints, or link annotations.

## 5. Clean build and release package

Run a source-only build:

```text
python scripts/clean_build.py PROJECT_ROOT main.tex --passes 3
```

Exclude `.aux`, `.log`, `.out`, `.toc`, rendered pages, caches, and previous PDFs from the source
archive. Extract the archive to a new empty directory and rebuild there. Verify:

- PDF opens, is A4, has expected pages, text, links, bookmarks, and images;
- no undefined references, missing glyphs, fatal errors, or unintended overflow remain;
- every inventory and source file required for reproducibility is included;
- archive paths are relative and safe;
- SHA-256 values are recorded for every delivered PDF and archive.

Release a concise manifest naming version/date, source snapshot, known source gaps, page counts,
hashes, build command, and audit status.


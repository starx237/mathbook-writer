# Source reconstruction and provenance

## Contents

1. Inventory schema
2. Classification and transcription
3. Problem-level provenance
4. Missing and defective sources

## 1. Inventory schema

Create one row per distinct source file with at least:

| Field | Meaning |
|---|---|
| `source_id` | Stable ASCII identifier |
| `path_or_url` | Original location |
| `sha256` | Deduplication and release trace |
| `course_claimed` | Directory or page classification |
| `course_verified` | Classification after content review |
| `teacher`, `year`, `exam_type` | Use `unknown` rather than guessing |
| `pages`, `text_method` | Native text, OCR, handwritten/manual |
| `answer_source` | Official, instructor notes, recollection, authored |
| `completeness` | Complete, truncated, missing pages, partial recollection |
| `notes` | Ambiguity, diagrams, defects, related editions |

Search the repository tree as well as the rendered index. Unlinked files and naming collisions are
common. Hash identical files before counting exams.

## 2. Classification and transcription

Classify with converging evidence: printed title, instructor, syllabus topics, notation, neighboring
files, and answer keys. If evidence conflicts, record the conflict.

Use this transcription loop:

1. Extract native text.
2. Render pages at sufficient resolution.
3. OCR only pages without usable text.
4. Use OCR to locate likely wording.
5. Compare each mathematical token with the page image.
6. Transcribe diagrams or crop the original.
7. Run a second pass focused on negations, quantifiers, exponents, closure bars, subscripts,
   orientation arrows, ranges, and point values.

Never silently normalize a possibly meaningful typo. Preserve the source statement, then add a
clearly separated correction.

## 3. Problem-level provenance

Assign each recoverable problem a stable ID such as `COURSE-XXXX-X-Q03`. Maintain a matrix with:

- source file and page;
- verbatim/reconstructed/partial status;
- subproblem count and figures;
- official-answer page or lack of answer;
- verified course and topic;
- final LaTeX file and anchor;
- mathematical review and visual review status.

Count problems from this matrix, not from headings in a draft. Reconcile the matrix against the
source inventory in both directions: every relevant source problem is represented, and every
historical problem in the book has a source.

## 4. Missing and defective sources

Use explicit labels:

- **Archive missing**: a referenced file or page is unavailable.
- **Source truncated**: the file ends before all questions.
- **Partial recollection**: visible wording is incomplete.
- **Ambiguous figure/wording**: multiple interpretations remain.
- **Source statement false**: give a counterexample and, if useful, a corrected version.

Do not fabricate a question from an answer key. You may describe the recoverable topic and scoring
structure, but distinguish that description from a verbatim historical problem.

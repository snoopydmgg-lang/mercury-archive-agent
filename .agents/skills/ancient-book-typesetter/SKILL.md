---
name: ancient-book-typesetter
description: Create reviewable, source-faithful modern-punctuation manuscripts from scanned Chinese rare books. Use for multimodal direct reading, reference-assisted punctuation alignment, and DOCX review packages; never use OCR text as production copy.
---

# Ancient Book Typesetter

Produce a manuscript whose body text remains traceable to supplied page images.
This Skill is for review and delivery workflows where a character-level error is
more harmful than an unfinished passage.

## Source hierarchy

1. The supplied scan is the authority for every body character and heading.
2. A multimodal direct read fixes the reading order: vertical columns right to
   left, and characters within a column top to bottom.
3. A public edition may be used only after that direct-read layer exists. It
   may supply candidate punctuation positions, title checks, and a discrepancy
   signal. It must not supply replacement body text.
4. OCR engines and their exported text are not production sources. Do not use
   them to seed, repair, or fill a manuscript.

Never silently replace a source glyph from a reference edition. If a scan glyph
cannot be confirmed, use red, bold `[不清]` in the DOCX and record the source
page and reason.

## Required records

Keep the original direct-read record immutable. Write review work into a
separate audit record containing: source PDF page, reference URL, retrieval
date, source-character count, aligned-character count, punctuation candidates,
transferred punctuation, confidence, and every unresolved decision.

Read [reference punctuation alignment](references/punctuation-reference-alignment.md)
before using a public point-collected edition. Use the project helper
`06_Python Scripts/06_工具/build_reference_aligned_review.py` when its input
matches the supported `潛學稿` record layout.

## Workflow gates

### Direct read

- Inspect the scan with a vision-capable model and save a fixed `source_text`
  layer for each textual page.
- Preserve headings separately from body blocks. Verify book title, volume,
  and running-title text against the scan before output.
- When a direct-read record repeats a verified heading inside `source_text`,
  remove that duplicate only in the derived review layer after re-reading the
  scan. Record the page, original string, normalized heading, and reason; do
  not overwrite the immutable direct-read record.
- Set `ocr_used: false`; do not claim page completion for a missing direct read.

### Heading and title adjudication

- Record high-risk headings in a separate adjudication object with
  `source_title`, `reference_title`, `reviewer_claim`, `evidence`,
  `second_model_reading`, `decision` (`accepted|rejected|pending`), and
  `output_rule` (`source|derived_review_only|unresolved`).
- A reviewer request or a public title alone never changes the immutable
  source layer. Accept a character change only when the scan or documented
  textual evidence supports it; otherwise keep the source title and expose
  the disagreement in the audit record.

### Reference-aligned punctuation

- Fetch public reference text only from an explicitly recorded source URL.
- Align reference and direct-read strings character by character.
- Transfer a punctuation mark only where adjacent source characters have a
  contiguous high-confidence alignment. Never transfer reference characters.
- Validate that removing editorial punctuation from the output yields exactly
  the direct-read source character sequence (apart from the standardized
  `[不清]` marker).
- Flag low-coverage alignment or reference/source divergence for scan reread;
  it is not an automatically punctuated passage.

### Review delivery

- A review manuscript may contain unresolved passages, but its title must say
  `审阅版`; do not label it a final point-collected edition.
- Present prose as continuous semantic paragraphs, not as page-by-page body
  fragments. Keep source-page information in the audit record and concise end
  notes only.
- A left-text/right-image DOCX is a review aid, not the final reading layout.
- Render the DOCX when a renderer is available; otherwise run OOXML and
  character-sequence checks and disclose the unavailable render step.

### Final delivery

Only label a file `终校本` when all textual pages have a direct read, a
validated punctuation layer, a resolved-or-marked discrepancy record, no page
in `human_review_required` or `retry_exhausted` state, and a successful
source-character sequence check. Do not re-export an old review file under a
new name as a final deliverable.

## Review feedback

Treat feedback such as a wrong title, a missing punctuation run, or a black
uncertainty marker as a test case: add the observed cause to the audit record,
fix the narrow rule, rebuild a new file, and preserve the previous review file.

## Model and transport routing

Use an OpenAI-compatible channel selected by the operator. BibiLab (哔哔拉布)
is a supported example, but the Skill must not assume a provider, endpoint,
account, or credential. Read [provider setup](references/provider-setup.md)
before the first model call in a new environment.

On first run, stop at the configuration gate and ask the operator to supply,
through the local secret mechanism rather than chat or a committed file:

1. a primary `chat/completions` URL, model name, and API key;
2. a secondary `chat/completions` URL, model name, and API key (the URL and key
   may be shared with the primary channel when the models are distinct).

Run a non-destructive connectivity test for both profiles before reading pages.
If either profile is absent or fails, record `configuration_missing` or
`transport_failed` and do not present the output as cross-validated. Never print
keys, authorization headers, cookies, or full provider responses to stdout,
records, reports, or DOCX.

For the project's BibiLab profile, the recommended model roles are:

- `GPT-5.6-SOL` is the primary vision model for page reading and source-text
  freezing.
- `Gemini 3.1 Pro` is the independent cross-read for titles, names, shaped
  characters, and other high-risk or disputed readings.

Model names and URLs must remain configurable; these names are defaults for a
BibiLab deployment, not embedded credentials or mandatory provider values.

The two calls must be independent: both models receive the scan, and neither
receives the other's text until comparison. Compare their source character
sequences, headings, and uncertainty locations after both responses are saved.
For disagreements, return to the scan and record the adjudication; never choose
the majority string or silently copy a reference edition. A page is
`cross_validated` only when the comparison is saved and every disagreement is
resolved or marked `[不清]`.

Keep the key in an environment variable or local secret store. Never write a
key, cookie, authorization header, or full response containing a key to a
record, report, stdout, or DOCX. A transport failure may be retried with
bounded backoff, with at most 3 attempts per page and a 30-second per-attempt
timeout unless the provider documents a lower limit. Do not silently change
the provider or claim a page was read when no model response was saved. Record
provider, model, attempt count, timeout/error class, and status without
recording credentials. Use `transport_failed` for a transient failed attempt
and `retry_exhausted` for a page whose retry budget is spent; these are not
synonyms for `unreadable`. Persist each page record and ledger entry atomically
(write a temporary file, flush, then replace), and make reruns idempotent by
resuming from the first non-complete page.

## Quality gates learned from failure cases

These are hard gates, not optional polish:

| Observed failure | Required countermeasure |
| --- | --- |
| OCR output diverges from the scan | Do not use OCR as production text; return to the page image and a vision model. |
| Book title or heading is misread | Re-read title/volume/article headings separately and run the second-model cross-read before export. |
| A long passage has no punctuation, or each column receives a comma | Build punctuation from syntax, discourse and genre; use public editions only for candidate boundaries; review unusually long unpunctuated runs. |
| `[不清]` appears as an ordinary black character | Emit the exact marker as a red, bold run and verify the OOXML color and weight. |
| Only a late page or a small sample is delivered | Persist `pNNNN.json` records and a coverage ledger; block final export until every requested source page is classified and accounted for. |
| Page-by-page fragments are mistaken for the final manuscript | Merge prose by semantic paragraph for the reading edition; keep page images in the separate comparison edition. |
| A reference edition silently replaces source characters | Preserve the immutable source layer; reference text may influence punctuation candidates and discrepancy flags only. |
| API failure is confused with an unreadable scan | Use `transport_failed`/`retry_exhausted`, preserve the last error class and attempt count, and resume from the first non-complete page after bounded retries. |
| A title dispute is written directly into the source layer | Require an `accepted|rejected|pending` heading adjudication; reviewer preference without evidence remains a derived review note. |
| A page has high-density unresolved glyphs | Escalate to human review when unresolved glyphs exceed 20 on a page or 1% of its source characters; pending pages cannot be labelled `终校本`. |

## Resumable production contract

Work in batches, but save after every page or small batch. Each page record
must identify the source PDF page, page type, direct-read status, source text,
punctuation layer, unresolved count, and model metadata. The ledger must make
missing, blank, unreadable, rechecked, complete, `transport_failed`, and
`retry_exhausted` pages distinct states. Each unresolved item must include a
page-local locator (`block`, `column`, `character_offset`, or a concise
crop/shape description), candidate readings when available, and the
second-model/adjudication result. A page with more than 20 unresolved glyphs
or more than 1% unresolved source characters is `human_review_required` until
a reviewer resolves or explicitly accepts the uncertainty. Resume from the
first non-complete page; never regenerate a finished page from memory and
never overwrite an earlier deliverable in place.

Before calling a document final, require all of the following:

1. Every requested PDF page is present in the ledger and has a direct-read
   record, including explicit records for blank or non正文 pages.
2. Removing editorial punctuation from each exported section reproduces its
   source character sequence, with `[不清]` treated as the standardized
   unresolved token.
3. The title, volume, article headings, and section order match the scan.
4. All unresolved tokens are red and bold; no black substitute such as a lone
   “不” is used.
5. No page in `human_review_required` or `retry_exhausted` state may be called
   `终校本`; the escalation queue must be empty or explicitly resolved in the
   audit record.
6. The reading DOCX, comparison DOCX, audit records, and completion report are
   separate deliverables. Render DOCX files when LibreOffice is available and
   inspect every rendered page; otherwise disclose the missing render gate.

## Scholarly review handoff

Address a classical-Chinese-literature reviewer in terms of 底本、版本、字形、
异体、通假、讹脱衍倒、训诂、句读、章法 and篇章义理. Ask for feedback as
“源页码 + 卷次/篇题 + 原文定位 + 拟改字或断限 + 所据材料”. A proposed
change to a character requires image or textual evidence; a proposed change to
punctuation requires a stated syntactic or rhetorical reason. Preserve
uncertainty when evidence is insufficient.

## Deliverable scope

The reusable result is more than the two manuscripts. Package the source-page
ledger, immutable direct-read records, punctuation/recheck records, validators,
the completion report, and this Skill's updated routing and quality gates. The
completion report must include a problem retrospective (observed failure,
diagnosis, corrective action, residual risk), the Skill evolution from its
initial rules to the current contract, and its installation/reuse entry points.
It should state which model and channel were actually used, which failures were
found and corrected, what remains uncertain, and how reviewer feedback is fed
into the next rebuild.

## Installation and reuse

From a clean machine, install the Skill from the public repository with:

```powershell
$tmp = Join-Path $env:TEMP 'mercury-archive-agent-install'; git clone --depth 1 --branch codex/ancient-book-typesetter-publish https://github.com/snoopydmgg-lang/mercury-archive-agent.git $tmp; Copy-Item -Recurse -Force (Join-Path $tmp '.agents\skills\ancient-book-typesetter') (Join-Path $env:USERPROFILE '.codex\skills'); Remove-Item -Recurse -Force $tmp
```

For a project-local WorkBuddy/Kimi deployment, copy the same directory into the
project's `.agents\skills\` directory. On first invocation, follow the provider
setup gate and provide that installation's own endpoint, model names, and
secrets; no project-specific key is distributed with this repository.

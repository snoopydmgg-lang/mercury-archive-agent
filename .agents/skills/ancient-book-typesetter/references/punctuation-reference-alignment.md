# Reference Punctuation Alignment

Use this procedure only after a page has a source-faithful multimodal direct
read. The purpose is to borrow *punctuation positions*, not text.

## Input contract

- `source_text`: page text fixed by scan reading, including any `[不清]`.
- `reference_text`: public, punctuated text with a recorded URL and retrieval
  date.
- `editorial_punctuation`: punctuation that may be inserted or moved. Brackets
  belonging to `[不清]` are not editorial punctuation.

## Transfer rule

1. Strip editorial punctuation from the reference, while remembering each
   punctuation boundary.
2. Normalize only alignment-equivalent variants, such as `濳/潜 -> 潛`, in a
   separate comparison layer. Preserve the original source layer unchanged.
3. Compute a character alignment. For each reference punctuation boundary,
   transfer the mark only when the source characters on both sides map to
   contiguous reference characters, or when the boundary is the end of a
   matched run.
4. Do not transfer punctuation across a source `[不清]`, an insertion/deletion
   run, an unmatched title, or an ambiguous repeated phrase.
5. Reject an automatic page result when alignment coverage or transferred
   punctuation coverage falls below the project threshold. Re-read the scan;
   do not fill the gap from the public text.

## Audit fields

Store one record per source page or logical section:

```json
{
  "source_pdf_pages": [6, 7],
  "reference": {
    "url": "https://example.invalid/chapter",
    "retrieved_at": "2026-08-30",
    "use": "punctuation_reference_only"
  },
  "source_characters": 0,
  "aligned_source_characters": 0,
  "alignment_coverage": 0.0,
  "reference_punctuation": 0,
  "transferred_punctuation": 0,
  "punctuation_coverage": 0.0,
  "status": "review_ready|scan_recheck_required",
  "unresolved_reasons": []
}
```

The exported DOCX must retain the fixed source characters. Its audit record
must make a low-confidence result visible rather than masking it with a
complete-looking prose paragraph.

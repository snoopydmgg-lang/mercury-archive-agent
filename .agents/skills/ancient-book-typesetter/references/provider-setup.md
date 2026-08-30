# Provider Setup

This Skill accepts any OpenAI-compatible vision endpoint. The endpoint must
accept a `POST` request to `chat/completions` with a text part and an
`image_url` data URL. Do not assume that a browser login, a dashboard session,
or a provider-specific SDK is available to the agent.

## First-run gate

Before the first page call, collect two local profiles:

| Profile | Required values | Purpose |
| --- | --- | --- |
| primary | `url`, `model`, `api_key` | freezes the source-faithful direct read |
| secondary | `url`, `model`, `api_key` | independent read for cross-validation |

The operator may use one endpoint for both profiles when the model names are
different. The values should be supplied through the host's secret store or
process environment, for example:

```text
ANCIENT_BOOK_PRIMARY_API_URL
ANCIENT_BOOK_PRIMARY_MODEL
ANCIENT_BOOK_PRIMARY_API_KEY
ANCIENT_BOOK_SECONDARY_API_URL
ANCIENT_BOOK_SECONDARY_MODEL
ANCIENT_BOOK_SECONDARY_API_KEY
```

Existing project helpers may use the compatibility aliases
`BIBI_API_URL`, `BIBI_MODEL`, and `BIBI_API_KEY`; map them locally without
writing their values into source files. A URL may be either the full
`.../chat/completions` endpoint or a documented base URL, but normalize it once
and record only the redacted URL (scheme, host, and path; no query strings).

## Connectivity test

Send one harmless, non-page request to each profile with a short text prompt and
no scan. Check HTTP status, JSON shape, and that the returned model is the
requested route. Store only:

```json
{
  "profile": "primary|secondary",
  "provider_host": "api.example.invalid",
  "model": "model-name",
  "status": "ok|configuration_missing|transport_failed",
  "error_class": ""
}
```

Never store the request headers, token, cookies, or unredacted response. Use a
30-second request timeout and at most three attempts with bounded backoff.

## Independent cross-read

For each textual page:

1. Send the scan independently to the primary model and save its direct-read
   JSON.
2. Send the same scan independently to the secondary model and save a separate
   JSON record. Do not include the primary text in this request.
3. Compare ordered columns, headings, source character sequence, and `[不清]`
   positions in a local adjudication pass.
4. Re-read disputed glyphs from the scan. Accept a character only with image
   evidence; otherwise emit red, bold `[不清]` and retain both candidates in the
   audit record.

The public edition, if consulted, can suggest punctuation boundaries or flag a
title discrepancy only after these two source reads are fixed. It cannot replace
either model's source characters.

## Failure states

Use `configuration_missing` when a required URL, model, or key is absent;
`transport_failed` for a failed attempt; and `retry_exhausted` when the bounded
retry budget is spent. These states are distinct from an unreadable scan and
must remain visible in the ledger. A page with only one successful model read is
not `cross_validated` and cannot be labelled `终校本`.

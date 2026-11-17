# signed-webhook-submit

A GitHub Action that POSTs a canonical JSON payload (sorted keys, compact separators, UTF-8) signed with HMAC-SHA256 in an `X-Signature-256` header, then prints the receipt from the response.

- `submit.py` builds the payload, signs it, sends it, and prints the receipt.
- `.github/workflows/submit.yml` runs the script on demand (Actions → Submit application → Run workflow).
- The signing secret is read from the `B12_SIGNING_SECRET` repository secret.

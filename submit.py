"""Submit an application to B12 from CI with an HMAC-signed, canonical JSON body."""
import hashlib
import hmac
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

URL = "https://b12.io/apply/submission"


def canonical_body(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


def sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def main() -> int:
    secret = os.environ["B12_SIGNING_SECRET"]
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "name": os.environ["APPLICANT_NAME"],
        "email": os.environ["APPLICANT_EMAIL"],
        "resume_link": os.environ["RESUME_LINK"],
        "repository_link": f"{server}/{repo}",
        "action_run_link": f"{server}/{repo}/actions/runs/{run_id}",
    }
    body = canonical_body(payload)
    req = urllib.request.Request(
        URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "X-Signature-256": sign(body, secret)},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}", file=sys.stderr)
        return 1

    if not data.get("success"):
        print(f"Submission failed: {data}", file=sys.stderr)
        return 1
    print(f"Receipt: {data['receipt']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

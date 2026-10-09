# Native n8n integration: 7/7 verified

**Evidence date:** 9 October 2026, 18:09 UTC  
**Engine:** Official n8n 2.42.6 Docker image on an isolated GitHub Actions Linux runner  
**Result:** All **seven real n8n webhook-to-REST-API tests passed**.

[View passing GitHub Actions run](https://github.com/mrwanahmedx/mrwanahmedx.github.io/actions/runs/37971158690) · [Original test logs and JSON artifact](https://github.com/mrwanahmedx/mrwanahmedx.github.io/actions/runs/37971158690/artifacts/11634988933) · [Machine-readable evidence summary](native_e2e_summary.json)

## What was executed

GitHub Actions pulled the official pinned n8n image, imported workflow_n8n.json, published and activated it, started the n8n webhook server on loopback, started the project's local Python/SQLite Job Form API, and sent actual HTTP POST messages through n8n's Webhook, Code, IF and HTTP Request nodes. The test runner verified response JSON, persisted jobs, duplicate prevention and recovery from a simulated HTTP 503.

| Live native test | Observed result |
|---|---|
| Valid English camera-operator job | PASS — submitted |
| Repeat same English message | PASS — duplicate detected |
| Arabic editor job in Sharjah | PASS — submitted |
| Simulated transient API failure | PASS — retried and submitted |
| Ordinary group conversation | PASS — ignored |
| Job with missing city | PASS — flagged for review |
| Private WhatsApp-format chat | PASS — ignored |

**Database reconciliation:** Three unique jobs inserted; the retry scenario generated two destination attempts. The runner's LIVE_E2E_7_OF_7_PASS assertion confirms all individual checks and database counts.

## Boundaries

The input was synthetic WAHA-shaped group-message JSON. There is **no connected WhatsApp account or actual WAHA gateway**, **no customer's live Job Posting Form API**, **no structured-output LLM provider**, **no production deployment**, and **no claimed paid client delivery**. The public interactive website runs the workflow's real Code-node functions; the GitHub Actions proof independently verifies the full native n8n HTTP path. These are different test layers.

The original test artifact is retained by GitHub Actions for 14 days; run logs and this summary remain source-linked. All test data was synthetic and contained no credentials.

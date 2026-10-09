# Bilingual Job-Post Intake Automation — n8n + Webhooks + Python API

**Self-directed, n8n 2.42.6 native-integration-verified prototype | 7/7 tests passed | English + Arabic**

## The problem
Job announcements arrive as free-form WhatsApp group messages. Someone must decide whether each message is a real job posting, read the details, manually enter the listing into an API form, and handle duplicates or incomplete posts. Arabic-English formatting differences and temporarily unavailable APIs make the manual process harder.

## The automation
I built an importable n8n workflow that receives WAHA-shaped WhatsApp events through a Webhook, normalizes the message metadata, categorizes hiring posts, extracts role/city/pay/date, validates mandatory fields, and POSTs structured JSON to an actual local test API.

The workflow uses **real n8n Webhook, Code, IF, HTTP Request and Respond to Webhook nodes**. A local Python-backed REST API persists jobs into SQLite, prevents repeated submission via stable external IDs, and simulates transient API outages to exercise n8n's retry policy. Unsupported or vague posts are not silently pushed into the destination; they are ignored or flagged for review.

## Sample message to output
English input:
"Hiring a freelance Camera Operator in Dubai for an event on 15/10/2026. Pay AED 800."

Structured result:
{
  "title": "Camera Operator",
  "city": "Dubai",
  "language": "en",
  "employment_type": "freelance",
  "pay": "AED 800",
  "work_date": "15/10/2026"
}

Arabic input:
"مطلوب مونتير في الشارقة يوم 16/10/2026، الأجر 700 درهم."

Structured result:
{
  "title": "مونتير",
  "city": "Sharjah",
  "language": "ar",
  "pay": "700 درهم",
  "work_date": "16/10/2026"
}

## Technical stack
n8n workflow JSON; webhook event normalization; JavaScript in n8n Code nodes; native n8n IF and HTTP Request nodes; Python 3.12 local REST receiver; SQLite storage; seven-case native n8n webhook-to-API test runner, independently passed on an isolated GitHub Actions server.

## Project files and proof
- workflow_n8n.json — actual editable/importable n8n automation.
- demo_api.py — REST API with SQLite persistence and deduplication.
- test_workflow.py — sends synthetic English/Arabic WAHA messages through the real n8n webhook.
- evidence/NATIVE_E2E_VERIFIED.md — independently verified 7/7 native execution results; original JSON and logs retained in GitHub Actions artifact.
- README.md — runbook, source and real-versus-simulated disclosures.

## Boundaries and honesty
This portfolio demonstration is not a claim of past customer delivery. Messages are synthetic and no real WhatsApp group is connected. A customer's actual posting form API and live WAHA instance were not available, so the prototype uses a real local HTTP API in their place. This version uses deterministic bilingual extraction rules, not a paid LLM; production work would add an approved structured-output model, customer schema mapping, validated WAHA authentication, monitoring and deployment.

The value demonstrated is a working, testable automation architecture and reliable handoff—not fictional cost savings or 24/7 production uptime.

## Latest test evidence

50/50 original synthetic messages passed against embedded n8n Code-node JavaScript; 4/4 local HTTP API unit tests passed; **7/7 native n8n webhook-to-API integration tests passed** with real HTTP submission, API retry and SQLite persistence in an isolated official n8n Docker environment on October 9, 2026. The demonstration still uses synthetic WAHA-format input; no real WhatsApp connection, LLM model, live customer API or production hosting is claimed. An authentic workflow architecture diagram and observed input/output examples are included in portfolio_assets/.


[**See the successful seven-test native n8n run and its logs**](https://github.com/mrwanahmedx/mrwanahmedx.github.io/actions/runs/37971158690) · [Detailed evidence](evidence/NATIVE_E2E_VERIFIED.md)

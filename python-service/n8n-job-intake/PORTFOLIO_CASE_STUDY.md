# Bilingual Job-Post Intake Automation — n8n + Webhooks + Python API

**Self-directed, code-verified prototype | native n8n integration pending | English + Arabic**

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
n8n workflow JSON; webhook event normalization; JavaScript in n8n Code nodes; native n8n IF and HTTP Request nodes; Python 3.12 local REST receiver; SQLite storage; seven-case native n8n live workflow test runner (prepared, not yet passed).

## Project files and proof
- workflow_n8n.json — actual editable/importable n8n automation.
- demo_api.py — REST API with SQLite persistence and deduplication.
- test_workflow.py — sends synthetic English/Arabic WAHA messages through the real n8n webhook.
- evidence/integration_test_results.json — only generated when end-to-end tests succeed.
- README.md — runbook, source and real-versus-simulated disclosures.

## Boundaries and honesty
This portfolio demonstration is not a claim of past customer delivery. Messages are synthetic and no real WhatsApp group is connected. A customer's actual posting form API and live WAHA instance were not available, so the prototype uses a real local HTTP API in their place. This version uses deterministic bilingual extraction rules, not a paid LLM; production work would add an approved structured-output model, customer schema mapping, validated WAHA authentication, monitoring and deployment.

The value demonstrated is a working, testable automation architecture and reliable handoff—not fictional cost savings or 24/7 production uptime.

## Latest test evidence

50/50 original synthetic messages passed against embedded n8n Code-node JavaScript; separately, 4/4 local HTTP API unit tests passed. No native n8n workflow execution, real WhatsApp integration, or LLM model run has yet been verified. An authentic workflow architecture diagram and observed input/output examples are included in portfolio_assets/.

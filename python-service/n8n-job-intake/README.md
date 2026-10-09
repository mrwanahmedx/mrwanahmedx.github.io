# WAHA WhatsApp Group to UAE Job Form API — a real n8n portfolio project

This repository contains a real ten-node n8n workflow, verified in the official n8n 2.42.6 engine with **7/7 native webhook-to-API integration tests passing**. The test runner imports, publishes and executes the workflow in an isolated GitHub Actions environment.

## Problem
A UAE film/TV/events platform currently receives English and Arabic job posts in a WhatsApp group. The team manually copies these posts into a Job Posting Form API. We built a realistic local demonstration of the workflow.

## Actual workflow
Import workflow_n8n.json into n8n. It has ten connected n8n nodes:

1. WAHA Incoming Message — POST Webhook trigger
2. Normalize WAHA Payload — Code node extracting group, message ID and text
3. Classify and Extract Job — Code node parsing English/Arabic hiring messages
4. Complete Job Details? — native IF node
5. Submit to Demo Job API — native HTTP Request node; retry-on-failure
6. Prepare Submission Receipt — Code
7. Respond Accepted — native Respond to Webhook
8. Prepare Error Receipt — Code
9. Respond API Failure — native Respond to Webhook, HTTP 502
10. Respond Ignored or Review — native Respond to Webhook

Live local demo API: demo_api.py, hosted on 127.0.0.1:8767. Real SQLite persistence in state/jobs.sqlite3 (unique external IDs prevent duplicate jobs). API can return a simulated 503 on its first delivery to test n8n retries.

An extraction is auto-submitted only when it has a clear supported job role and a UAE city. Incomplete messages are marked needs_review; non-job messages and private chats are ignored.

## Verified functions vs not connected
- **Native n8n execution verified (7/7):** incoming webhook, Code, IF, HTTP request, retry and response paths, with a real local Python/SQLite receiver. Independent Code-node and API unit tests also passed.
- WAHA WhatsApp group integration: synthetic WAHA-shaped webhook fixtures only; real WhatsApp account NOT connected.
- External client form API: local real HTTP service substitutes for unspecified customer API.
- LLM extraction: NOT implemented; clear deterministic rules are used. Do not claim this workflow includes OpenAI/Claude/Arabic LLM extraction.
- Production 24/7 hosting: NOT provided or claimed.

## Independent native execution proof

- **[Passing GitHub Actions run — 7/7 native integration tests](https://github.com/mrwanahmedx/mrwanahmedx.github.io/actions/runs/37971158690)**
- [Evidence table and exact limitations](evidence/NATIVE_E2E_VERIFIED.md)
- [Machine-readable seven-test summary](evidence/native_e2e_summary.json)
- [Original detailed execution artifact](https://github.com/mrwanahmedx/mrwanahmedx.github.io/actions/runs/37971158690/artifacts/11634988933)

On October 9, 2026, GitHub Actions imported and published the actual workflow in the official n8n 2.42.6 Docker image. Actual English and Arabic messages reached the webhook and a local SQLite-backed HTTP API. Tests verified three inserted jobs, idempotent duplicates, simulated HTTP 503 recovery, ignored non-jobs, manual review and private-chat rejection. This is a **synthetic local integration test**, not a real WhatsApp, LLM or production deployment.

## Local requirements and endpoints
Local Windows, Node.js 20.19–24.x and Python 3.12+.
D:\ChatGPT\Freelancing\n8n_WhatsApp_Job_Intake is the project root.
An n8n 2.42.6 installation was attempted under runtime/node_modules/n8n. Its binary version check passed, but dependency installation and native import did not finish. The workflow JSON is ready for import into an existing working n8n instance, or this isolated D: installation can be completed later.
Keep npm cache and n8n user data on D:; C: is almost full.
Editor: http://127.0.0.1:5679
Webhook: http://127.0.0.1:5679/webhook/portfolio-waha-jobs-v1
Local JSON API: http://127.0.0.1:8767 (GET /health, /stats, /jobs; POST /jobs)

After completing n8n installation and successful workflow import, start both services using START_DEMO_SILENT.pyw. Import workflow_n8n.json and publish workflow. n8n production webhook requires the workflow to be published; test webhooks instead require Listen for test event. If you run n8n outside localhost, add proper webhook auth and signed validation first.

Execute tests through python test_workflow.py. The script makes seven actual HTTP requests to the n8n production webhook:
- English job submitted
- Same message deduplicated
- Arabic job submitted
- Simulated transient API HTTP 503 recovered by n8n retry
- Non-job message ignored
- Job with missing city routed to review
- Private WhatsApp conversation ignored

The test checks a real DB count increment, Arabic city extraction, and retry count, then writes evidence/integration_test_results.json. A test file without successful execution is not proof.

## Production adaptation
To integrate with real WAHA + a client's posting API: obtain permission and documented event format; use HTTPS with authenticated webhook, group allowlist, real API credentials via n8n Credentials, rate limiting, retention, secure queue/dead-letter workflow, structured-output LLM (if approved), monitoring, and deployment. Do not paste credentials in workflow export or published portfolio.

The deterministic parser is intentionally conservative and not sufficient for all free-form Arabic, slang, multiple jobs in one message, or every event type. A buyer contract would require schema details, provider auth, an LLM step, and real-world acceptance tests.

## Files
workflow_n8n.json — n8n workflow
demo_api.py — SQLite-backed local job API
generate_workflow.py — reproducible workflow JSON generator
test_workflow.py — end-to-end tests
state/ — SQLite db, excluded from deliverables
runtime/, npm-cache/, n8n-user/ — local n8n binaries/cache/user data, excluded from portfolio distribution
evidence/ — live test results after actual execution
PORTFOLIO_CASE_STUDY.md — accurate Upwork-ready portfolio description

Self-directed demonstration project, not a paid client delivery.

## Offline 50-message evidence

The embedded n8n Code-node JavaScript was evaluated against 50 original synthetic English/Arabic/negative/incomplete messages. All 50 passed after fixes to Arabic-Indic digits, salary shorthand (for example 2k/day), and a false-positive non-job example. This is offline Code-node evaluation, NOT native n8n webhook execution or production accuracy. See evidence/synthetic_50_code_node_results.json and portfolio_assets/verified_examples.md. The workflow architecture SVG is automatically generated from the actual node graph, not an n8n editor screenshot.

## Single-group allowlist

The demonstration accepts only 120300011122@g.us (synthetic group ID). Other groups are ignored. Replace the ID with the client's approved group and configure authenticated webhook delivery before production. WAHA is not connected.

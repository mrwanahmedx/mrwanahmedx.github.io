# UPWORK PORTFOLIO — DRAFT FOR REVIEW (NOT PUBLISHED)

## Suggested title
Bilingual Job-Post Automation — n8n Workflow + Python API Prototype

## Description
I built a self-directed automation prototype for routing English and Arabic job announcements into structured job records.

The project contains a real, importable 10-node n8n workflow definition with webhook intake, single-group filtering, field extraction, validation, HTTP submission, and accepted/error response paths. The demonstration API is built with Python and SQLite and handles duplicate submissions and simulated temporary failures.

The embedded JavaScript extraction logic passed 50/50 original synthetic message tests. A separately launched local HTTP API passed 4/4 unit tests.

**Demonstrated capabilities:** API workflows, n8n Code-node JavaScript, webhook payload handling, Arabic/English parsing, data validation, SQLite, idempotency, and test-driven prototyping.

**Transparency:** This is an original portfolio prototype, not a past client project. The messages are synthetic. The demo uses deterministic extraction rather than a live LLM, and native n8n webhook execution is not yet independently verified. No real WAHA WhatsApp group or customer API has been connected.

Production work would require an approved WhatsApp integration, authenticated webhook, customer-specific field schema, LLM selection and validation, end-to-end tests, monitoring, and deployment.

## Suggested gallery
1. portfolio_assets/01_real_workflow_architecture.png — diagram derived from real workflow JSON, not an n8n editor screenshot.
2. portfolio_assets/02_real_input_output.png — tested message with actual observed JavaScript output.
3. portfolio_assets/03_test_evidence.png — measured offline tests and outstanding native validation.

## Technical evidence
- workflow_n8n.json — editable 10-node workflow definition.
- evidence/synthetic_50_code_node_results.json — verified test records.
- portfolio_assets/verified_examples.md — observed English and Arabic outputs.
- demo_api.py and test_local_api.py — actual REST/SQLite demonstration.

## Positioning
Do not change the main Upwork headline to 'n8n expert' yet.
Do not claim deployed WAHA, live model integration, a completed client project, 40 real WhatsApp test messages, or 24/7 uptime.
Do not publish an n8n paid Project Catalog offer until native testing and delivery scope are verified.

## Next validation
Import workflow_n8n.json into a functioning n8n instance with adequate RAM, connect it to the local demo API, trigger test_workflow.py, then capture genuine editor screenshots. Only after a passed native test update this case study with native execution claims.

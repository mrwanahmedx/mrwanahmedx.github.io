# Reproducible message extraction examples
These are observed outputs from executing JavaScript embedded in the actual workflow Code nodes.
All inputs are original synthetic data. This is not native n8n webhook, real WhatsApp, or LLM proof.

Offline embedded-code tests: 50/50 passed.

## en01
Input: Hiring Camera Operator in Dubai. AED 800.

Observed output:
```json
{
  "state": "ready",
  "job": {
    "external_id": "demo-waha-106008e7",
    "title": "Camera Operator",
    "city": "Dubai",
    "language": "en",
    "employment_type": "unspecified",
    "pay": "AED 800",
    "work_date": "",
    "source": "waha-webhook",
    "test_retry": false
  },
  "confidence": 0.95
}
```

## en16
Input: Hiring a camera person in Dubai AED 2k/day.

Observed output:
```json
{
  "state": "ready",
  "job": {
    "external_id": "demo-waha-0f6245eb",
    "title": "Camera Operator",
    "city": "Dubai",
    "language": "en",
    "employment_type": "unspecified",
    "pay": "AED 2k/day",
    "work_date": "",
    "source": "waha-webhook",
    "test_retry": false
  },
  "confidence": 0.95
}
```

## ar02
Input: مطلوب مصور في أبو ظبي

Observed output:
```json
{
  "state": "ready",
  "job": {
    "external_id": "demo-waha-d8519ba2",
    "title": "مصور",
    "city": "Abu Dhabi",
    "language": "ar",
    "employment_type": "unspecified",
    "pay": "",
    "work_date": "",
    "source": "waha-webhook",
    "test_retry": false
  },
  "confidence": 0.8999999999999999
}
```

## ar16
Input: مطلوب مونتير بدبي الأجر ٢٠٠٠ درهم

Observed output:
```json
{
  "state": "ready",
  "job": {
    "external_id": "demo-waha-d653d713",
    "title": "مونتير",
    "city": "Dubai",
    "language": "ar",
    "employment_type": "unspecified",
    "pay": "2000 درهم",
    "work_date": "",
    "source": "waha-webhook",
    "test_retry": false
  },
  "confidence": 0.95
}
```

## no02
Input: صباح الخير للجميع

Observed output:
```json
{
  "state": "ignored",
  "reason": "non_job_message",
  "external_id": "demo-waha-ccc8c36e"
}
```

## rv02
Input: مطلوب مونتير بشكل عاجل

Observed output:
```json
{
  "state": "needs_review",
  "reason": "missing_required_fields",
  "missing_fields": [
    "UAE_city"
  ],
  "external_id": "demo-waha-b3da44ed",
  "language": "ar",
  "confidence": 0.7
}
```

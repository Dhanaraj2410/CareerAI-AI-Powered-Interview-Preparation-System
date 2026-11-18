# API notes

The project exposes Django-backed endpoints for accounts, interviews, aptitude exercises, coding challenges, resumes, and feedback. Health information is available at `/health-check/`.

Use authenticated requests where required and treat API responses as implementation details unless an endpoint is documented for client integration.

## Dashboard progress

`GET /api/dashboard/progress` requires an authenticated session and returns the
latest measured scores, seven daily activity buckets, the current streak, and
the recommended next action. A score is `null` until the user completes that
practice area; clients should render this as “Not started” rather than zero.

Example response shape:

```json
{
  "scores": {"aptitude": null, "resume": 81.5, "technical": 74.0, "communication": 68.0},
  "overall": 74.5,
  "activity": [{"date": "2026-11-18", "label": "Wed", "count": 2}],
  "streak": 2,
  "active_days": 4,
  "next_action": {
    "label": "Take an aptitude assessment",
    "url_name": "aptitude_home",
    "reason": "Build your first measurable baseline."
  }
}
```


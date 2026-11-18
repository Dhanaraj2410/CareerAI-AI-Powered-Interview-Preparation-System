# Release checklist

Before releasing, review migrations, run system checks and tests, verify environment variables, confirm static and media handling, inspect dependency changes, and push the release commit only after the working tree is clean.

For dashboard changes, verify a new account sees “Not started”, an account
with activity sees real scores and a seven-day pulse, and an authenticated
request to `/api/dashboard/progress` returns the same values.


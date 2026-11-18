# Deployment notes

Set `DEBUG=False`, provide a strong `SECRET_KEY`, and configure `ALLOWED_HOSTS` for the deployed hostname. Use a managed MySQL database when persistent production data is required.

Run `python manage.py check --deploy` as part of the release checklist and collect static assets with `python manage.py collectstatic`.

WhiteNoise is included in the production dependency set and serves collected
static files when installed. The settings module also skips that middleware
when the package is unavailable, which keeps SQLite-based local checks usable;
production deployments should still install all entries from `requirements.txt`.


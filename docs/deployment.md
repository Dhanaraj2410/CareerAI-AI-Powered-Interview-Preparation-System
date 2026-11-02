# Deployment notes

Set `DEBUG=False`, provide a strong `SECRET_KEY`, and configure `ALLOWED_HOSTS` for the deployed hostname. Use a managed MySQL database when persistent production data is required.

Run `python manage.py check --deploy` as part of the release checklist and collect static assets with `python manage.py collectstatic`.


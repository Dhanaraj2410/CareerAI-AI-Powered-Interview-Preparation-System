# Troubleshooting

- If migrations fail, confirm the selected database and run `python manage.py migrate`.
- If AI features are unavailable, verify `GEMINI_API_KEY` and the configured model name.
- If static files are missing, run `python manage.py collectstatic` and check `STATIC_ROOT`.
- If uploads fail, confirm the media directory is writable in development.


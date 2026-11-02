# Database guidance

SQLite is suitable for local development. For MySQL, set `USE_MYSQL=True` and provide `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. Apply migrations after changing models and back up production data before migration work.


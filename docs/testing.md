# Testing and validation

Run Django's system checks before submitting changes:

```bash
python manage.py check
python manage.py test
```

For changes that affect migrations, run `python manage.py makemigrations --check` and apply migrations against a disposable development database.

# Testing CareerAI

Run the Django system checks and the full test suite against SQLite for a
repeatable local or CI run:

```powershell
$env:USE_MYSQL = "False"
$env:DEBUG = "True"
$env:SECRET_KEY = "test-only-secret-key"
C:/Users/Admin/anaconda3/python.exe manage.py check
C:/Users/Admin/anaconda3/python.exe manage.py test
```

The suite covers registration, aptitude scoring, CORS origin handling, resume
API ownership boundaries, and dashboard progress calculations. Keep new
endpoint behavior covered by a test before changing it.

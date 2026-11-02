# Testing and validation

Run Django's system checks before submitting changes:

```bash
python manage.py check
python manage.py test
```

For changes that affect migrations, run `python manage.py makemigrations --check` and apply migrations against a disposable development database.


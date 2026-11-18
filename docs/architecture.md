# Architecture overview

CareerAI is a Django project organized into focused apps: accounts, interview, aptitude, resumes, feedback, and machine-learning support. Templates provide the browser UI while app views, services, models, and API modules keep domain behavior close to its owning app.

Derived candidate progress lives in `accounts/progress.py` so the dashboard,
feedback generation, and authenticated client API share one source of truth.
The service reads domain records without adding duplicated aggregate state to
the database.


# Operations Runbook — Revenue Intelligence for Stripe Commerce (PureLaka)

This runbook describes how to run, validate, and operate the system safely.

---

## 1) Quick start (local dev — SQLite)

### Prerequisites
- Python 3.12.x
- Windows PowerShell
- Virtual environment tooling available

### Install + run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver

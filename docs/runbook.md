# PureLaka Enterprise — Runbook

Project: PureLaka_Commerce_Platform_LAUNCH_READY  
Stack: Django 5.2.10, Python 3.12.3 (Windows)

## 1) Definition-of-Done Gates (must stay green)

Run from project root with venv active:

```powershell
python manage.py test
python manage.py test analyticsapp -v 2
python manage.py run_checks --fail-on-issues

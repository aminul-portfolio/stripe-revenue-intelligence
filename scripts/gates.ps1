Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== PureLaka Gates =="

python manage.py check
python manage.py test
python manage.py run_checks --fail-on-issues
python manage.py makemigrations --check --dry-run

ruff check .
ruff format --check .

pip-audit -r requirements.txt

Write-Host "== ALL GATES PASSED =="

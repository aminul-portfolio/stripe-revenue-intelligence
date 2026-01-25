# Operations Runbook — Revenue Intelligence for Stripe Commerce (PureLaka)

This runbook explains how to run, validate, and operate the system safely.
It is written so a reviewer can reproduce “green gates” and understand the operational controls.

---

## 0) Quick facts (what this system is)
- **Product:** Stripe-first revenue analytics + operational controls (KPIs, exports, RBAC, audit, monitoring checks).
- **Primary reviewer goal:** run locally, seed demo data, verify dashboards/exports, and reproduce “gates green”.

---

## 1) Quick start (local dev — SQLite)

### 1.1 Prerequisites
- Python 3.12.x
- Windows PowerShell
- Git
- (Optional) VS Code

### 1.2 Create venv + install deps
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

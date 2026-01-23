# Operations Runbook — Revenue Intelligence for Stripe Commerce

This runbook describes how to run, validate, and operate the system safely.

## 1) Quick start (local dev)

## 2) Postgres parity (local) — Buyer-ready baseline (M4.1)

Purpose: prove the app runs and passes gates against Postgres (not only SQLite).

### Start Postgres parity via Docker Compose

```powershell
docker compose up -d --build
docker compose ps

### Prerequisites
- Python 3.12.x
- Virtual environment activated
- SQLite (dev default)

### Install
```bash
python -m pip install -U pip
pip install -r requirements.txt

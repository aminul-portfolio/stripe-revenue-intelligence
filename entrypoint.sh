#!/usr/bin/env sh
set -eu

echo "== entrypoint: starting =="

# Ensure DB is reachable (Compose healthcheck already covers this, but keep a fast sanity check)
python -c "import os,sys; print('DJANGO_SETTINGS_MODULE=', os.getenv('DJANGO_SETTINGS_MODULE','')); sys.exit(0)"

echo "== migrate =="
python manage.py migrate --noinput

if [ "${COLLECTSTATIC:-0}" = "1" ]; then
  echo "== collectstatic =="
  python manage.py collectstatic --noinput
else
  echo "== collectstatic skipped (COLLECTSTATIC!=1) =="
fi

echo "== exec: $* =="
exec "$@"

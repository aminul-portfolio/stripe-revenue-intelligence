from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.http import require_GET

from accounts.decorators import role_required
from .models import DataQualityIssue
from .services.run_all import run_all_checks


@role_required("ops", "analyst", staff_only=True)
def issues(request):
    if request.method == "POST":
        run_all_checks()
    rows = DataQualityIssue.objects.all()[:200]
    return render(request, "monitoring/issues.html", {"issues": rows})


def _db_ready() -> tuple[bool, str | None]:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return True, None
    except Exception as exc:
        return False, str(exc)


@require_GET
def healthz(request):
    db_ok, db_err = _db_ready()

    payload = {
        "service": "stripe-revenue-intelligence",
        "time": now().isoformat(),
        "checks": {"db": db_ok},
        "status": "ok" if db_ok else "not-ready",
    }

    if not db_ok:
        payload["errors"] = {"db": (db_err or "unknown")[:200]}
        return JsonResponse(payload, status=503)

    return JsonResponse(payload, status=200)

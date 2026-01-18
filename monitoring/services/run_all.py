from __future__ import annotations

import time
import traceback
from typing import Callable, Any

from audit.services.logger import log_event
from monitoring.checks.analytics_snapshot_reconciliation import (
    run_analytics_snapshot_reconciliation,
)
from monitoring.checks.refund_reconciliation import run_refund_reconciliation
from monitoring.services.order_state_checks import check_invalid_order_states
from monitoring.services.payment_checks import check_payment_reconciliation
from monitoring.services.stock_checks import check_stock_anomalies


def _compact_traceback(tb: str, *, max_chars: int = 6000) -> str:
    """
    Prevent audit log bloat. Keeps the tail of traceback (usually the most useful part).
    """
    tb = (tb or "").strip()
    if len(tb) <= max_chars:
        return tb
    return "…(truncated)…\n" + tb[-max_chars:]


def run_all_checks() -> dict[str, Any]:
    """
    Enterprise monitoring runner:
    - Stable order
    - Resilient execution (one failure doesn't block others)
    - Emits audit event if a check fails
    - Returns summary (useful for CI/ops)
    """
    checks: list[tuple[str, Callable[[], None]]] = [
        ("payment_reconciliation", check_payment_reconciliation),
        ("refund_reconciliation", run_refund_reconciliation),
        ("analytics_snapshot_reconciliation", run_analytics_snapshot_reconciliation),
        ("invalid_order_states", check_invalid_order_states),
        ("stock_anomalies", check_stock_anomalies),
    ]

    started = time.perf_counter()
    results: dict[str, Any] = {
        "ok": [],
        "failed": [],
        "timings_ms": {},  # per-check runtime
        "total_ms": 0,
        "status": "ok",  # "ok" or "degraded"
    }

    for name, fn in checks:
        t0 = time.perf_counter()
        try:
            fn()
            results["ok"].append(name)
        except Exception as exc:
            results["failed"].append(name)

            tb = traceback.format_exc()
            log_event(
                event_type="monitoring_check_failed",
                entity_type="monitoring",
                entity_id=name,
                metadata={
                    "check": name,
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                    "traceback": _compact_traceback(tb),
                },
            )
        finally:
            results["timings_ms"][name] = int((time.perf_counter() - t0) * 1000)

    results["total_ms"] = int((time.perf_counter() - started) * 1000)
    results["status"] = "ok" if not results["failed"] else "degraded"

    log_event(
        event_type="monitoring_checks_completed",
        entity_type="monitoring",
        entity_id="run_all_checks",
        metadata={
            "status": results["status"],
            "ok": results["ok"],
            "failed": results["failed"],
            "timings_ms": results["timings_ms"],
            "total_ms": results["total_ms"],
        },
    )

    return results

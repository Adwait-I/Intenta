"""
INTENTA — Observability: Metrics
Lightweight in-memory counters + hooks for Prometheus-style export.
These can be scraped by a metrics endpoint or exported to Prometheus via push gateway.
"""
from __future__ import annotations
import time
from collections import defaultdict
from threading import Lock

_lock = Lock()

_counters: dict[str, int] = defaultdict(int)
_histograms: dict[str, list[float]] = defaultdict(list)
_gauges: dict[str, float] = {}


def record_request(success: bool, duration_ms: float) -> None:
    """Called for every /generate request."""
    with _lock:
        _counters["requests_total"] += 1
        if success:
            _counters["requests_success"] += 1
        else:
            _counters["requests_failed"] += 1
        _histograms["request_duration_ms"].append(duration_ms)


def record_llm_call(model: str, duration_ms: float, success: bool) -> None:
    """Track LLM call latency and success rate."""
    with _lock:
        key = f"llm_{model}"
        _counters[f"{key}_calls_total"] += 1
        if not success:
            _counters[f"{key}_errors_total"] += 1
        _histograms[f"{key}_duration_ms"].append(duration_ms)


def set_gauge(name: str, value: float) -> None:
    """Set a point-in-time gauge value."""
    with _lock:
        _gauges[name] = value


def get_metrics_snapshot() -> dict:
    """Return a snapshot of all current metrics."""
    with _lock:
        snapshot: dict = {
            "counters": dict(_counters),
            "gauges": dict(_gauges),
            "histograms": {},
        }
        for key, values in _histograms.items():
            if values:
                sorted_v = sorted(values)
                n = len(sorted_v)
                snapshot["histograms"][key] = {
                    "count": n,
                    "min": round(sorted_v[0], 2),
                    "max": round(sorted_v[-1], 2),
                    "mean": round(sum(sorted_v) / n, 2),
                    "p50": round(sorted_v[int(n * 0.5)], 2),
                    "p95": round(sorted_v[int(n * 0.95)], 2),
                    "p99": round(sorted_v[int(n * 0.99)], 2),
                }
        return snapshot

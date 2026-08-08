from __future__ import annotations

from typing import Any, Dict


def calculate_health_score(metric: Dict[str, Any]) -> int:
    latency = float(metric.get("latency_ms", 0) or 0)
    packet_loss = float(metric.get("packet_loss_pct", 0) or 0)
    disconnects = int(metric.get("disconnects", 0) or 0)
    connected_devices = int(metric.get("connected_devices", 0) or 0)
    signal = int(metric.get("signal_dbm", -60) or -60)
    is_bad = bool(metric.get("is_bad", False))

    score = 100
    score -= max(0, (latency - 60) * 0.18)
    score -= max(0, packet_loss * 4.2)
    score -= disconnects * 5
    score -= max(0, (connected_devices - 120) * 0.18)
    score -= max(0, (-signal - 45) * 1.8)

    if is_bad:
        score -= 25

    score = max(0, min(100, round(score)))
    return int(score)

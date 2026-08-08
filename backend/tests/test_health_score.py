from datetime import datetime

from backend.services.health_score import compute_health_score
from backend.services.data_loader import RouterMetric


def test_compute_health_score_healthy_router():
    metrics = [
        RouterMetric(
            router_id="R-1000",
            hour=datetime(2026, 8, 6, 0, 0),
            avg_speed_mbps=80.0,
            latency_ms=20.0,
            packet_loss_pct=0.2,
            disconnects=0.0,
            connected_devices=12,
            signal_dbm=-48.0,
        )
        for _ in range(48)
    ]
    summary = compute_health_score(metrics, complaint_count=0)
    assert summary.score >= 80.0
    assert summary.label == "healthy"
    assert summary.primary_issue in {"speed", "latency", "packet_loss", "disconnects", "signal"}


def test_compute_health_score_poor_router():
    metrics = [
        RouterMetric(
            router_id="R-1042",
            hour=datetime(2026, 8, 6, 0, 0),
            avg_speed_mbps=18.0,
            latency_ms=145.0,
            packet_loss_pct=4.2,
            disconnects=1.2,
            connected_devices=22,
            signal_dbm=-78.0,
        )
        for _ in range(48)
    ]
    summary = compute_health_score(metrics, complaint_count=3)
    assert summary.score < 50.0
    assert summary.label == "poor"
    assert summary.primary_issue in {"speed", "latency", "packet_loss", "disconnects", "signal"}

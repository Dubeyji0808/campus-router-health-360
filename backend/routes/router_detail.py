from typing import List, Optional

from fastapi import APIRouter, HTTPException

from services.data_loader import ComplaintTicket, RouterInventory, RouterMetric, load_all_data
from services.health_score import build_health_summary, RouterHealthScore

router = APIRouter()


def map_metric(metric: RouterMetric) -> dict:
    return {
        "hour": metric.hour.isoformat(),
        "avg_speed_mbps": metric.avg_speed_mbps,
        "latency_ms": metric.latency_ms,
        "packet_loss_pct": metric.packet_loss_pct,
        "disconnects": metric.disconnects,
        "connected_devices": metric.connected_devices,
        "signal_dbm": metric.signal_dbm,
    }


@router.get("/router/{router_id}")
def get_router_detail(router_id: str):
    inventories, metrics_by_router, complaints_by_router = load_all_data()
    scores = build_health_summary()
    summary = scores.get(router_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Router not found")

    inventory = inventories.get(router_id)
    metrics = metrics_by_router.get(router_id, [])
    complaints = complaints_by_router.get(router_id, [])

    return {
        "router_id": router_id,
        "summary": {
            "score": summary.score,
            "label": summary.label,
            "health_score": summary.score,
            "avg_speed_mbps": summary.avg_speed_mbps,
            "avg_latency_ms": summary.avg_latency_ms,
            "avg_packet_loss_pct": summary.avg_packet_loss_pct,
            "avg_disconnects": summary.avg_disconnects,
            "avg_signal_dbm": summary.avg_signal_dbm,
            "bad_hours_percent": round(summary.bad_hour_ratio * 100, 1),
            "complaint_count": summary.complaint_count,
            "primary_issue": summary.primary_issue,
        },
        "inventory": {
            "model": inventory.model if inventory else None,
            "firmware_version": inventory.firmware_version if inventory else None,
            "building": inventory.building if inventory else None,
            "room": inventory.room if inventory else None,
            "user_type": inventory.user_type if inventory else None,
            "issue_date": inventory.issue_date.isoformat() if inventory and inventory.issue_date else None,
        },
        "metrics": [map_metric(metric) for metric in metrics],
        "complaints": [
            {
                "ticket_id": complaint.ticket_id,
                "date": complaint.date.isoformat() if complaint.date else None,
                "complaint_text": complaint.complaint_text,
            }
            for complaint in complaints
        ],
    }

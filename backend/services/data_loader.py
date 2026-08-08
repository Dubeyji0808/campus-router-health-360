import csv
from copy import deepcopy
from pathlib import Path
from typing import Dict, List

from config import DATA_DIR


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="") as handle:
        return list(csv.DictReader(handle))


def load_router_rows() -> List[Dict[str, str]]:
    return _read_csv(DATA_DIR / "routers.csv")


def load_metrics_rows() -> List[Dict[str, str]]:
    return _read_csv(DATA_DIR / "metrics.csv")


def load_complaint_rows() -> List[Dict[str, str]]:
    return _read_csv(DATA_DIR / "complaints.csv")


def _coerce_metric(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "hour": int(row.get("hour", 0) or 0),
        "latency_ms": float(row.get("latency_ms", 0) or 0),
        "packet_loss_pct": float(row.get("packet_loss_pct", 0) or 0),
        "disconnects": int(row.get("disconnects", 0) or 0),
        "connected_devices": int(row.get("connected_devices", 0) or 0),
        "signal_dbm": int(row.get("signal_dbm", 0) or 0),
        "is_bad": str(row.get("is_bad", "false")).strip().lower() == "true",
    }


def _coerce_router(row: Dict[str, str]) -> Dict[str, object]:
    return {
        "router_id": row.get("router_id", ""),
        "building": row.get("building", ""),
        "room": row.get("room", ""),
        "model": row.get("model", ""),
        "firmware_version": row.get("firmware_version", ""),
        "user_type": row.get("user_type", ""),
        "health_score": int(row.get("health_score", 0) or 0),
        "bad_hours_count": int(row.get("bad_hours_count", 0) or 0),
    }


def get_concatenated_router_data() -> Dict[str, List[Dict[str, object]]]:
    # The project includes CSV files but they are intentionally empty in the scaffold.
    # This function keeps the loader resilient so the app can still render a valid
    # mock fallback while the real CSVs are being populated.
    routers = load_router_rows()
    metrics = load_metrics_rows()
    complaints = load_complaint_rows()

    if not routers and not metrics and not complaints:
        try:
            from mock_data import ROUTERS  # type: ignore
        except ImportError:  # pragma: no cover
            from backend.mock_data import ROUTERS  # type: ignore

        return {
            "routers": deepcopy(ROUTERS),
            "metrics": [],
            "complaints": [],
        }

    metric_index: Dict[str, List[Dict[str, object]]] = {}
    for metric in metrics:
        router_id = str(metric.get("router_id", "")).strip()
        if not router_id:
            continue
        metric_index.setdefault(router_id, []).append(_coerce_metric(metric))

    complaint_index: Dict[str, List[Dict[str, object]]] = {}
    for complaint in complaints:
        router_id = str(complaint.get("router_id", "")).strip()
        if not router_id:
            continue
        complaint_index.setdefault(router_id, []).append(
            {
                "ticket_id": complaint.get("ticket_id", ""),
                "date": complaint.get("date", ""),
                "complaint_text": complaint.get("complaint_text", ""),
            }
        )

    public_routers: List[Dict[str, object]] = []
    for router in routers:
        router_id = str(router.get("router_id", "")).strip()
        if not router_id:
            continue
        public_routers.append(
            {
                **_coerce_router(router),
                "breakdown": {
                    "latency": router.get("latency_breakdown", "healthy"),
                    "packet_loss": router.get("packet_loss_breakdown", "healthy"),
                    "signal": router.get("signal_breakdown", "healthy"),
                    "disconnects": router.get("disconnects_breakdown", "healthy"),
                },
                "metrics_timeseries": sorted(
                    metric_index.get(router_id, []),
                    key=lambda row: int(row.get("hour", 0)),
                ),
                "complaints": complaint_index.get(router_id, []),
            }
        )

    return {"routers": public_routers, "metrics": metrics, "complaints": complaints}

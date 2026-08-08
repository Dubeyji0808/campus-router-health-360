from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]
METRICS_DATETIME_FORMATS = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
MISSING_VALUES = {"", "na", "n/a", "none", "null", "nan"}


@dataclass
class RouterInventory:
    router_id: str
    model: str
    firmware_version: str
    building: str
    room: str
    user_type: str
    issue_date: Optional[date]


@dataclass
class RouterMetric:
    router_id: str
    hour: datetime
    avg_speed_mbps: float
    latency_ms: float
    packet_loss_pct: float
    disconnects: float
    connected_devices: int
    signal_dbm: float


@dataclass
class ComplaintTicket:
    ticket_id: str
    router_id: str
    date: Optional[date]
    complaint_text: str


def parse_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None

    raw = value.strip()
    if raw.lower() in MISSING_VALUES:
        return None

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None

    raw = value.strip()
    if raw.lower() in MISSING_VALUES:
        return None

    for fmt in METRICS_DATETIME_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    raw = value.strip()
    if raw.lower() in MISSING_VALUES:
        return None

    try:
        return int(float(raw))
    except ValueError:
        return None


def parse_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    raw = value.strip()
    if raw.lower() in MISSING_VALUES:
        return None

    try:
        return float(raw)
    except ValueError:
        return None


def _open_csv(path: Path):
    return path.open("r", encoding="utf-8", newline="")


def load_router_inventory(path: Path) -> Dict[str, RouterInventory]:
    path = path.resolve()
    result: Dict[str, RouterInventory] = {}

    with _open_csv(path) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            router_id = (row.get("router_id") or "").strip()
            if not router_id:
                continue

            inventory = RouterInventory(
                router_id=router_id,
                model=(row.get("model") or "").strip(),
                firmware_version=(row.get("firmware_version") or "").strip(),
                building=(row.get("building") or "").strip(),
                room=(row.get("room") or "").strip(),
                user_type=(row.get("user_type") or "").strip(),
                issue_date=parse_date(row.get("issue_date")),
            )
            result[router_id] = inventory

    return result


def load_router_metrics(path: Path) -> Dict[str, List[RouterMetric]]:
    path = path.resolve()
    result: Dict[str, List[RouterMetric]] = {}

    with _open_csv(path) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            router_id = (row.get("router_id") or "").strip()
            hour = parse_datetime(row.get("hour"))
            avg_speed = parse_float(row.get("avg_speed_mbps"))
            latency = parse_float(row.get("latency_ms"))
            packet_loss = parse_float(row.get("packet_loss_pct"))
            disconnects = parse_float(row.get("disconnects"))
            connected_devices = parse_int(row.get("connected_devices"))
            signal = parse_float(row.get("signal_dbm"))

            if not router_id or hour is None:
                continue
            if avg_speed is None or latency is None or packet_loss is None or disconnects is None or connected_devices is None or signal is None:
                continue

            metric = RouterMetric(
                router_id=router_id,
                hour=hour,
                avg_speed_mbps=avg_speed,
                latency_ms=latency,
                packet_loss_pct=packet_loss,
                disconnects=disconnects,
                connected_devices=connected_devices,
                signal_dbm=signal,
            )
            result.setdefault(router_id, []).append(metric)

    return result


def load_complaints(path: Path) -> Dict[str, List[ComplaintTicket]]:
    path = path.resolve()
    result: Dict[str, List[ComplaintTicket]] = {}

    with _open_csv(path) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            ticket_id = (row.get("ticket_id") or "").strip()
            router_id = (row.get("router_id") or "").strip()
            if not ticket_id or not router_id:
                continue

            complaint = ComplaintTicket(
                ticket_id=ticket_id,
                router_id=router_id,
                date=parse_date(row.get("date")),
                complaint_text=(row.get("complaint_text") or "").strip(),
            )
            result.setdefault(router_id, []).append(complaint)

    return result


def load_all_data(base_dir: Optional[Path] = None) -> tuple[Dict[str, RouterInventory], Dict[str, List[RouterMetric]], Dict[str, List[ComplaintTicket]]]:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[1] / "data"
    base_dir = base_dir.resolve()
    routers = load_router_inventory(base_dir / "routers.csv")
    metrics = load_router_metrics(base_dir / "metrics.csv")
    complaints = load_complaints(base_dir / "COMPLA_1.CSV")
    return routers, metrics, complaints

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

from services.data_loader import ComplaintTicket, RouterInventory, RouterMetric, load_all_data


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def normalize_signal(signal_dbm: float) -> float:
    return clamp((signal_dbm + 90) / 35, 0.0, 1.0)


def normalize_speed(speed_mbps: float) -> float:
    return clamp(speed_mbps / 75.0, 0.0, 1.0)


def normalize_latency(latency_ms: float) -> float:
    return clamp(1.0 - ((latency_ms - 35.0) / 80.0), 0.0, 1.0)


def normalize_packet_loss(packet_loss_pct: float) -> float:
    return clamp(1.0 - (packet_loss_pct / 3.5), 0.0, 1.0)


def normalize_disconnects(disconnects: float) -> float:
    return clamp(1.0 - (disconnects / 0.9), 0.0, 1.0)


@dataclass
class RouterHealthScore:
    router_id: str
    score: float
    label: str
    avg_speed_mbps: float
    avg_latency_ms: float
    avg_packet_loss_pct: float
    avg_disconnects: float
    avg_signal_dbm: float
    bad_hour_ratio: float
    complaint_count: int
    primary_issue: str


def compute_health_score(metrics: Sequence[RouterMetric], complaint_count: int) -> RouterHealthScore:
    if not metrics:
        return RouterHealthScore(
            router_id="",
            score=0.0,
            label="no data",
            avg_speed_mbps=0.0,
            avg_latency_ms=0.0,
            avg_packet_loss_pct=0.0,
            avg_disconnects=0.0,
            avg_signal_dbm=-90.0,
            bad_hour_ratio=1.0,
            complaint_count=complaint_count,
            primary_issue="no metrics",
        )

    speeds = [m.avg_speed_mbps for m in metrics]
    latencies = [m.latency_ms for m in metrics]
    losses = [m.packet_loss_pct for m in metrics]
    disconnects = [m.disconnects for m in metrics]
    signals = [m.signal_dbm for m in metrics]

    avg_speed = mean(speeds)
    avg_latency = mean(latencies)
    avg_loss = mean(losses)
    avg_disconnect = mean(disconnects)
    avg_signal = mean(signals)

    bad_hours = 0
    for metric in metrics:
        conditions = 0
        if metric.avg_speed_mbps < 35:
            conditions += 1
        if metric.latency_ms > 120:
            conditions += 1
        if metric.packet_loss_pct > 1.5:
            conditions += 1
        if metric.disconnects >= 1:
            conditions += 1
        if metric.signal_dbm < -72:
            conditions += 1
        if conditions >= 2:
            bad_hours += 1

    bad_hour_ratio = bad_hours / len(metrics)

    speed_score = normalize_speed(avg_speed)
    latency_score = normalize_latency(avg_latency)
    loss_score = normalize_packet_loss(avg_loss)
    disconnect_score = normalize_disconnects(avg_disconnect)
    signal_score = normalize_signal(avg_signal)

    base_score = (
        speed_score * 0.25
        + latency_score * 0.2
        + loss_score * 0.2
        + disconnect_score * 0.2
        + signal_score * 0.15
    ) * 100

    penalty = 0.0
    penalty += bad_hour_ratio * 100 * 0.35
    if base_score < 65 and complaint_count > 0:
        penalty += min(complaint_count * 1.5, 15.0)

    score = clamp(base_score - penalty, 0.0, 100.0)

    if bad_hour_ratio < 0.05 and score >= 70:
        label = "healthy"
    elif score >= 60:
        label = "ok"
    elif score >= 40:
        label = "warning"
    else:
        label = "poor"

    issues: List[Tuple[str, float]] = [
        ("speed", speed_score),
        ("latency", latency_score),
        ("packet_loss", loss_score),
        ("disconnects", disconnect_score),
        ("signal", signal_score),
    ]
    primary_issue = min(issues, key=lambda item: item[1])[0]

    return RouterHealthScore(
        router_id=metrics[0].router_id,
        score=round(score, 1),
        label=label,
        avg_speed_mbps=round(avg_speed, 1),
        avg_latency_ms=round(avg_latency, 1),
        avg_packet_loss_pct=round(avg_loss, 2),
        avg_disconnects=round(avg_disconnect, 2),
        avg_signal_dbm=round(avg_signal, 1),
        bad_hour_ratio=round(bad_hour_ratio, 3),
        complaint_count=complaint_count,
        primary_issue=primary_issue,
    )


def score_all_routers(
    inventories: Dict[str, RouterInventory],
    metrics_by_router: Dict[str, List[RouterMetric]],
    complaints_by_router: Dict[str, List[ComplaintTicket]],
) -> Dict[str, RouterHealthScore]:
    scores: Dict[str, RouterHealthScore] = {}
    router_ids = sorted(set(inventories) | set(metrics_by_router) | set(complaints_by_router))
    for router_id in router_ids:
        metrics = metrics_by_router.get(router_id, [])
        complaint_count = len(complaints_by_router.get(router_id, []))
        score = compute_health_score(metrics, complaint_count)
        score.router_id = router_id
        scores[router_id] = score
    return scores


def rank_routers(scores: Dict[str, RouterHealthScore]) -> List[RouterHealthScore]:
    return sorted(
        scores.values(),
        key=lambda item: (item.score, -item.bad_hour_ratio, -item.complaint_count),
    )


def worst_routers(scores: Dict[str, RouterHealthScore], top_n: int = 10) -> List[RouterHealthScore]:
    return rank_routers(scores)[:top_n]


def build_health_summary(base_dir: Optional[Path] = None) -> Dict[str, RouterHealthScore]:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[1] / "data"
    inventories, metrics_by_router, complaints_by_router = load_all_data(base_dir)
    return score_all_routers(inventories, metrics_by_router, complaints_by_router)


def print_worst_routers(scores: Dict[str, RouterHealthScore], top_n: int = 10) -> None:
    print(f"Worst {top_n} routers by health score:\n")
    for idx, item in enumerate(worst_routers(scores, top_n), start=1):
        print(
            f"{idx}. {item.router_id}: {item.score} ({item.label}) "
            f"speed={item.avg_speed_mbps}Mbps latency={item.avg_latency_ms}ms "
            f"loss={item.avg_packet_loss_pct}% disconnects={item.avg_disconnects} signal={item.avg_signal_dbm}dBm "
            f"complaints={item.complaint_count} bad_hours={item.bad_hour_ratio * 100:.1f}%"
        )


def print_router_ranking(scores: Dict[str, RouterHealthScore]) -> None:
    print("Router ranking from worst to best health score:\n")
    for idx, item in enumerate(rank_routers(scores), start=1):
        print(
            f"{idx}. {item.router_id}: {item.score} ({item.label}) "
            f"speed={item.avg_speed_mbps}Mbps latency={item.avg_latency_ms}ms "
            f"loss={item.avg_packet_loss_pct}% disconnects={item.avg_disconnects} signal={item.avg_signal_dbm}dBm "
            f"complaints={item.complaint_count} bad_hours={item.bad_hour_ratio * 100:.1f}%"
        )


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Compute router health scores from cleaned router, metrics, and complaint data.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--ranking", action="store_true", help="Print the full ranking from worst to best.")
    args = parser.parse_args()

    scores = build_health_summary(args.data_dir)
    if args.ranking:
        print_router_ranking(scores)
    else:
        print_worst_routers(scores, args.top_n)

from copy import deepcopy
from typing import Any, Dict, List, Optional

from services.data_loader import get_concatenated_router_data


def _fallback_routers() -> List[Dict[str, Any]]:
    try:
        from mock_data import ROUTERS  # type: ignore
    except ImportError:  # pragma: no cover
        from backend.mock_data import ROUTERS  # type: ignore

    return deepcopy(ROUTERS)


def get_all_rankings() -> List[Dict[str, Any]]:
    payload = get_concatenated_router_data().get("routers") or _fallback_routers()
    rankings = []
    for item in payload:
        rankings.append(
            {
                "router_id": item.get("router_id"),
                "health_score": item.get("health_score"),
                "building": item.get("building"),
                "bad_hours_count": item.get("bad_hours_count", 0),
                "firmware_version": item.get("firmware_version"),
            }
        )
    return sorted(rankings, key=lambda router: int(router["health_score"]))


def get_router_by_id(router_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not router_id:
        return None
    payload = get_concatenated_router_data().get("routers") or _fallback_routers()
    for item in payload:
        if item.get("router_id") == router_id:
            return item
    return None


def get_router_detail(router_id: str) -> Optional[Dict[str, Any]]:
    item = get_router_by_id(router_id)
    if item is None:
        return None
    return {
        "router_id": item["router_id"],
        "info": {
            "building": item.get("building"),
            "room": item.get("room"),
            "model": item.get("model"),
            "firmware_version": item.get("firmware_version"),
            "user_type": item.get("user_type"),
        },
        "health_score": item.get("health_score"),
        "breakdown": item.get("breakdown", {}),
        "metrics_timeseries": item.get("metrics_timeseries", []),
        "complaints": item.get("complaints", []),
    }

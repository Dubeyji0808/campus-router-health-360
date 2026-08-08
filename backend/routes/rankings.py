from typing import List

from fastapi import APIRouter

from services.health_score import build_health_summary, RouterHealthScore
from services.data_loader import load_all_data

router = APIRouter()


def map_score(score: RouterHealthScore) -> dict:
    return {
        "router_id": score.router_id,
        "score": score.score,
        "label": score.label,
        "building": None,
        "health_score": score.score,
        "bad_hours_percent": round(score.bad_hour_ratio * 100, 1),
        "complaints": score.complaint_count,
    }


@router.get("/rankings", response_model=List[dict])
def get_rankings():
    inventories, _, _ = load_all_data()
    scores = build_health_summary()
    ranked = sorted(scores.values(), key=lambda item: item.score)
    return [
        {
            "router_id": score.router_id,
            "score": score.score,
            "label": score.label,
            "building": inventories.get(score.router_id).building if inventories.get(score.router_id) else None,
            "bad_hours_percent": round(score.bad_hour_ratio * 100, 1),
            "complaints": score.complaint_count,
        }
        for score in ranked[:10]
    ]

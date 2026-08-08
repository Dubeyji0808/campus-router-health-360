from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.copilot_route import ask_copilot_route
from routes.rankings import get_rankings_route
from routes.router_detail import get_router_detail_route
from services.health_score import calculate_health_score

app = FastAPI(title=settings.APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/rankings")
def get_rankings():
    return get_rankings_route()


@app.get("/api/router/{router_id}")
def get_router(router_id: str):
    router = get_router_detail_route(router_id)
    if router is None:
        raise HTTPException(status_code=404, detail="Router not found")
    return router


@app.post("/api/copilot")
def ask_copilot(payload: dict):
    return ask_copilot_route(payload or {})


__all__ = ["app", "calculate_health_score", "settings"]

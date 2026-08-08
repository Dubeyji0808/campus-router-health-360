from fastapi import FastAPI

from routes import rankings, router_detail, copilot_route

app = FastAPI(title="Campus Router Health 360")

app.include_router(rankings.router, prefix="/api")
app.include_router(router_detail.router, prefix="/api")
app.include_router(copilot_route.router, prefix="/api")

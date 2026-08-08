from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RouterMetric(BaseModel):
    hour: int
    latency_ms: float
    packet_loss_pct: float
    disconnects: int
    connected_devices: int
    signal_dbm: int
    is_bad: bool = False


class Complaint(BaseModel):
    ticket_id: str
    date: str
    complaint_text: str


class RouterInfo(BaseModel):
    building: str
    room: str
    model: str
    firmware_version: str
    user_type: str


class RouterDetailResponse(BaseModel):
    router_id: str
    info: RouterInfo
    health_score: int
    breakdown: Dict[str, str]
    metrics_timeseries: List[RouterMetric]
    complaints: List[Complaint]


class CopilotRequest(BaseModel):
    question: str = Field(default="")
    router_id: Optional[str] = None


class CopilotResponse(BaseModel):
    router_id: str
    cause: str
    evidence: str
    recommended_fix: str

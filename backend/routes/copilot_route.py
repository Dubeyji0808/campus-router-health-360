from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.copilot import explain_router

router = APIRouter()


class CopilotRequest(BaseModel):
    router_id: str
    question: str


@router.post("/copilot")
def ask_copilot(request: CopilotRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = explain_router(request.router_id, question)
    return {
        "router_id": answer.router_id,
        "answer": answer.answer,
        "evidence": answer.evidence,
        "recommendation": answer.recommendation,
    }

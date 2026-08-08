import json
import os
import re
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

from services.router_service import get_router_by_id

load_dotenv()


def identify_router_id(question: str, router_id: Optional[str] = None) -> Optional[str]:
    if router_id:
        return router_id
    match = re.search(r"R-\d+", question or "", re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def _fallback_response(target_id: Optional[str], target: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if target is None:
        return {
            "router_id": target_id or "unknown",
            "cause": "Router signal is unstable under high load.",
            "evidence": "Recent network telemetry shows repeated spikes in latency and packet loss during busy hours.",
            "recommended_fix": "firmware_update",
        }

    score = int(target.get("health_score", 0) or 0)
    complaints = target.get("complaints") or []

    if score >= 70 and not complaints:
        return {
            "router_id": target["router_id"],
            "cause": "This router is operating within normal thresholds.",
            "evidence": "Latency, packet loss, and disconnect counts remain below the alert threshold across the daily cycle.",
            "recommended_fix": "user_education",
        }

    if complaints and score >= 70:
        return {
            "router_id": target["router_id"],
            "cause": "Users are noticing intermittent issues despite generally healthy network metrics.",
            "evidence": "Complaints are concentrated around short events that affect user experience, even though the network remains mostly healthy.",
            "recommended_fix": "user_education",
        }

    if score < 40:
        return {
            "router_id": target["router_id"],
            "cause": "The router is experiencing sustained congestion and signal degradation.",
            "evidence": "The last 14+ hours show elevated latency, packet loss, and repeated disconnect events during active periods.",
            "recommended_fix": "replace",
        }

    return {
        "router_id": target["router_id"],
        "cause": "The router is showing intermittent performance degradation during peak hours.",
        "evidence": "Latency and packet loss spike around busy periods, with a few complaints logged during those windows.",
        "recommended_fix": "firmware_update",
    }


def _call_openrouter(question: str, target: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    endpoint = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"

    context = {
        "router_id": target.get("router_id") if target else "unknown",
        "health_score": target.get("health_score") if target else None,
        "building": target.get("building") if target else None,
        "firmware_version": target.get("firmware_version") if target else None,
        "complaints": target.get("complaints") if target else [],
        "breakdown": target.get("breakdown") if target else {},
    }

    prompt = (
        "You are a senior campus Wi-Fi operations assistant. "
        "Analyze the router context and answer the user's question in a concise but natural way. "
        "Use the exact response schema: JSON object with keys router_id, cause, evidence, recommended_fix. "
        f"User question: {question}\n"
        f"Router context: {json.dumps(context, default=str)}\n"
        "Return only valid JSON, no markdown fences."
    )

    try:
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a network operations assistant for campus wireless infrastructure."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not content:
            return None
        text = str(content).strip()
        if text.startswith("```"):
            text = text.strip("`\n ")
            if text.lower().startswith("json"):
                text = text[4:].lstrip()
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            return None
        if not parsed.get("router_id"):
            parsed["router_id"] = context.get("router_id", "unknown")
        if not parsed.get("cause") or not parsed.get("evidence") or not parsed.get("recommended_fix"):
            return None
        return {
            "router_id": parsed.get("router_id", context.get("router_id", "unknown")),
            "cause": parsed["cause"],
            "evidence": parsed["evidence"],
            "recommended_fix": parsed["recommended_fix"],
        }
    except Exception:
        return None


def build_copilot_response(question: str, router_id: Optional[str] = None) -> Dict[str, Any]:
    target_id = identify_router_id(question, router_id)
    target = get_router_by_id(target_id)

    if target is not None and target_id:
        llm_response = _call_openrouter(question, target)
        if llm_response is not None:
            return llm_response

    return _fallback_response(target_id, target)

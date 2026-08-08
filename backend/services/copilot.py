from __future__ import annotations

import json
import urllib.error
import urllib.request

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from config import OPENROUTER_API_KEY
from .data_loader import ComplaintTicket, RouterInventory, RouterMetric, load_all_data
from .health_score import RouterHealthScore, build_health_summary


OPENROUTER_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class CopilotAnswer:
    router_id: str
    answer: str
    evidence: List[str]
    recommendation: str


def choose_recommendation(primary_issue: str, label: str) -> str:
    if label == "healthy":
        return "This router appears healthy; verify local device settings and educate the user about Wi-Fi coverage and interference."

    recommendations = {
        "speed": "Inspect the router backhaul and firmware, then replace or rebalance the affected uplink if sustained throughput is low.",
        "latency": "Check for congestion and noisy interference; update firmware and inspect the uplink path to reduce latency.",
        "packet_loss": "Investigate cabling and radio interference; replace the router or radio module if packet loss is persistent.",
        "disconnects": "Review the firmware and power state; schedule a replacement or reset for routers that disconnect repeatedly.",
        "signal": "Relocate the router or remove physical obstructions; ensure antennas and access points are positioned for consistent coverage.",
        "no data": "There is not enough data for this router; confirm the router is reporting metrics and retry.",
    }
    return recommendations.get(primary_issue, recommendations["latency"])


def build_evidence(
    inventory: Optional[RouterInventory],
    metrics: List[RouterMetric],
    complaints: List[ComplaintTicket],
    summary: RouterHealthScore,
) -> List[str]:
    evidence: List[str] = []
    if inventory:
        evidence.append(f"Router model {inventory.model} in {inventory.building} / {inventory.room} ({inventory.user_type}).")
    evidence.append(
        f"Average speed is {summary.avg_speed_mbps} Mbps, latency is {summary.avg_latency_ms} ms, packet loss is {summary.avg_packet_loss_pct}%, "
        f"disconnects are {summary.avg_disconnects} per hour and signal is {summary.avg_signal_dbm} dBm."
    )
    evidence.append(f"Health score is {summary.score} and {summary.bad_hour_ratio * 100:.1f}% of hours show sustained poor conditions.")

    if complaints:
        evidence.append(f"There are {len(complaints)} complaint tickets, including: {complaints[0].complaint_text}")

    return evidence


def _get_openrouter_api_key() -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is required to call the OpenRouter model.")
    return OPENROUTER_API_KEY


def _build_router_prompt(
    router_id: str,
    inventory: Optional[RouterInventory],
    summary: RouterHealthScore,
    evidence: List[str],
    complaints: List[ComplaintTicket],
    question: str,
) -> str:
    inventory_text = (
        f"Router {router_id} inventory: model={inventory.model}, firmware={inventory.firmware_version}, "
        f"building={inventory.building}, room={inventory.room}, user_type={inventory.user_type}."
        if inventory
        else f"Router {router_id} inventory is missing."
    )

    complaints_text = (
        "Complaints:\n" + "\n".join(f"- {c.ticket_id}: {c.complaint_text}" for c in complaints)
        if complaints
        else "No complaints reported."
    )

    prompt = (
        "You are a router health analyst. Answer the user question using only the data below. "
        "If the question is outside the scope of wifi, routers, or router health, reply exactly: 'Please ask me things regarding wifi.' "
        "Do not invent evidence. Cite exact metrics and complaint details when available. Provide one recommended fix if the question is about this router.\n\n"
        f"User question: {question}\n\n"
        f"Router: {router_id}\n"
        f"Summary: health_score={summary.score}, label={summary.label}, avg_speed_mbps={summary.avg_speed_mbps}, "
        f"avg_latency_ms={summary.avg_latency_ms}, avg_packet_loss_pct={summary.avg_packet_loss_pct}, "
        f"avg_disconnects={summary.avg_disconnects}, avg_signal_dbm={summary.avg_signal_dbm}, "
        f"bad_hour_ratio={summary.bad_hour_ratio:.3f}, complaint_count={summary.complaint_count}.\n\n"
        f"{inventory_text}\n\n"
        f"Evidence:\n"
        + "\n".join(f"- {item}" for item in evidence)
        + "\n\n"
        f"{complaints_text}\n\n"
        "Answer with a short, factual paragraph and then a single recommended fix when appropriate."
    )
    return prompt


def _fetch_openrouter_answer(prompt: str) -> str:
    api_key = _get_openrouter_api_key()
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise technical assistant for router health diagnostics."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 450,
        "reasoning": {"enabled": True},
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenRouter request failed: {exc.code} {exc.reason}. Body: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc.reason}") from exc

    content = response_data.get("choices", [{}])[0].get("message", {}).get("content")
    if not content:
        raise RuntimeError(f"OpenRouter response missing content: {response_data}")
    return content.strip()


def build_router_answer(
    router_id: str,
    inventories: Dict[str, RouterInventory],
    metrics_by_router: Dict[str, List[RouterMetric]],
    complaints_by_router: Dict[str, List[ComplaintTicket]],
    scores: Dict[str, RouterHealthScore],
    question: str,
) -> CopilotAnswer:
    router_summary = scores.get(router_id)
    if router_summary is None:
        return CopilotAnswer(
            router_id=router_id,
            answer=f"Router {router_id} is not present in the cleaned data.",
            evidence=[],
            recommendation="Confirm the router ID and try again.",
        )

    inventory = inventories.get(router_id)
    metrics = metrics_by_router.get(router_id, [])
    complaints = complaints_by_router.get(router_id, [])
    evidence = build_evidence(inventory, metrics, complaints, router_summary)
    recommendation = choose_recommendation(router_summary.primary_issue, router_summary.label)
    prompt = _build_router_prompt(router_id, inventory, router_summary, evidence, complaints, question)

    try:
        answer_text = _fetch_openrouter_answer(prompt)
    except Exception as exc:
        answer_text = (
            f"Model request failed; falling back to deterministic explanation. Error: {exc}. "
            f"Router {router_id} has score {router_summary.score} and primary issue {router_summary.primary_issue}."
        )

    return CopilotAnswer(
        router_id=router_id,
        answer=answer_text,
        evidence=evidence,
        recommendation=recommendation,
    )


def explain_router(router_id: str, question: str, base_dir: Optional[Path] = None) -> CopilotAnswer:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[1] / "data"

    inventories, metrics_by_router, complaints_by_router = load_all_data(base_dir)
    scores = build_health_summary(base_dir)
    return build_router_answer(router_id, inventories, metrics_by_router, complaints_by_router, scores, question)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Create an evidence-based router health explanation for a given router ID.")
    parser.add_argument("router_id", help="Router identifier to explain, for example R-1042.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = parser.parse_args()

    answer = explain_router(args.router_id, args.data_dir)
    print(answer.answer)
    print("\nEvidence:")
    for item in answer.evidence:
        print(f"- {item}")
    print(f"\nRecommended fix: {answer.recommendation}")

from services.copilot import build_copilot_response


def ask_copilot_route(payload: dict):
    question = str((payload or {}).get("question", ""))
    router_id = (payload or {}).get("router_id")
    return build_copilot_response(question, router_id)

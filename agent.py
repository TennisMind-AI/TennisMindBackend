from typing import Any, Dict, List

import memory


def process_event(user_id: str, event: Any) -> Dict[str, Any]:
    logs: List[str] = []

    logs.append("Agent received input")
    logs.append("Retrieving memory from Redis")

    memory.get_last_event(user_id)
    memory.get_last_decision(user_id)

    pattern = _detect_pattern(event)
    logs.append(f"Pattern detected: {pattern}")

    existing_pattern = memory.get_pattern(user_id, pattern)
    if existing_pattern:
        decision = "Recurring issue detected"
        logs.append(f"Existing pattern found in Redis: {pattern}")
    else:
        decision = "New issue detected"
        logs.append(f"No existing pattern found in Redis: {pattern}")

    logs.append("Updating memory with pattern learning and history")
    memory.save_last_event(user_id, event)
    memory.save_pattern(user_id, pattern, {})
    memory.save_decision(user_id, decision)
    memory.append_history(user_id, event, decision)

    logs.append("Decision complete")

    return {
        "decision": decision,
        "voice_text": _voice_text(pattern, decision),
        "logs": logs,
    }


def _detect_pattern(event: Any) -> str:
    if _event_value(event) > 80:
        return "serve_too_wide"
    return "normal"


def _event_value(event: Any) -> float:
    if isinstance(event, dict):
        return float(event.get("value", 0))
    if isinstance(event, (int, float)):
        return float(event)
    return 0.0


def _voice_text(pattern: str, decision: str) -> str:
    if pattern == "serve_too_wide":
        if decision == "Recurring issue detected":
            return "Your serve is still going too wide. Keep your toss slightly more controlled."
        return "Your serve is going too wide. Try adjusting your angle slightly."
    return "Your pattern looks normal. Keep your rhythm steady."

import json
import os
import time
from typing import Any, List, Optional


redis_client = None
INTERVAL_BY_COUNT = {
    1: 1,
    2: 3,
    3: 7,
}


def save_last_event(user_id: str, event: Any) -> None:
    _set_json(_last_event_key(user_id), event)


def get_last_event(user_id: str) -> Optional[Any]:
    return _get_json(_last_event_key(user_id))


def save_decision(user_id: str, decision: Any) -> None:
    _set_json(_last_decision_key(user_id), decision)


def get_last_decision(user_id: str) -> Optional[Any]:
    return _get_json(_last_decision_key(user_id))


def append_history(user_id: str, event: Any, decision: Any) -> None:
    key = _history_key(user_id)
    history = get_history(user_id)
    history.append(
        {
            "event": event,
            "decision": decision,
        }
    )
    _set_json(key, history)


def get_history(user_id: str) -> List[Any]:
    return _get_json(_history_key(user_id)) or []


def get_pattern(user_id: str, pattern: str) -> Optional[Any]:
    return _get_json(_pattern_key(user_id, pattern))


def save_pattern(user_id: str, pattern: str, data: Any) -> None:
    existing = get_pattern(user_id, pattern)
    history_count = 1
    strength = 0.3

    if existing:
        history_count = int(existing["history_count"]) + 1
        strength = min(1.0, float(existing.get("strength", strength)) + 0.1)

    review_interval = INTERVAL_BY_COUNT.get(history_count, 14)
    pattern_data = dict(data or {})
    pattern_data.update(
        {
            "pattern": pattern,
            "history_count": history_count,
            "review_interval": review_interval,
            "next_review": time.time() + (review_interval * 24 * 60 * 60),
            "strength": strength,
        }
    )

    _set_json(_pattern_key(user_id, pattern), pattern_data)


def _get_client():
    global redis_client

    if redis_client is None:
        import redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.Redis.from_url(redis_url)

    return redis_client


def _set_json(key: str, value: Any) -> None:
    _get_client().set(key, json.dumps(value))


def _get_json(key: str) -> Optional[Any]:
    raw_value = _get_client().get(key)
    if raw_value is None:
        return None
    if isinstance(raw_value, bytes):
        raw_value = raw_value.decode("utf-8")
    return json.loads(raw_value)


def _last_event_key(user_id: str) -> str:
    return f"agent:memory:last_event:{user_id}"


def _last_decision_key(user_id: str) -> str:
    return f"agent:memory:last_decision:{user_id}"


def _history_key(user_id: str) -> str:
    return f"agent:memory:history:{user_id}"


def _pattern_key(user_id: str, pattern: str) -> str:
    return f"agent:memory:pattern:{user_id}:{pattern}"

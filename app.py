from typing import Any, Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

import agent
import memory


app = FastAPI()
logs: List[str] = []
USER_ID = "default_user"


class TriggerPayload(BaseModel):
    value: float
    context: str


class TriggerRequest(BaseModel):
    event_id: str
    timestamp: str
    type: str
    payload: TriggerPayload


@app.post("/trigger")
def trigger(request: TriggerRequest) -> Dict[str, str]:
    event = {
        "event_id": request.event_id,
        "timestamp": request.timestamp,
        "type": request.type,
        "value": request.payload.value,
        "context": request.payload.context,
    }
    result = agent.process_event(USER_ID, event)
    logs.extend(result["logs"])

    return {
        "status": "ok",
        "decision": result["decision"],
        "voice_text": result["voice_text"],
    }


@app.get("/logs")
def get_logs() -> List[str]:
    return logs


@app.get("/state")
def get_state() -> Dict[str, Any]:
    history = memory.get_history(USER_ID)
    return {
        "last_event": memory.get_last_event(USER_ID),
        "last_decision": memory.get_last_decision(USER_ID),
        "history_count": len(history),
    }

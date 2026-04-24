from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import agent
import memory


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logs_by_user: Dict[str, List[str]] = {}


class TriggerPayload(BaseModel):
    value: float
    context: str


class TriggerRequest(BaseModel):
    user_id: str
    event_id: str
    timestamp: str
    type: str
    payload: TriggerPayload


@app.post("/trigger")
def trigger(request: TriggerRequest) -> Dict[str, str]:
    event = {
        "user_id": request.user_id,
        "event_id": request.event_id,
        "timestamp": request.timestamp,
        "type": request.type,
        "value": request.payload.value,
        "context": request.payload.context,
    }
    result = agent.process_event(request.user_id, event)
    logs_by_user.setdefault(request.user_id, []).extend(result["logs"])

    return {
        "status": "ok",
        "decision": result["decision"],
        "voice_text": result["voice_text"],
    }


@app.get("/logs")
def get_logs(user_id: str) -> List[str]:
    return logs_by_user.get(user_id, [])


@app.get("/state")
def get_state(user_id: str) -> Dict[str, Any]:
    history = memory.get_history(user_id)
    return {
        "last_event": memory.get_last_event(user_id),
        "last_decision": memory.get_last_decision(user_id),
        "history_count": len(history),
    }

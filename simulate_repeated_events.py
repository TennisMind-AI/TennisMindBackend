import json
import time

import agent
import memory


USER_ID = f"repeat_demo_{int(time.time())}"
PATTERN = "serve_too_wide"


def main() -> None:
    events = [
        {"event_id": "evt-1", "timestamp": "2026-04-24T12:00:00Z", "type": "serve", "value": 91, "context": "serve practice"},
        {"event_id": "evt-2", "timestamp": "2026-04-24T12:01:00Z", "type": "serve", "value": 92, "context": "serve practice"},
        {"event_id": "evt-3", "timestamp": "2026-04-24T12:02:00Z", "type": "serve", "value": 93, "context": "serve practice"},
    ]

    for index, event in enumerate(events, start=1):
        result = agent.process_event(USER_ID, event)
        pattern_memory = memory.get_pattern(USER_ID, PATTERN)

        print(f"Event {index}")
        print(f"decision: {result['decision']}")
        print("pattern_memory:")
        print(json.dumps(pattern_memory, indent=2))
        print()


if __name__ == "__main__":
    main()

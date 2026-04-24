# TennisMindBackend

Minimal Redis memory module for a tennis coaching AI.

## Install

```bash
pip install -r requirements.txt
```

## Redis Config

Redis connection settings live in `config.json`:

```json
{
  "redis": {
    "host": "redis-11081.c60.us-west-1-2.ec2.cloud.redislabs.com",
    "port": 11081,
    "decode_responses": true,
    "username": "default",
    "password": "your-password"
  }
}
```

To use another config file:

```bash
set REDIS_CONFIG_PATH=path\to\config.json
```

## Memory Keys

- `agent:memory:last_event:{user_id}`
- `agent:memory:last_decision:{user_id}`
- `agent:memory:history:{user_id}`
- `agent:memory:pattern:{user_id}:{pattern}`

All values are stored as JSON strings.

## Run API

```bash
uvicorn app:app --reload
```

Trigger the agent:

```bash
curl -X POST http://127.0.0.1:8000/trigger ^
  -H "Content-Type: application/json" ^
  -d "{\"event_id\":\"evt-1\",\"timestamp\":\"2026-04-24T12:00:00Z\",\"type\":\"serve\",\"payload\":{\"value\":91,\"context\":\"serve practice\"}}"
```

Check logs:

```bash
curl http://127.0.0.1:8000/logs
```

Check state:

```bash
curl http://127.0.0.1:8000/state
```

## Run Repeated Event Demo

This simulates three repeated serve events with `value > 80`.

Expected behavior:

- First event: `New issue detected`, interval `1`
- Second event: `Recurring issue detected`, interval `3`
- Third event: `Recurring issue detected`, interval `7`

Run:

```bash
python simulate_repeated_events.py
```

The script prints:

- `decision`
- pattern memory from Redis

## Test

```bash
python -m unittest -v
```

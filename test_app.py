import unittest

import app
import memory


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value


class AppTest(unittest.TestCase):
    def setUp(self):
        memory.redis_client = FakeRedis()
        app.logs.clear()

    def tearDown(self):
        memory.redis_client = None
        app.logs.clear()

    def test_trigger_returns_decision_and_updates_state(self):
        request = app.TriggerRequest(
            event_id="evt-1",
            timestamp="2026-04-24T12:00:00Z",
            type="serve",
            payload=app.TriggerPayload(value=91, context="serve practice"),
        )

        response = app.trigger(request)
        state = app.get_state()

        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["decision"], "New issue detected")
        self.assertEqual(state["history_count"], 1)
        self.assertEqual(state["last_decision"], "New issue detected")
        self.assertEqual(state["last_event"]["value"], 91)

    def test_logs_returns_human_readable_entries(self):
        request = app.TriggerRequest(
            event_id="evt-1",
            timestamp="2026-04-24T12:00:00Z",
            type="serve",
            payload=app.TriggerPayload(value=70, context="rally"),
        )

        app.trigger(request)

        self.assertIn("Agent received input", app.get_logs())
        self.assertIn("Retrieving memory from Redis", app.get_logs())


if __name__ == "__main__":
    unittest.main()

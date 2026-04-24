import unittest

import agent
import memory


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value


class AgentTest(unittest.TestCase):
    def setUp(self):
        memory.redis_client = FakeRedis()

    def tearDown(self):
        memory.redis_client = None

    def test_process_event_detects_new_issue_and_updates_memory(self):
        result = agent.process_event("player-1", {"value": 91})

        self.assertEqual(result["decision"], "New issue detected")
        self.assertEqual(
            result["voice_text"],
            "Your serve is going too wide. Try adjusting your angle slightly.",
        )
        self.assertEqual(memory.get_pattern("player-1", "serve_too_wide")["history_count"], 1)
        self.assertEqual(len(memory.get_history("player-1")), 1)
        self.assertIn("Agent received input", result["logs"])
        self.assertIn("Retrieving memory from Redis", result["logs"])

    def test_process_event_detects_recurring_issue(self):
        agent.process_event("player-1", {"value": 91})
        result = agent.process_event("player-1", {"value": 95})

        self.assertEqual(result["decision"], "Recurring issue detected")
        self.assertEqual(memory.get_pattern("player-1", "serve_too_wide")["history_count"], 2)
        self.assertEqual(len(memory.get_history("player-1")), 2)

    def test_process_event_detects_normal_pattern(self):
        result = agent.process_event("player-1", {"value": 70})

        self.assertEqual(result["decision"], "New issue detected")
        self.assertEqual(
            result["voice_text"],
            "Your pattern looks normal. Keep your rhythm steady.",
        )
        self.assertEqual(memory.get_pattern("player-1", "normal")["history_count"], 1)


if __name__ == "__main__":
    unittest.main()

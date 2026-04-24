import unittest

import memory


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value


class MemoryTest(unittest.TestCase):
    def setUp(self):
        memory.redis_client = FakeRedis()

    def tearDown(self):
        memory.redis_client = None

    def test_save_get_works(self):
        memory.save_last_event("player-1", {"shot": "serve", "result": "wide"})
        memory.save_decision("player-1", {"message": "adjust serve angle"})

        self.assertEqual(
            memory.get_last_event("player-1"),
            {"shot": "serve", "result": "wide"},
        )
        self.assertEqual(
            memory.get_last_decision("player-1"),
            {"message": "adjust serve angle"},
        )

    def test_history_append_works(self):
        memory.append_history("player-1", "serve wide", "adjust angle")
        memory.append_history("player-1", "late backhand", "prepare earlier")

        self.assertEqual(
            memory.get_history("player-1"),
            [
                {"event": "serve wide", "decision": "adjust angle"},
                {"event": "late backhand", "decision": "prepare earlier"},
            ],
        )

    def test_pattern_interval_increases_on_repeat(self):
        memory.save_pattern("player-1", "serve_wide", {})
        self.assertEqual(memory.get_pattern("player-1", "serve_wide")["review_interval"], 1)

        memory.save_pattern("player-1", "serve_wide", {})
        self.assertEqual(memory.get_pattern("player-1", "serve_wide")["review_interval"], 3)

        memory.save_pattern("player-1", "serve_wide", {})
        pattern = memory.get_pattern("player-1", "serve_wide")

        self.assertEqual(pattern["history_count"], 3)
        self.assertEqual(pattern["review_interval"], 7)


if __name__ == "__main__":
    unittest.main()

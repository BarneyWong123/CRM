import unittest
import os
import json
from state_manager import StateManager

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_processed_messages.json'
        # Ensure file doesn't exist
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_init_creates_empty_set_if_no_file(self):
        sm = StateManager(self.test_file)
        self.assertEqual(sm.processed_ids, set())

    def test_save_and_load(self):
        sm = StateManager(self.test_file)
        sm.mark_processed('123')

        # Verify it's in memory
        self.assertTrue(sm.is_processed('123'))

        # Verify it's on disk
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertIn('123', data)

        # Verify loading from disk
        sm2 = StateManager(self.test_file)
        self.assertTrue(sm2.is_processed('123'))
        self.assertFalse(sm2.is_processed('456'))

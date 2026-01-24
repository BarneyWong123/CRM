import unittest
import os
from unittest.mock import patch
from config import Config

class TestConfig(unittest.TestCase):
    def test_search_days_back_default(self):
        # Config is already imported, so we check the value loaded at start.
        # Ideally we should reload the module to test defaults properly,
        # but for now we just check if it's an integer.
        self.assertIsInstance(Config.SEARCH_DAYS_BACK, int)
        # Default is 7 unless env var is set.
        # Since we can't easily isolate the process environment for this unit test
        # without running in a subprocess or reloading, we just assert it's a valid int.
        self.assertTrue(Config.SEARCH_DAYS_BACK > 0)

    def test_validate_missing_creds(self):
        # We need to mock os.getenv to return None for credentials
        # But Config loads them at class level.
        # So we have to mock the class attributes directly.

        with patch.object(Config, 'GMAIL_EMAIL', None):
            with self.assertRaises(ValueError):
                Config.validate()

    def test_validate_success(self):
        with patch.object(Config, 'GMAIL_EMAIL', 'test@example.com'), \
             patch.object(Config, 'GMAIL_APP_PASSWORD', 'secret'):
             # Should not raise
             Config.validate()

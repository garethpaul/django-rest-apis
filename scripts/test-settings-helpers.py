#!/usr/bin/env python3
import importlib.util
import os
import pathlib
import sys
import types
import unittest


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT_DIR / "app" / "settings.py"


class ImproperlyConfigured(Exception):
    pass


def install_django_stub():
    django = types.ModuleType("django")
    core = types.ModuleType("django.core")
    exceptions = types.ModuleType("django.core.exceptions")
    exceptions.ImproperlyConfigured = ImproperlyConfigured
    core.exceptions = exceptions
    django.core = core
    sys.modules["django"] = django
    sys.modules["django.core"] = core
    sys.modules["django.core.exceptions"] = exceptions


def load_settings(env):
    install_django_stub()
    original_env = os.environ.copy()
    module_name = "settings_under_test_{0}".format(abs(hash(tuple(sorted(env.items())))))

    try:
        os.environ.clear()
        os.environ.update(env)
        spec = importlib.util.spec_from_file_location(module_name, SETTINGS_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        os.environ.clear()
        os.environ.update(original_env)


class SettingsHelperTests(unittest.TestCase):
    def test_production_requires_secret_key(self):
        with self.assertRaises(ImproperlyConfigured):
            load_settings({"DJANGO_DEBUG": "0"})

    def test_debug_mode_requires_secret_key(self):
        with self.assertRaises(ImproperlyConfigured):
            load_settings({"DJANGO_DEBUG": "1"})

    def test_debug_mode_uses_configured_secret_key(self):
        settings = load_settings({
            "DJANGO_DEBUG": "1",
            "DJANGO_SECRET_KEY": "debug-secret",
        })

        self.assertTrue(settings.DEBUG)
        self.assertEqual(settings.TEMPLATE_DEBUG, settings.DEBUG)
        self.assertEqual(settings.SECRET_KEY, "debug-secret")

    def test_secret_key_and_allowed_hosts_are_environment_driven(self):
        settings = load_settings({
            "DJANGO_SECRET_KEY": "test-secret",
            "DJANGO_ALLOWED_HOSTS": "example.com, api.example.com",
        })

        self.assertFalse(settings.DEBUG)
        self.assertEqual(settings.SECRET_KEY, "test-secret")
        self.assertEqual(settings.ALLOWED_HOSTS, ["example.com", "api.example.com"])

    def test_env_bool_parses_expected_truthy_values(self):
        settings = load_settings({
            "DJANGO_DEBUG": "1",
            "DJANGO_SECRET_KEY": "test-secret",
        })
        original_env = os.environ.copy()
        try:
            for value in ("1", "true", "yes", "on"):
                os.environ["FEATURE_FLAG"] = value
                self.assertTrue(settings.env_bool("FEATURE_FLAG"))
            os.environ["FEATURE_FLAG"] = "0"
            self.assertFalse(settings.env_bool("FEATURE_FLAG"))
        finally:
            os.environ.clear()
            os.environ.update(original_env)

    def test_twitter_credentials_are_environment_driven(self):
        settings = load_settings({
            "DJANGO_SECRET_KEY": "test-secret",
            "SOCIAL_AUTH_TWITTER_KEY": "consumer-key",
            "SOCIAL_AUTH_TWITTER_SECRET": "consumer-secret",
            "TWITTER_ACCESS_TOKEN": "access-token",
            "TWITTER_ACCESS_TOKEN_SECRET": "access-token-secret",
        })

        self.assertEqual(settings.SOCIAL_AUTH_TWITTER_KEY, "consumer-key")
        self.assertEqual(settings.SOCIAL_AUTH_TWITTER_SECRET, "consumer-secret")
        self.assertEqual(settings.TWITTER_ACCESS_TOKEN, "access-token")
        self.assertEqual(settings.TWITTER_ACCESS_TOKEN_SECRET, "access-token-secret")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
import importlib.util
import pathlib
import sys
import types
import unittest


ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
VIEWS_PATH = ROOT_DIR / "home" / "views.py"


class ImproperlyConfigured(Exception):
    pass


def identity_decorator(function=None, **_kwargs):
    if function is None:
        return lambda wrapped: wrapped
    return function


def install_stubs():
    django = types.ModuleType("django")
    shortcuts = types.ModuleType("django.shortcuts")
    shortcuts.render_to_response = lambda *args, **kwargs: (args, kwargs)
    shortcuts.RequestContext = lambda request: request
    shortcuts.HttpResponseRedirect = lambda target: target

    contrib = types.ModuleType("django.contrib")
    auth = types.ModuleType("django.contrib.auth")
    decorators = types.ModuleType("django.contrib.auth.decorators")
    decorators.login_required = identity_decorator
    decorators.user_passes_test = identity_decorator
    auth.decorators = decorators
    auth.logout = lambda request: None
    contrib.auth = auth

    views_module = types.ModuleType("django.views")
    http_decorators = types.ModuleType("django.views.decorators.http")
    http_decorators.require_POST = identity_decorator
    views_decorators = types.ModuleType("django.views.decorators")
    views_decorators.http = http_decorators
    views_module.decorators = views_decorators

    conf = types.ModuleType("django.conf")
    conf.settings = types.SimpleNamespace(
        SOCIAL_AUTH_TWITTER_KEY="consumer-key",
        SOCIAL_AUTH_TWITTER_SECRET="consumer-secret",
        TWITTER_ACCESS_TOKEN="access-token",
        TWITTER_ACCESS_TOKEN_SECRET="access-token-secret",
    )

    core = types.ModuleType("django.core")
    exceptions = types.ModuleType("django.core.exceptions")
    exceptions.ImproperlyConfigured = ImproperlyConfigured
    core.exceptions = exceptions

    social = types.ModuleType("social")
    social_apps = types.ModuleType("social.apps")
    social_django = types.ModuleType("social.apps.django_app")
    social_default = types.ModuleType("social.apps.django_app.default")
    social_models = types.ModuleType("social.apps.django_app.default.models")
    social_models.UserSocialAuth = object
    social_default.models = social_models
    social_django.default = social_default
    social_apps.django_app = social_django
    social.apps = social_apps

    twitter = types.ModuleType("twitter")
    twitter.TwitterError = type("TwitterError", (Exception,), {})
    twitter.Api = object

    modules = {
        "django": django,
        "django.shortcuts": shortcuts,
        "django.contrib": contrib,
        "django.contrib.auth": auth,
        "django.contrib.auth.decorators": decorators,
        "django.views": views_module,
        "django.views.decorators": views_decorators,
        "django.views.decorators.http": http_decorators,
        "django.conf": conf,
        "django.core": core,
        "django.core.exceptions": exceptions,
        "social": social,
        "social.apps": social_apps,
        "social.apps.django_app": social_django,
        "social.apps.django_app.default": social_default,
        "social.apps.django_app.default.models": social_models,
        "twitter": twitter,
    }
    sys.modules.update(modules)


def load_views_module():
    install_stubs()
    module_name = "views_under_test"
    spec = importlib.util.spec_from_file_location(module_name, VIEWS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


views = load_views_module()


class ViewHelperTests(unittest.TestCase):
    def test_normalize_status_strips_text(self):
        self.assertEqual(views.normalize_status("  hello twitter  "), "hello twitter")

    def test_normalize_status_ignores_empty_text(self):
        self.assertIsNone(views.normalize_status(None))
        self.assertIsNone(views.normalize_status(""))
        self.assertIsNone(views.normalize_status("   "))

    def test_normalize_status_ignores_overlong_text(self):
        self.assertIsNone(views.normalize_status("x" * 281))

    def test_load_twitter_home_preserves_timeline_when_post_fails(self):
        class FakeApi:
            def PostUpdates(self, status):
                self.status = status
                raise views.twitter.TwitterError("provider detail")

            def GetUserTimeline(self, screen_name, count):
                self.screen_name = screen_name
                self.count = count
                return ["existing status"]

        api = FakeApi()
        statuses, error = views.load_twitter_home(api, "sample-user", "hello")

        self.assertEqual(statuses, ["existing status"])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertEqual(api.status, "hello")
        self.assertEqual(api.screen_name, "sample-user")
        self.assertEqual(api.count, 10)

    def test_load_twitter_home_returns_stable_error_when_timeline_fails(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                raise views.twitter.TwitterError("provider detail")

        statuses, error = views.load_twitter_home(FakeApi(), "sample-user", None)

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertNotIn("provider detail", error)

    def test_get_twitter_uses_environment_tokens_when_social_token_is_missing(self):
        captured = {}

        class FakeManager:
            def get(self, user, provider):
                self.user = user
                self.provider = provider
                return types.SimpleNamespace(extra_data={})

        def fake_api(**kwargs):
            captured.update(kwargs)
            return captured

        original_user_social_auth = views.UserSocialAuth
        original_api = views.twitter.Api

        try:
            views.UserSocialAuth = types.SimpleNamespace(objects=FakeManager())
            views.twitter.Api = fake_api

            user = types.SimpleNamespace(username="sample-user")
            api = views.get_twitter(user)

            self.assertIs(api, captured)
            self.assertEqual(captured["access_token_key"], "access-token")
            self.assertEqual(captured["access_token_secret"], "access-token-secret")
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.twitter.Api = original_api

    def test_get_twitter_uses_environment_tokens_when_social_auth_is_missing(self):
        captured = {}

        class FakeUserSocialAuth:
            class DoesNotExist(Exception):
                pass

            class objects:
                @staticmethod
                def get(user, provider):
                    raise FakeUserSocialAuth.DoesNotExist()

        def fake_api(**kwargs):
            captured.update(kwargs)
            return captured

        original_user_social_auth = views.UserSocialAuth
        original_api = views.twitter.Api

        try:
            views.UserSocialAuth = FakeUserSocialAuth
            views.twitter.Api = fake_api

            user = types.SimpleNamespace(username="sample-user")
            api = views.get_twitter(user)

            self.assertIs(api, captured)
            self.assertEqual(captured["access_token_key"], "access-token")
            self.assertEqual(captured["access_token_secret"], "access-token-secret")
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.twitter.Api = original_api

    def test_get_twitter_uses_environment_tokens_when_social_token_is_blank(self):
        captured = {}

        class FakeManager:
            def get(self, user, provider):
                self.user = user
                self.provider = provider
                return types.SimpleNamespace(extra_data={
                    "access_token": {
                        "oauth_token": "   ",
                        "oauth_token_secret": "",
                    }
                })

        def fake_api(**kwargs):
            captured.update(kwargs)
            return captured

        original_user_social_auth = views.UserSocialAuth
        original_api = views.twitter.Api

        try:
            views.UserSocialAuth = types.SimpleNamespace(objects=FakeManager())
            views.twitter.Api = fake_api

            user = types.SimpleNamespace(username="sample-user")
            api = views.get_twitter(user)

            self.assertIs(api, captured)
            self.assertEqual(captured["access_token_key"], "access-token")
            self.assertEqual(captured["access_token_secret"], "access-token-secret")
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.twitter.Api = original_api

    def test_get_twitter_uses_environment_tokens_when_social_token_is_malformed(self):
        captured = {}

        class FakeManager:
            def get(self, user, provider):
                self.user = user
                self.provider = provider
                return types.SimpleNamespace(extra_data={
                    "access_token": {
                        "oauth_token": 123,
                        "oauth_token_secret": object(),
                    }
                })

        def fake_api(**kwargs):
            captured.update(kwargs)
            return captured

        original_user_social_auth = views.UserSocialAuth
        original_api = views.twitter.Api

        try:
            views.UserSocialAuth = types.SimpleNamespace(objects=FakeManager())
            views.twitter.Api = fake_api

            user = types.SimpleNamespace(username="sample-user")
            api = views.get_twitter(user)

            self.assertIs(api, captured)
            self.assertEqual(captured["access_token_key"], "access-token")
            self.assertEqual(captured["access_token_secret"], "access-token-secret")
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.twitter.Api = original_api

    def test_get_twitter_raises_configuration_error_when_access_tokens_are_missing(self):
        class FakeUserSocialAuth:
            class DoesNotExist(Exception):
                pass

            class objects:
                @staticmethod
                def get(user, provider):
                    raise FakeUserSocialAuth.DoesNotExist()

        original_user_social_auth = views.UserSocialAuth
        original_access_token = views.settings.TWITTER_ACCESS_TOKEN
        original_access_token_secret = views.settings.TWITTER_ACCESS_TOKEN_SECRET

        try:
            views.UserSocialAuth = FakeUserSocialAuth
            views.settings.TWITTER_ACCESS_TOKEN = " "
            views.settings.TWITTER_ACCESS_TOKEN_SECRET = ""

            user = types.SimpleNamespace(username="sample-user")
            with self.assertRaises(ImproperlyConfigured):
                views.get_twitter(user)
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.settings.TWITTER_ACCESS_TOKEN = original_access_token
            views.settings.TWITTER_ACCESS_TOKEN_SECRET = original_access_token_secret


if __name__ == "__main__":
    unittest.main()

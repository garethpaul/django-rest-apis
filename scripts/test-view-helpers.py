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


def make_status(status_id=42, text="existing status", screen_name="sample_user"):
    return types.SimpleNamespace(
        id=status_id,
        text=text,
        user=types.SimpleNamespace(screen_name=screen_name),
    )


class RaisingStatus:
    @property
    def id(self):
        raise RuntimeError("status accessor detail")


class RaisingUser:
    @property
    def screen_name(self):
        raise RuntimeError("user accessor detail")


class ViewHelperTests(unittest.TestCase):
    def test_normalize_status_strips_text(self):
        self.assertEqual(views.normalize_status("  hello twitter  "), "hello twitter")

    def test_normalize_status_ignores_empty_text(self):
        self.assertIsNone(views.normalize_status(None))
        self.assertIsNone(views.normalize_status(""))
        self.assertIsNone(views.normalize_status("   "))

    def test_normalize_status_ignores_overlong_text(self):
        self.assertIsNone(views.normalize_status("x" * 281))

    def test_normalize_status_ignores_non_string_values(self):
        for status in (123, True, [], {}, object()):
            self.assertIsNone(views.normalize_status(status))

    def test_normalize_status_rejects_lone_surrogates(self):
        for status in (u"high \ud800", u"low \udfff"):
            with self.subTest(status=repr(status)):
                self.assertIsNone(views.normalize_status(status))

    def test_normalize_status_preserves_valid_supplementary_text(self):
        self.assertEqual(
            views.normalize_status(u"  diamond \U0001f48e  "),
            u"diamond \U0001f48e",
        )

    def test_load_twitter_home_preserves_timeline_when_post_fails(self):
        class FakeApi:
            def PostUpdates(self, status):
                self.status = status
                raise views.twitter.TwitterError("provider detail")

            def GetUserTimeline(self, screen_name, count):
                self.screen_name = screen_name
                self.count = count
                return [make_status()]

        api = FakeApi()
        statuses, error, posted = views.load_twitter_home(api, "sample_user", "hello")

        self.assertEqual(statuses, [make_status()])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertFalse(posted)
        self.assertEqual(api.status, "hello")
        self.assertEqual(api.screen_name, "sample_user")
        self.assertEqual(api.count, 10)

    def test_load_twitter_home_returns_stable_error_when_timeline_fails(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                raise views.twitter.TwitterError("provider detail")

        statuses, error, posted = views.load_twitter_home(FakeApi(), "sample_user", None)

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)
        self.assertNotIn("provider detail", error)

    def test_load_twitter_home_accepts_tuple_timeline(self):
        first_status = make_status(1, "first status")
        second_status = make_status(2, "second status")

        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                return (first_status, second_status)

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", None
        )

        self.assertEqual(statuses, (first_status, second_status))
        self.assertIsNone(error)
        self.assertFalse(posted)

    def test_load_twitter_home_rejects_noncanonical_request_screen_name(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                raise AssertionError("invalid screen name must not reach provider")

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample-user", None
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_preserves_post_error_for_invalid_request_name(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise views.twitter.TwitterError("post provider detail")

            def GetUserTimeline(self, screen_name, count):
                raise AssertionError("invalid screen name must not reach provider")

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample-user", "hello"
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertFalse(posted)

    def test_timeline_status_requires_template_fields(self):
        self.assertTrue(views.timeline_status_is_renderable(make_status()))
        self.assertFalse(views.timeline_status_is_renderable(None))
        self.assertFalse(views.timeline_status_is_renderable(make_status(status_id=0)))
        self.assertFalse(views.timeline_status_is_renderable(make_status(status_id=True)))
        self.assertFalse(views.timeline_status_is_renderable(make_status(text=None)))
        self.assertFalse(views.timeline_status_is_renderable(make_status(text="  ")))
        self.assertFalse(views.timeline_status_is_renderable(make_status(screen_name="  ")))
        self.assertFalse(
            views.timeline_status_is_renderable(
                types.SimpleNamespace(id=42, text="missing user")
            )
        )

    def test_timeline_status_accepts_exact_text_limit(self):
        self.assertTrue(
            views.timeline_status_is_renderable(
                make_status(text="x" * views.MAX_STATUS_LENGTH)
            )
        )

    def test_timeline_status_bounds_unsigned_64_bit_ids(self):
        self.assertTrue(
            views.timeline_status_is_renderable(
                make_status(status_id=views.MAX_TWITTER_STATUS_ID)
            )
        )
        self.assertFalse(
            views.timeline_status_is_renderable(
                make_status(status_id=views.MAX_TWITTER_STATUS_ID + 1)
            )
        )
        self.assertFalse(
            views.timeline_status_is_renderable(make_status(status_id=10**5000))
        )

    def test_load_twitter_home_rejects_oversized_status_ids(self):
        oversized_ids = (views.MAX_TWITTER_STATUS_ID + 1, 10**5000)

        class FakeApi:
            def __init__(self, status_id):
                self.status_id = status_id

            def GetUserTimeline(self, screen_name, count):
                return [make_status(), make_status(status_id=self.status_id)]

        for status_id in oversized_ids:
            with self.subTest(bit_length=status_id.bit_length()):
                statuses, error, posted = views.load_twitter_home(
                    FakeApi(status_id), "sample_user", None
                )

                self.assertEqual(statuses, [])
                self.assertEqual(
                    error, "Twitter could not load the timeline right now."
                )
                self.assertFalse(posted)

    def test_load_twitter_home_rejects_oversized_timeline_text(self):
        oversized_status = make_status(text="x" * (views.MAX_STATUS_LENGTH + 1))

        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                return [make_status(), oversized_status]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", None
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)

    def test_timeline_status_rejects_lone_surrogates(self):
        for text in ("high-\ud800-surrogate", "low-\udfff-surrogate"):
            with self.subTest(text=repr(text)):
                self.assertFalse(
                    views.timeline_status_is_renderable(make_status(text=text))
                )

    def test_timeline_status_preserves_valid_supplementary_text(self):
        text = "valid \U0001f680 status"

        self.assertTrue(views.timeline_status_is_renderable(make_status(text=text)))
        self.assertEqual(text.encode("utf-8").decode("utf-8"), text)

    def test_load_twitter_home_rejects_lone_surrogate_text(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                return [make_status(), make_status(text="provider-\ud800-text")]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", None
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_preserves_post_error_for_oversized_timeline_text(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise views.twitter.TwitterError("post provider detail")

            def GetUserTimeline(self, screen_name, count):
                return [make_status(text="x" * (views.MAX_STATUS_LENGTH + 1))]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", "hello"
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertFalse(posted)

    def test_twitter_screen_name_accepts_canonical_values(self):
        for screen_name in ("a", "SampleUser", "sample_user", "user123", "x" * 15):
            with self.subTest(screen_name=screen_name):
                self.assertTrue(views.twitter_screen_name_is_valid(screen_name))

    def test_twitter_screen_name_rejects_noncanonical_values(self):
        invalid_screen_names = (
            None,
            "",
            "  ",
            "@sample_user",
            "sample-user",
            "sample.user",
            "sample/user",
            "sample user",
            "caf\u00e9",
            "x" * 16,
        )

        for screen_name in invalid_screen_names:
            with self.subTest(screen_name=screen_name):
                self.assertFalse(views.twitter_screen_name_is_valid(screen_name))

    def test_timeline_status_rejects_raising_accessors(self):
        self.assertFalse(views.timeline_status_is_renderable(RaisingStatus()))
        self.assertFalse(
            views.timeline_status_is_renderable(
                types.SimpleNamespace(id=42, text="status", user=RaisingUser())
            )
        )

    def test_load_twitter_home_rejects_malformed_timeline_items(self):
        malformed_items = (
            None,
            make_status(status_id=-1),
            make_status(text=["not", "text"]),
            make_status(text="  "),
            make_status(screen_name=None),
            types.SimpleNamespace(id=42, text="missing user"),
            RaisingStatus(),
            types.SimpleNamespace(id=42, text="status", user=RaisingUser()),
        )

        class FakeApi:
            def __init__(self, item):
                self.item = item

            def GetUserTimeline(self, screen_name, count):
                return [make_status(), self.item]

        for malformed_item in malformed_items:
            with self.subTest(item=repr(malformed_item)):
                statuses, error, posted = views.load_twitter_home(
                    FakeApi(malformed_item), "sample_user", None
                )

                self.assertEqual(statuses, [])
                self.assertEqual(
                    error, "Twitter could not load the timeline right now."
                )
                self.assertFalse(posted)

    def test_load_twitter_home_rejects_path_like_screen_name(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                return [make_status(), make_status(screen_name="sample/user")]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", None
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_rejects_malformed_timeline_results(self):
        malformed_results = (None, {}, "single status", 123, object())

        class FakeApi:
            def __init__(self, result):
                self.result = result

            def GetUserTimeline(self, screen_name, count):
                return self.result

        for malformed_result in malformed_results:
            with self.subTest(result=repr(malformed_result)):
                statuses, error, posted = views.load_twitter_home(
                    FakeApi(malformed_result), "sample_user", None
                )

                self.assertEqual(statuses, [])
                self.assertEqual(
                    error, "Twitter could not load the timeline right now."
                )
                self.assertFalse(posted)

    def test_load_twitter_home_accepts_exact_timeline_limit(self):
        expected = [make_status(status_id=index + 1) for index in range(10)]

        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                self.requested_count = count
                return expected

        api = FakeApi()
        statuses, error, posted = views.load_twitter_home(
            api, "sample_user", None
        )

        self.assertEqual(api.requested_count, views.TIMELINE_STATUS_LIMIT)
        self.assertEqual(statuses, expected)
        self.assertIsNone(error)
        self.assertFalse(posted)

    def test_load_twitter_home_rejects_oversized_timeline_results(self):
        class FakeApi:
            def GetUserTimeline(self, screen_name, count):
                return [make_status(status_id=index + 1) for index in range(count + 1)]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", None
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not load the timeline right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_preserves_post_error_for_malformed_timeline(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise views.twitter.TwitterError("post provider detail")

            def GetUserTimeline(self, screen_name, count):
                return None

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", "hello"
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_preserves_post_error_for_malformed_item(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise views.twitter.TwitterError("post provider detail")

            def GetUserTimeline(self, screen_name, count):
                return [make_status(), RaisingStatus()]

        statuses, error, posted = views.load_twitter_home(
            FakeApi(), "sample_user", "hello"
        )

        self.assertEqual(statuses, [])
        self.assertEqual(error, "Twitter could not post the status right now.")
        self.assertFalse(posted)

    def test_load_twitter_home_skips_timeline_after_successful_post(self):
        class FakeApi:
            def PostUpdates(self, status):
                self.status = status

            def GetUserTimeline(self, screen_name, count):
                raise AssertionError("timeline must not load after a successful post")

        api = FakeApi()
        statuses, error, posted = views.load_twitter_home(api, "sample-user", "hello")

        self.assertEqual(statuses, [])
        self.assertIsNone(error)
        self.assertTrue(posted)
        self.assertEqual(api.status, "hello")

    def test_home_redirects_after_successful_status_post(self):
        class FakeApi:
            def PostUpdates(self, status):
                self.status = status

            def GetUserTimeline(self, screen_name, count):
                raise AssertionError("timeline must not load after a successful post")

        api = FakeApi()
        original_get_twitter = views.get_twitter
        views.get_twitter = lambda user: api
        try:
            request = types.SimpleNamespace(
                POST={"status": "  hello  "},
                user=types.SimpleNamespace(username="sample_user"),
            )

            self.assertEqual(views.home(request), "/home")
            self.assertEqual(api.status, "hello")
        finally:
            views.get_twitter = original_get_twitter

    def test_home_renders_timeline_when_status_post_fails(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise views.twitter.TwitterError("provider detail")

            def GetUserTimeline(self, screen_name, count):
                return [make_status()]

        original_get_twitter = views.get_twitter
        views.get_twitter = lambda user: FakeApi()
        try:
            request = types.SimpleNamespace(
                POST={"status": "hello"},
                user=types.SimpleNamespace(username="sample_user"),
            )

            args, _kwargs = views.home(request)
            self.assertEqual(args[0], "home.html")
            self.assertEqual(args[1]["statuses"], [make_status()])
            self.assertEqual(
                args[1]["twitter_error"],
                "Twitter could not post the status right now.",
            )
        finally:
            views.get_twitter = original_get_twitter

    def test_home_does_not_post_non_string_status(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise AssertionError("malformed status must not reach Twitter")

            def GetUserTimeline(self, screen_name, count):
                return [make_status()]

        original_get_twitter = views.get_twitter
        views.get_twitter = lambda user: FakeApi()
        try:
            request = types.SimpleNamespace(
                POST={"status": ["unexpected", "list"]},
                user=types.SimpleNamespace(username="sample_user"),
            )

            args, _kwargs = views.home(request)
            self.assertEqual(args[1]["statuses"], [make_status()])
            self.assertIsNone(args[1]["twitter_error"])
        finally:
            views.get_twitter = original_get_twitter

    def test_home_does_not_post_lone_surrogate_status(self):
        class FakeApi:
            def PostUpdates(self, status):
                raise AssertionError("unencodable status must not reach Twitter")

            def GetUserTimeline(self, screen_name, count):
                return [make_status()]

        original_get_twitter = views.get_twitter
        views.get_twitter = lambda user: FakeApi()
        try:
            for status in (u"high \ud800", u"low \udfff"):
                with self.subTest(status=repr(status)):
                    request = types.SimpleNamespace(
                        POST={"status": status},
                        user=types.SimpleNamespace(username="sample_user"),
                    )

                    args, _kwargs = views.home(request)
                    self.assertEqual(args[1]["statuses"], [make_status()])
                    self.assertIsNone(args[1]["twitter_error"])
        finally:
            views.get_twitter = original_get_twitter

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

    def assert_environment_tokens_for_extra_data(self, extra_data):
        captured = {}

        class FakeManager:
            def get(self, user, provider):
                self.user = user
                self.provider = provider
                return types.SimpleNamespace(extra_data=extra_data)

        def fake_api(**kwargs):
            captured.update(kwargs)
            return captured

        original_user_social_auth = views.UserSocialAuth
        original_api = views.twitter.Api

        try:
            views.UserSocialAuth = types.SimpleNamespace(objects=FakeManager())
            views.twitter.Api = fake_api

            api = views.get_twitter(types.SimpleNamespace(username="sample-user"))

            self.assertIs(api, captured)
            self.assertEqual(captured["access_token_key"], "access-token")
            self.assertEqual(captured["access_token_secret"], "access-token-secret")
        finally:
            views.UserSocialAuth = original_user_social_auth
            views.twitter.Api = original_api

    def test_get_twitter_uses_environment_tokens_when_extra_data_is_string(self):
        self.assert_environment_tokens_for_extra_data("malformed")

    def test_get_twitter_uses_environment_tokens_when_extra_data_is_list(self):
        self.assert_environment_tokens_for_extra_data(["malformed"])

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

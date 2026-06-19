from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.http import require_POST

from social.apps.django_app.default.models import UserSocialAuth
import re
import twitter

MAX_STATUS_LENGTH = 280
MAX_TWITTER_STATUS_ID = (1 << 64) - 1
TIMELINE_STATUS_LIMIT = 10
TWITTER_SCREEN_NAME_RE = re.compile(r'^[A-Za-z0-9_]{1,15}\Z')
try:
    STRING_TYPES = (basestring,)
except NameError:
    STRING_TYPES = (str,)
try:
    INTEGER_TYPES = (int, long)
except NameError:
    INTEGER_TYPES = (int,)


def normalize_status(status):
    if status is None or type(status) not in STRING_TYPES:
        return None
    status = status.strip()
    if (
        not status or
        len(status) > MAX_STATUS_LENGTH or
        not twitter_text_is_utf8_encodable(status)
    ):
        return None
    return status


def normalize_token(value):
    if value is None:
        return None
    if type(value) not in STRING_TYPES:
        return None
    try:
        value = value.strip()
    except AttributeError:
        pass
    return value or None


def twitter_screen_name_is_valid(value):
    return (
        type(value) in STRING_TYPES and
        TWITTER_SCREEN_NAME_RE.match(value) is not None
    )


def twitter_text_is_utf8_encodable(value):
    if type(value) not in STRING_TYPES:
        return False
    try:
        value.encode('utf-8')
    except UnicodeError:
        return False
    return True


def normalize_timeline_status(status):
    try:
        status_id = getattr(status, 'id', None)
        text = getattr(status, 'text', None)
        user = getattr(status, 'user', None)
        screen_name = getattr(user, 'screen_name', None)
        if not (
            type(status_id) in INTEGER_TYPES and
            status_id > 0 and
            status_id <= MAX_TWITTER_STATUS_ID and
            type(text) in STRING_TYPES and
            bool(text.strip()) and
            len(text) <= MAX_STATUS_LENGTH and
            twitter_text_is_utf8_encodable(text) and
            twitter_screen_name_is_valid(screen_name)
        ):
            return None
        return {
            'id': status_id,
            'text': text,
            'screen_name': screen_name,
        }
    except Exception:
        return None


def timeline_status_is_renderable(status):
    return normalize_timeline_status(status) is not None


def load_twitter_home(api, username, status):
    error = None
    if status:
        try:
            api.PostUpdates(status)
            return [], None, True
        except (twitter.TwitterError, IOError, OSError):
            error = 'Twitter could not post the status right now.'

    if not twitter_screen_name_is_valid(username):
        if error is None:
            error = 'Twitter could not load the timeline right now.'
        return [], error, False

    try:
        statuses = api.GetUserTimeline(
            screen_name=username, count=TIMELINE_STATUS_LIMIT
        )
    except (twitter.TwitterError, IOError, OSError):
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'

    if type(statuses) not in (list, tuple):
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'
    elif len(statuses) > TIMELINE_STATUS_LIMIT:
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'
    else:
        normalized_statuses = []
        for item in statuses:
            normalized_status = normalize_timeline_status(item)
            if normalized_status is None:
                statuses = []
                if error is None:
                    error = 'Twitter could not load the timeline right now.'
                break
            normalized_statuses.append(normalized_status)
        else:
            statuses = normalized_statuses

    return statuses, error, False


def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):
    status = normalize_status(request.POST.get("status", None))

    api = get_twitter(request.user)
    statuses, twitter_error, posted = load_twitter_home(api, request.user.username, status)
    if posted:
        return HttpResponseRedirect('/home')

    context = {
        "request": request,
        'statuses': statuses,
        'twitter_error': twitter_error,
    }
    return render_to_response('home.html', context, context_instance=RequestContext(request))

from django.contrib.auth import logout as auth_logout
@login_required
@require_POST
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')

def get_twitter(user):

    consumer_key = normalize_token(settings.SOCIAL_AUTH_TWITTER_KEY)
    consumer_secret = normalize_token(settings.SOCIAL_AUTH_TWITTER_SECRET)
    if not consumer_key or not consumer_secret:
        raise ImproperlyConfigured('Twitter consumer key and secret must be configured in the environment.')

    access_token_key = normalize_token(settings.TWITTER_ACCESS_TOKEN)
    access_token_secret = normalize_token(settings.TWITTER_ACCESS_TOKEN_SECRET)

    try:
        usa = UserSocialAuth.objects.get(user=user, provider='twitter')
    except UserSocialAuth.DoesNotExist:
        usa = None

    if usa:
        try:
            extra_data = getattr(usa, 'extra_data', {}) or {}
            access_token = extra_data.get('access_token') if type(extra_data) is dict else None
            if type(access_token) is dict:
                social_token_key = normalize_token(access_token.get('oauth_token'))
                social_token_secret = normalize_token(access_token.get('oauth_token_secret'))
                if social_token_key and social_token_secret:
                    access_token_key = social_token_key
                    access_token_secret = social_token_secret
        except Exception:
            pass

    if not access_token_key or not access_token_secret:
        raise ImproperlyConfigured('Twitter access token and secret must be configured in social-auth or the environment.')

    api = twitter.Api(
        # base_url='https://api.twitter.com/1.1?include_cards=1&include_entities=1',
        base_url='https://api.twitter.com/1.1',
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token_key,
        access_token_secret=access_token_secret)

    return api

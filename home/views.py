from django.shortcuts import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.views.decorators.http import require_POST

from social.apps.django_app.default.models import UserSocialAuth
import twitter

MAX_STATUS_LENGTH = 280
try:
    STRING_TYPES = (basestring,)
except NameError:
    STRING_TYPES = (str,)
try:
    INTEGER_TYPES = (int, long)
except NameError:
    INTEGER_TYPES = (int,)


def normalize_status(status):
    if status is None or not isinstance(status, STRING_TYPES):
        return None
    status = status.strip()
    if not status or len(status) > MAX_STATUS_LENGTH:
        return None
    return status


def normalize_token(value):
    if value is None:
        return None
    if not isinstance(value, STRING_TYPES):
        return None
    try:
        value = value.strip()
    except AttributeError:
        pass
    return value or None


def timeline_status_is_renderable(status):
    try:
        status_id = getattr(status, 'id', None)
        text = getattr(status, 'text', None)
        user = getattr(status, 'user', None)
        screen_name = getattr(user, 'screen_name', None)
        return (
            isinstance(status_id, INTEGER_TYPES) and
            not isinstance(status_id, bool) and
            status_id > 0 and
            isinstance(text, STRING_TYPES) and
            isinstance(screen_name, STRING_TYPES) and
            bool(screen_name.strip())
        )
    except Exception:
        return False


def load_twitter_home(api, username, status):
    error = None
    if status:
        try:
            api.PostUpdates(status)
            return [], None, True
        except twitter.TwitterError:
            error = 'Twitter could not post the status right now.'

    try:
        statuses = api.GetUserTimeline(screen_name=username, count=10)
    except twitter.TwitterError:
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'

    if not isinstance(statuses, (list, tuple)):
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'
    elif not all(timeline_status_is_renderable(item) for item in statuses):
        statuses = []
        if error is None:
            error = 'Twitter could not load the timeline right now.'

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
        extra_data = getattr(usa, 'extra_data', {}) or {}
        access_token = extra_data.get('access_token') if isinstance(extra_data, dict) else None
        if isinstance(access_token, dict):
            access_token_key = normalize_token(access_token.get('oauth_token')) or access_token_key
            access_token_secret = normalize_token(access_token.get('oauth_token_secret')) or access_token_secret

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

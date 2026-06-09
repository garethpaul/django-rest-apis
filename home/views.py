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


def normalize_status(status):
    if status is None:
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


def login(request):
    context = {"request": request}
    return render_to_response('login.html', context, context_instance=RequestContext(request))

@login_required
def home(request):
    
    status = normalize_status(request.POST.get("status", None))
    
    api = get_twitter(request.user)
    if status:
        api.PostUpdates(status)
    
    statuses = api.GetUserTimeline(screen_name=request.user.username, count=10)
    
    context = {"request": request, 'statuses': statuses}
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
        access_token = extra_data.get('access_token')
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

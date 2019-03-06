from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from app import forms as app_forms, models as app_models, helpers as app_helpers
from twitter.client import TwitterClient


def index(request):
    return render(request, 'app/index.html')


def register(request):
    # For now, allow only one app to be registered.
    if app_models.TwitterApp.objects.exists():
        messages.info(request, _('You can only connect one Twitter app right now.'))
        return redirect('dashboard')
    if request.method == 'POST':
        register_form = app_forms.RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            messages.success(request, _('Successfully connected to Twitter app.'))
            return redirect('dashboard')
    else:
        register_form = app_forms.RegisterForm()
    return render(request, 'app/register.html', context={
        'register_form': register_form
    })


def auth(request, id):
    try:
        twitter_app = app_models.TwitterApp.objects.get(id=id)
        api_client = twitter_app.get_api_client()
        if api_client.get_auth_url():
            request.session['twitter_auth'] = request.session.pop('twitter_auth', {})
            request.session['twitter_auth'][api_client.oauth_token] = {
                'id': twitter_app.id,
                'secret': api_client.oauth_token_secret,
            }
            return redirect(api_client.auth_url)
        messages.error(request, _('Could not link your account to the Twitter app.'))
    except app_models.TwitterApp.DoesNotExist:
        messages.error(request, _('The Twitter app you requested does not exist.'))
    return redirect('dashboard')


def delete(request, id):
    try:
        app_models.TwitterApp.objects.filter(id=id).delete()
        messages.success(request, _('The Twitter app has been deleted.'))
    except app_models.TwitterApp.DoesNotExist:
        messages.error(request, _('The Twitter app you requested does not exist.'))
    return redirect('dashboard')


def callback(request):
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    if not oauth_token or not oauth_verifier:
        messages.error(request, _('Please provide credentials for authentication.'))
        return redirect('dashboard')

    auth_details = request.session.get('twitter_auth', {}).pop(oauth_token, {})
    if not auth_details.get('id'):
        messages.error(request, _(
            'No Twitter app was found for this callback. '
            'Please initiate account linking from inside Twennyson.'))
        return redirect('dashboard')

    try:
        twitter_app = app_models.TwitterApp.objects.get(id=auth_details.get('id'))
        api_client = TwitterClient(
            twitter_app.api_key,
            twitter_app.api_key_secret,
            oauth_token,
            auth_details.get('secret'))
        user_auth = api_client.get_authorized_tokens(oauth_verifier)
        if app_helpers.create_twitter_account_from_user_auth(user_auth, twitter_app):
            messages.success(request, _('Twitter account linked or updated successfully.'))
        else:
            messages.error(request, _('Twitter account could not be linked.'))
    except app_models.TwitterApp.DoesNotExist:
        messages.error(request, _('The Twitter app you requested does not exist.'))

    return redirect('dashboard')


def dashboard(request):
    if app_models.TwitterApp.objects.count():
        twitter_apps = app_models.TwitterApp.objects.all()
        twitter_accounts = app_models.TwitterAccount.objects.all()
        return render(request, 'app/dashboard.html', context={
            'twitter_apps': twitter_apps,
            'twitter_accounts': twitter_accounts,
        })

    messages.info(request, _('Please connect a Twitter app.'))
    return redirect('register')


def delete_account(request, id):
    try:
        app_models.TwitterAccount.objects.filter(id=id).delete()
        messages.success(request, _('The Twitter account has been deleted.'))
    except app_models.TwitterAccount.DoesNotExist:
        messages.error(request, _('The Twitter account you requested does not exist.'))
    return redirect('dashboard')

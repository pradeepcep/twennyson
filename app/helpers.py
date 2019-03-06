from app import models as app_models


def create_twitter_account_from_user_auth(user_auth, twitter_app):
    account_params = {}
    required_params = ['oauth_token', 'oauth_token_secret', 'user_id', 'screen_name']
    for param in required_params:
        if param not in user_auth:
            return
    account_params.update({
        'twitter_app': twitter_app,
        'access_token': user_auth['oauth_token'],
        'access_token_secret': user_auth['oauth_token_secret'],
        'user_id': user_auth['user_id'],
        'username': user_auth['screen_name'],
        'name': user_auth['screen_name'],
        'nickname': user_auth['screen_name']
    })
    try:
        twitter_account = app_models.TwitterAccount.objects.get(user_id=account_params['user_id'])
        app_models.TwitterAccount.objects.filter(id=twitter_account.id).update(**account_params)
        twitter_account.refresh_from_db()
    except app_models.TwitterAccount.DoesNotExist:
        twitter_account = app_models.TwitterAccount.objects.create(**account_params)
    return twitter_account

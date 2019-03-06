from django.conf import settings

from twython import Twython, TwythonError


class TwitterClient:

    def __init__(self, key, secret, *args, **kwargs):
        self.key = key
        self.secret = secret
        self.callback_url = kwargs.pop('callback_url', None)
        self.api = Twython(self.key, self.secret, *args, *kwargs)
        self.auth_url = None
        self.last_error = None

    def get_authentication_tokens(self):
        if self.callback_url:
            return self.api.get_authentication_tokens(callback_url=self.callback_url)
        return self.api.get_authentication_tokens()

    def get_auth_url(self):
        try:
            auth = self.get_authentication_tokens()
            self.auth_url = auth.get('auth_url')
            self.oauth_token = auth.get('oauth_token')
            self.oauth_token_secret = auth.get('oauth_token_secret')
            return self.auth_url
        except TwythonError as e:
            self.last_error = e

    def is_valid_credentials(self):
        return True if self.get_auth_url() else False

    def refresh_twitter_app(self, twitter_app):
        if self.get_auth_url():
            twitter_app.auth_url = self.auth_url
            twitter_app.oauth_token = self.oauth_token
            twitter_app.oauth_token_secret = self.oauth_token_secret
            twitter_app.save()
            return twitter_app

    def get_authorized_tokens(self, oauth_verifier):
        try:
            return self.api.get_authorized_tokens(oauth_verifier)
        except TwythonError as e:
            self.last_error = e

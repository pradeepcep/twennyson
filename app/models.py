import datetime

from django.db import models

from twitter.client import TwitterClient


class TwitterApp(models.Model):
    app_label = models.CharField(max_length=200, blank=True)
    api_key = models.CharField(max_length=200, unique=True)
    api_key_secret = models.CharField(max_length=200)
    callback_url = models.CharField(max_length=400, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_auth_url(self):
        client = TwitterClient(key=self.api_key, secret=self.api_key_secret, callback_url=self.callback_url)
        return client.get_auth_url()

    def get_api_client(self):
        return TwitterClient(key=self.api_key, secret=self.api_key_secret, callback_url=self.callback_url)


class TwitterAccount(models.Model):
    twitter_app = models.ForeignKey(TwitterApp, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=200, blank=True)
    access_token = models.CharField(max_length=100, null=True, blank=True)
    access_token_secret = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.CharField(max_length=25, unique=True)
    profile_picture_url = models.CharField(max_length=2100, null=True, blank=True)


class TwitterTweet(models.Model):
    from_user_id = models.CharField(max_length=25)
    to_user_id = models.CharField(max_length=25)
    contents = models.TextField()


class TwitterDM(models.Model):
    from_user_id = models.CharField(max_length=25)
    to_user_id = models.CharField(max_length=25)
    contents = models.TextField()

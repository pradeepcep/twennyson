from django import forms
from django.utils.translation import gettext as _

from app import models as app_models
from twitter.client import TwitterClient


class RegisterForm(forms.Form):
    app_label = forms.CharField(max_length=200, required=False)
    api_key = forms.CharField(max_length=200)
    api_key_secret = forms.CharField(max_length=200)
    callback_url = forms.URLField(initial='https://', required=False)

    def clean_app_label(self):
        return self.cleaned_data.get('app_label', '').strip()

    def clean_api_key(self):
        api_key = self.cleaned_data.get('api_key', '').strip()
        if app_models.TwitterApp.objects.filter(api_key=api_key).exists():
            raise forms.ValidationError(_('Invalid Credentials'))
        return api_key

    def clean_api_key_secret(self):
        return self.cleaned_data.get('api_key_secret', '').strip()

    def clean(self):
        cleaned_data = super().clean()
        api_key = cleaned_data.get('api_key')
        api_key_secret = cleaned_data.get('api_key_secret')
        callback_url = cleaned_data.get('callback_url')
        api_client = TwitterClient(api_key, api_key_secret, callback_url=callback_url)
        if not api_client.is_valid_credentials():
            raise forms.ValidationError(_('Invalid Credentials'))

        cleaned_data['app_label'] = cleaned_data.get('app_label', '') or api_key
        return cleaned_data

    def save(self):
        try:
            twitter_app = app_models.TwitterApp.objects.get(api_key=self.cleaned_data['api_key'])
            app_models.TwitterApp.objects.filter(id=twitter_app.id).update(**self.cleaned_data)
            return twitter_app
        except app_models.TwitterApp.DoesNotExist:
            return app_models.TwitterApp.objects.create(**self.cleaned_data)

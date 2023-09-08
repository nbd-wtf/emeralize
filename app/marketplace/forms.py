from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import UserProfile
from django.core import validators

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['lightning_address', 'bio', 'profile_pic', 'youtube_username', 'tiktok_username', 'twitter_username', 'twitch_username', 'website']
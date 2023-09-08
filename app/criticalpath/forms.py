from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.core import validators
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from criticalpath.humanize import naturalsize
from django.forms import ModelForm, Select
from captcha.fields import ReCaptchaField


from marketplace.models import UserProfile
from django.core import validators

class CreatorSignUpForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['creator']

class JourneyForm(ModelForm):
    class Meta:
        model = Journey
        fields = ['title', 'objective', 'category', 'price', 'cover_image']


class CourseForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Course
        fields = ['status', 'title', 'excerpt', 'cover_image', 'price' ]

class CourseAddResourcesForm(ModelForm):
    class Meta:
        model = CourseResources
        fields = ['resource', 'order_no' ]

class CoursePaymentSplitsForm(ModelForm):
    class Meta:
        model = CoursePaymentSplits
        fields = ['user', 'amount' ]

# class PhaseForm(ModelForm):
#     class Meta:
#         model = Phase
#         fields = ['title', 'description']

class EbookForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Ebook
        fields = ['status', 'title', 'excerpt', 'cover_image', 'price', 'currency_type', 'file', 'content' ]

class EbookPaymentSplitsForm(ModelForm):
    class Meta:
        model = EbookPaymentSplits
        fields = ['user', 'amount' ]

class WorkshopForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Workshop
        fields = ['status', 'title', 'excerpt', 'cover_image', 'price', 'currency_type', 'content' ]

class WorkshopPaymentSplitsForm(ModelForm):
    class Meta:
        model = WorkshopPaymentSplits
        fields = ['user', 'amount' ]


class ResourceForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Resource
        fields = ['status', 'title', 'excerpt', 'cover_image', 'price', 'content' ]


class SuperResourceForm(ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Resource
        fields = ['status', 'title', 'excerpt', 'cover_image', 'price', 'content', 'file', 'video']


class AddResourceForm(ModelForm):
    class Meta:
        model = JourneyResources
        fields = ['resource']


class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)


# https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/3.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other


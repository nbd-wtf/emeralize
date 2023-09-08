from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django import forms
# from captcha.fields import ReCaptchaField



class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    # captcha = ReCaptchaField()
    

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# class CaptchaPasswordResetForm(PasswordResetForm):
#     captcha = ReCaptchaField()



# class CaptchaForm(forms.Form):
#     captcha = ReCaptchaField()
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# from .forms import CaptchaPasswordResetForm


urlpatterns = [
    path('logout_user/', views.logout_view, name="logout_user"),
    path('register_user/', views.register_user, name="register"),
    path('help/', views.help, name="help"),
    path('password/', views.change_password, name='change_password'),
    path('logout_user/', views.logout_view, name="logout_user"),
    path('signin/', views.login_user, name="signin"),
    path("password_reset/", auth_views.PasswordResetView.as_view()),

    # path("password_reset/", auth_views.PasswordResetView.as_view(form_class=CaptchaPasswordResetForm)),

] 
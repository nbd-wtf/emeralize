"""emeralize URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, reverse_lazy
from .views import *
from django.contrib.auth.views import LoginView,LogoutView
from marketplace import views
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static


app_name='marketplace'
urlpatterns = [
    path('marketplace/', discover, name='discover'),
    path('marketplace/resources/', resource_list, name='resource_list'),
    path('journey/<int:pk>/buy/', journey_buy_view, name="journey_buy"),

    path('resource/<int:pk>/buy/', resource_buy_view, name="resource_buy"),
    path('resource/purchase_detail/<int:pk>/', views.ResourcePurchaseDetailView.as_view(), name="resource_purchase_detail"),
    path('resource/<int:resource>/buy/success/', resource_success, name="resource_success"),

    path('ebook/<int:pk>/buy/', ebook_buy_view, name="ebook_buy"),
    path('ebook/purchase_detail/<int:pk>/', views.EbookPurchaseDetailView.as_view(), name="ebook_purchase_detail"),
    path('ebook/<int:ebook>/buy/success/', ebook_success, name="ebook_success"),

    path('workshop/<int:pk>/buy/', workshop_buy_view, name="workshop_buy"),
    path('workshop/purchase_detail/<int:pk>/', views.WorkshopPurchaseDetailView.as_view(), name="workshop_purchase_detail"),
    path('workshop/<int:workshop>/buy/success/', workshop_success, name="workshop_success"),

    path('course/purchase_detail/<int:pk>/', views.CoursePurchaseDetailView.as_view(), name="course_purchase_detail"),
    path('course/<int:pk>/buy/', course_buy_view, name="course_buy"),
    path('course/<int:course>/buy/success/', course_success, name="course_success"),

    path('journey/<int:journey>/buy/success/', journey_success, name="journey_success"),
    path('webhook/zbd/', csrf_exempt(zbd_webhook), name="charge_callback"),
    path('charge-status/', charge_status_check),
    path('purchase-history/', purchase_history, name="purchase-history"),
    path('transaction-history/', transaction_history, name="transaction-history"),
    path('accounts/profile/', views.UserProfileCreate.as_view(), name="account-profile"),
    path('profile/<username>/', profile, name="user-profile"),
    path('profile/<username>/tip/', tip_amount, name="tip-amount"),
    path('profile/<username>/tip/pay/', tip_pay, name="tip-pay"),
    path('profile/<username>/tip/pay/success/', tip_success, name="tip-success"),
    path('wallet/', wallet_view, name="wallet"),
    path('withdrawal/', withdrawal, name="withdrawal"),
    path('terms/', terms, name="terms"),
    path('privacy/', privacy, name="privacy"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

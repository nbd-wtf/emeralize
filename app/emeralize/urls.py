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
from django.urls import path, reverse_lazy, include
from marketplace.views import homepage
from marketplace import views
from accounts.views import confirm
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django_email_verification import urls as email_urls  # include the urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="home"),
    path('', include('marketplace.urls')),
    path('', include('criticalpath.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include(email_urls)),  # connect them to an arbitrary path
    # path('email/<str:token>/', confirm), # remember to set the "token" parameter in the url!


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "marketplace.views.handle_not_found"

# if settings.DEBUG:
#     urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL,  
                        document_root=settings.MEDIA_ROOT) 
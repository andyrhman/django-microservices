"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path
from rest_framework import status
from rest_framework.exceptions import JsonResponse

urlpatterns = [
    path('api/admin/categories/', include(('core.urls_admin', 'category'), namespace='admin_category')),
    path('api/categories/', include(('core.urls', 'category'), namespace='user_category')),     
]

def custom_404(request, exception):
    return JsonResponse(
        {"detail": "Not found."},
        status=status.HTTP_404_NOT_FOUND
    )

def custom_500(request):
    return JsonResponse(
        {"detail": "Internal server error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

handler404 = 'app.urls.custom_404'
handler500 = 'app.urls.custom_500'
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
from django.http import JsonResponse
from django.urls import include, path
from rest_framework import status

urlpatterns = [
    path('api/admin/', include(('core.urls_admin', 'address'), namespace='admin_address')),
    path('api/', include(('core.urls', 'address'), namespace='user_address')),   
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
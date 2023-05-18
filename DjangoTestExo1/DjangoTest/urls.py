"""
URL configuration for DjangoTest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
import requests

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

#Générez des jetons d'authentification pour les utilisateurs
urlpatterns = [
    # Other URL patterns
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

def get_page_list(request):
    #  récupérer la liste des pages de Notion
    response = requests.get('https://api.notion.com/pages', headers={'Authorization': 'Bearer YOUR_API_KEY'})
    data = response.json()
    return JsonResponse(data)

def get_page_details(request, page_id):
    #  récupérer les détails d'une page spécifique de Notion
    response = requests.get(f'https://api.notion.com/pages/{page_id}', headers={'Authorization': 'Bearer YOUR_API_KEY'})
    data = response.json()
    return JsonResponse(data)

def update_page(request, page_id):
    #  mettre à jour une page de Notion
    # requête (request) envoyée par le client
    new_title = request.POST.get('title')
    payload = {'title'}

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.shortcuts import render
from django.http import JsonResponse
import requests
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView


#les donnés du notion api c'est juste des exemples 

def get_page_list(request):
    # Logique pour récupérer la liste des pages de Notion
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json',
        'Notion-Version': '2023-05-18',  
    }

    response = requests.get('https://api.notion.com/v1/pages', headers=headers)

    if response.status_code == 200:
        notion_pages = response.json()
        return JsonResponse(notion_pages, safe=False)
    else:
        return JsonResponse({'error': 'Impossible de récupérer les pages'}, status=response.status_code)

def get_page_details(request, page_id):
    # Logique pour récupérer les détails d'une page spécifique de Notion
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json',
        'Notion-Version': '2023-05-18',  
    }

    url = f'https://api.notion.com/v1/pages/{page_id}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        notion_page = response.json()
        return JsonResponse(notion_page)
    else:
        return JsonResponse({'error': 'Impossible de récupérer les details des pages'}, status=response.status_code)

def update_page(request, page_id):
    # Logic to update a page in Notion
    # You can extract the update data from the request sent by the client
    try:
        updated_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalide JSON data'}, status=400)

    # Send a request to the Notion API to update the page
    headers = {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json',
        'Notion-Version': '2023-05-18', 
    }

    url = f'https://api.notion.com/v1/pages/{page_id}'
    response = requests.patch(url, json=updated_data, headers=headers)

    if response.status_code == 200:
        return JsonResponse({'message': 'Page mise à jour avec succès'})
    else:
        return JsonResponse({'error': 'Échec de la mise à jour de la page'}, status=response.status_code)
    
    #Protégez les points d'accès avec l'authentification
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_view(request):
   class MyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the authenticated user
        user = request.user

        data = {
            'message': f'Hello, {user.username}! Ceci est une ressource protégée.'
        }

        # Return a response
        return Response(data)
    pass
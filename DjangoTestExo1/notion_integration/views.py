import json
from django.shortcuts import render
from django.http import JsonResponse
import requests
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view, parser_classes
from .models import Video, VideoAnalysis
import openai
from django.utils import timezone
import subprocess

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

    
def perform_video_analysis(video):
    
    video_content = video.read()  # Lire le contenu du fichier vidéo
    # Ou
    video_url = video.url  # Obtenir l'URL de la vidéo

    # Appeler l'API Whisper d'OpenAI pour effectuer l'analyse vidéo
    response = openai.whisper_analyze_video(video_content=video_content, video_url=video_url)

    # Analyser et extraire les résultats de l'analyse vidéo à partir de la réponse de l'API
    title = response['title']
    content = response['description']
    analysis_date = response['analysis_date']
    confidence_score = response['confidence_score']
    category = response['category']
    duration = response['duration']
    thumbnail_url = response['thumbnail_url']
    location = response['location']

    # Retourner les résultats de l'analyse vidéo
    analysis_results = {
        'title': title,
        'content': content,
        'analysis_date': analysis_date,
        'confidence_score': confidence_score,
        'category': category,
        'duration': duration,
        'thumbnail_url': thumbnail_url,
        'location': location,
    }
    return analysis_results

def process_video(video_content, video_url):

    # Appeler l'API Whisper d'OpenAI pour effectuer l'analyse vidéo
    response = requests.post(
        'aoi ici ',
        headers={'Authorization': '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'},
        json={'video_content': video_content, 'video_url': video_url}
    )

    # Vérifiez et traitez la réponse de l'API
    if response.status_code == 200:
        analysis_results = response.json()
        return analysis_results
    else:
        # Gérez les erreurs de l'appel API selon vos besoins
        raise Exception('Failed to analyze video: ' + response.text)

@api_view(['POST'])
@parser_classes([FileUploadParser])
@csrf_exempt
def upload_video(request):
    video_file = request.FILES['video']

    # Traitez le fichier vidéo ou l'URL ici et effectuez l'analyse vidéo en utilisant l'API Whisper d'OpenAI
    analysis_results = process_video(video_content=video_file.read(), video_url='')

    # Enregistrez la vidéo dans la base de données
    video = Video.objects.create(
        title=video_file.name,
        content=video_file.read(),
        confidence_score=0,
        category='',
        analysis_date=timezone.now(),
        duration=0,
        thumbnail=None,
    )
    
    # Effectuez l'analyse vidéo et enregistrez les résultats dans la base de données
    video_analysis = VideoAnalysis.objects.create(
        video=video,
        confidence_score=analysis_results['confidence_score'],
        category=analysis_results['category'],
        timestamp=timezone.now(),
        location=analysis_results['location'],
        description=analysis_results['description'],
    )

    return JsonResponse({'message': 'Video uploaded and analyzed successfully.'})


import json
from django.shortcuts import render
from django.http import JsonResponse
import requests
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view, parser_classes
from .models import Video, VideoAnalysis
import openai
from django.utils import timezone
import subprocess
import os
from django.http import HttpResponseBadRequest, JsonResponse

MAX_VIDEO_SIZE = 25 * 1024 * 1024  # 25 MB
openai.api_key = "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"
"""
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
    pass"""

  
def analyze_video(video_content):
    # Étape 1: Enregistrer le contenu du fichier vidéo dans un fichier temporaire
    with open("video_temp.mp4", "wb") as file:
        for chunk in video_content.chunks():
            file.write(chunk)

    # Étape 2: Vérifier le format du fichier vidéo
    allowed_formats = [".mp4", ".mpeg", ".m4a", ".webm"]
    file_extension = os.path.splitext("video_temp.mp4")[1]
    if file_extension.lower() not in allowed_formats:
        os.remove("video_temp.mp4")
        return HttpResponseBadRequest("Le format de fichier vidéo n'est pas pris en charge.")

    # Étape 3: Vérifier la taille du fichier vidéo
    file_size = os.path.getsize("video_temp.mp4")
    if file_size > MAX_VIDEO_SIZE:
        os.remove("video_temp.mp4")
        return HttpResponseBadRequest("La taille du fichier vidéo dépasse la limite autorisée.")

    # Étape 4: Extraire l'audio de la vidéo
    audio_filename = "audio_temp.wav"
    extract_audio_command = f'ffmpeg -i video_temp.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_filename}'
    os.system(extract_audio_command)

    # Étape 5: Appeler l'API Whisper pour transcrire l'audio
    with open(audio_filename, "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)

    # Étape 6: Supprimer les fichiers temporaires
    os.remove("video_temp.mp4")
    os.remove(audio_filename)

    return response

@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES['video']
        content_type = video_file.content_type
        file_size = video_file.size

        # Vérifier le format du fichier vidéo
        valid_formats = ['video/mp4', 'video/mpeg', 'audio/mp4', 'video/webm']
        if content_type not in valid_formats:
            return JsonResponse({'message': 'Invalid video format.'}, status=400)

        # Vérifier la taille du fichier vidéo
        if file_size > MAX_VIDEO_SIZE:
            return JsonResponse({'message': 'Video file size exceeds the limit.'}, status=400)

        # Traiter le fichier vidéo ici et extraire l'audio
        video_content = video_file.read()

        # Appeler la méthode analyze_video pour effectuer l'analyse de l'audio
        response = analyze_video(video_content)

        if response.status == "completed":
            # Récupérer la transcription de l'audio
            transcription = response.transcriptions[0].text

            # Enregistrer la transcription dans la base de données 
            video = Video.objects.create(
                title=video.file.name,
                content=video.file.read(),
                analysis_date=timezone.now(),
            )
            
            VideoAnalysis = VideoAnalysis.objects.create(
                video=video,
                timestamp=timezone.now(),
                transcription=transcription,
            )

            return JsonResponse({'message': 'Video uploaded and audio analyzed successfully.'})
        else:
            return JsonResponse({'message': 'Failed to analyze video audio.'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

from contextvars import Token
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


#Générez des jetons d'authentification pour les utilisateurs
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Video(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    confidence_score = models.FloatField()
    category = models.CharField(max_length=50)
    analysis_date = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    thumbnail = models.ImageField(upload_to='video_thumbnails/')

    def __str__(self):
        return self.title


class VideoAnalysis(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    category = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"Analysis for {self.video.title}"

post_save.connect(create_auth_token, sender=User)
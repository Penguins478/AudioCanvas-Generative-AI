from django.db import models

class AudioRecord(models.Model):
    audio_file = models.FileField(upload_to='audio/')
    transcription = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return str(self.id)
    
class CachedImage(models.Model):
    transcription = models.TextField(unique=True)
    image_url = models.URLField()

    def __str__(self):
        return self.transcription

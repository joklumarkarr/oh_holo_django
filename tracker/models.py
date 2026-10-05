from django.db import models

# Create your models here.

class VTuber(models.Model):
    slug = models.SlugField(unique=True, help_text="Also the CSS theme class, e.g. 'mumei'")
    name = models.CharField(max_length=100)
    youtube_channel_id = models.CharField(max_length=64, blank=True)
    twitch_username = models.CharField(max_length=64, blank=True)
    is_live_youtube = models.BooleanField(default=False)
    is_live_twitch = models.BooleanField(default=False)

    def __str__(self):
        return self.name
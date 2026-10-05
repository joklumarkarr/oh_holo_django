from django.db import models

# Create your models here.

class VTuber(models.Model):
    slug = models.SlugField(unique=True, help_text="Also the CSS theme class, e.g. 'mumei'")
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, help_text="Filename inside tracker/static/tracker/images/")
    youtube_channel_id = models.CharField(max_length=64, blank=True)
    twitch_username = models.CharField(max_length=64, blank=True)
    is_live_youtube = models.BooleanField(default=False)
    is_live_twitch = models.BooleanField(default=False)

    # Filled in by the Holodex bootstrap command (Chapter 12)
    subscriber_count = models.BigIntegerField(null=True, blank=True)
    view_count = models.BigIntegerField(null=True, blank=True)
    profile_image_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.name


class StreamArchive(models.Model):
    class Platform(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        TWITCH = "twitch", "Twitch"

    class Status(models.TextChoices):
        LIVE = "live", "Live"
        UPCOMING = "upcoming", "Upcoming"
        ENDED = "ended", "Ended"

    vtuber = models.ForeignKey(VTuber, on_delete=models.CASCADE, related_name="streams")
    platform = models.CharField(max_length=10, choices=Platform.choices)
    stream_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ENDED)
    url = models.URLField(blank=True, max_length=500)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.vtuber} [{self.platform}] {self.title[:40]}"
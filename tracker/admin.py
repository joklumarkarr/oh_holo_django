from django.contrib import admin

# Register your models here.

from .models import StreamArchive, VTuber


@admin.register(VTuber)
class VTuberAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "youtube_channel_id", "twitch_username", "is_live_youtube", "is_live_twitch")

@admin.register(StreamArchive)
class StreamArchiveAdmin(admin.ModelAdmin):
    list_display = ("title", "vtuber", "platform", "started_at", "ended_at")
    list_filter = ("platform", "vtuber")
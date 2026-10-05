import json

from django.shortcuts import render
from django.templatetags.static import static

from .models import StreamArchive, VTuber

# Create your views here.

def stream_payload(stream):
    """Shape one StreamArchive row down to what the template/JS actually needs."""
    if stream is None:
        return None
    when = stream.started_at or stream.scheduled_at
    return {
        "title": stream.title,
        "link": stream.url,
        "thumbnail": f"https://i.ytimg.com/vi/{stream.stream_id}/maxresdefault.jpg",
        "date": when.isoformat() if when else None,
    }


def vtuber_payload(vtuber):
    live = vtuber.streams.filter(status=StreamArchive.Status.LIVE).order_by("-started_at").first()
    upcoming = vtuber.streams.filter(status=StreamArchive.Status.UPCOMING).order_by("scheduled_at").first()
    completed = vtuber.streams.filter(status=StreamArchive.Status.ENDED).order_by("-started_at").first()
    return {
        "slug": vtuber.slug,
        "name": vtuber.name,
        "icon_url": static(f"tracker/images/{vtuber.icon or 'placeholder.png'}"),
        "alt_icon_url": static(f"tracker/images/{vtuber.alt_icon or 'placeholder.png'}"),
        "noise_url": static(f"tracker/sounds/{vtuber.noise}") if vtuber.noise else "",
        "channel_link": f"https://www.youtube.com/channel/{vtuber.youtube_channel_id}" if vtuber.youtube_channel_id else "",
        "subscribers": vtuber.subscriber_count,
        "views": vtuber.view_count,
        "streams": {
            "live": stream_payload(live),
            "upcoming": stream_payload(upcoming),
            "completed": stream_payload(completed),
        },
    }


def index(request):
    vtubers = VTuber.objects.order_by("id")
    payload = [vtuber_payload(v) for v in vtubers]
    return render(request, "tracker/index.html", {
        "vtubers": vtubers,
        "vtubers_json": payload,
    })
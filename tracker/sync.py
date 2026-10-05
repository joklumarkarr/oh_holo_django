"""Everything that turns Holodex data into database rows and browser updates.

Used by:
  - the `bootstrap_data` command (one-off seeding),
  - the `poll_live` command (the long-running poller, Chapter 16).
"""
import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from . import services
from .consumers import GROUP_NAME
from .models import StreamArchive, VTuber
from .views import vtuber_payload

logger = logging.getLogger(__name__)
S = StreamArchive.Status


# --- Turning Holodex entries into rows (shared with bootstrap_data) ----------

def pick_entry(entries):
    """A channel can show up 0, 1, or 2+ times in the live/upcoming batch
    (e.g. live now AND a separate stream scheduled later). Live wins; if
    nothing's live, take the soonest upcoming one. Non-stream items
    (freechat/schedule community posts) are filtered out entirely."""
    entries = [e for e in entries if e.get("type") == "stream"]
    if not entries:
        return None
    live = [e for e in entries if e.get("status") == "live"]
    if live:
        return live[0]
    upcoming = sorted(entries, key=lambda e: e.get("start_scheduled") or "")
    return upcoming[0] if upcoming else None


def upsert_live_or_upcoming(vtuber, entry):
    is_live = entry["status"] == "live"
    StreamArchive.objects.update_or_create(
        stream_id=entry["id"],
        defaults={
            "vtuber": vtuber,
            "platform": StreamArchive.Platform.YOUTUBE,
            "title": entry.get("title", "")[:300],
            "status": S.LIVE if is_live else S.UPCOMING,
            "url": f"https://www.youtube.com/watch?v={entry['id']}",
            "scheduled_at": parse_datetime(entry.get("start_scheduled") or ""),
            "started_at": parse_datetime(entry.get("start_actual") or ""),
        },
    )
    vtuber.is_live_youtube = is_live
    vtuber.save(update_fields=["is_live_youtube"])


def upsert_past_video(vtuber, video):
    started = parse_datetime(video.get("start_actual") or video.get("available_at") or "")
    ended = None
    if started and video.get("duration"):
        ended = started + timedelta(seconds=video["duration"])
    StreamArchive.objects.update_or_create(
        stream_id=video["id"],
        defaults={
            "vtuber": vtuber,
            "platform": StreamArchive.Platform.YOUTUBE,
            "title": video.get("title", "")[:300],
            "status": S.ENDED,
            "url": f"https://www.youtube.com/watch?v={video['id']}",
            "started_at": started,
            "ended_at": ended,
        },
    )


# --- Broadcasting ------------------------------------------------------------

def broadcast_vtuber(vtuber, payload=None):
    """Push one talent's current state to every connected browser, over the
    same Chapter 15 group the consumer already listens on."""
    async_to_sync(get_channel_layer().group_send)(
        GROUP_NAME,
        {"type": "vtuber.update", "vtuber": payload or vtuber_payload(vtuber)},
    )


def run_and_broadcast(vtuber, action, *args):
    """Run `action`, then broadcast ONLY if what a browser would see changed.
    Comparing before/after payloads means an unchanged talent costs nothing."""
    before = vtuber_payload(vtuber)
    action(vtuber, *args)
    after = vtuber_payload(vtuber)
    if before == after:
        return False
    broadcast_vtuber(vtuber, after)
    return True


# --- The two kinds of refresh ------------------------------------------------

def apply_live_batch(vtuber, entries):
    """Apply one talent's slice of the batched /users/live response.

    Besides writing what Holodex reports, this reconciles rows that have
    disappeared from the report: a LIVE row that is no longer reported has
    ended; an UPCOMING row that is no longer reported was cancelled (or
    started, in which case it would be reported as live and handled above)."""
    streams = [e for e in entries if e.get("type") == "stream"]
    reported_ids = {e["id"] for e in streams}

    entry = pick_entry(streams)
    if entry:
        upsert_live_or_upcoming(vtuber, entry)
    elif vtuber.is_live_youtube:
        vtuber.is_live_youtube = False
        vtuber.save(update_fields=["is_live_youtube"])

    just_ended = False
    stale = vtuber.streams.filter(status__in=[S.LIVE, S.UPCOMING]).exclude(stream_id__in=reported_ids)
    for row in stale:
        if row.status == S.LIVE:
            row.status = S.ENDED
            row.ended_at = row.ended_at or timezone.now()
            row.save(update_fields=["status", "ended_at"])
            just_ended = True
        else:
            row.delete()

    if just_ended:
        # Holodex now lists it as a past video, with proper title/duration.
        try:
            video = services.fetch_last_past_video(vtuber.youtube_channel_id)
            if video:
                upsert_past_video(vtuber, video)
        except Exception as e:
            logger.warning("past-video lookup failed for %s: %s", vtuber.slug, e)


def refresh_slow(vtuber):
    """The slow-changing data: subscriber/view counts and the latest past stream."""
    channel_id = vtuber.youtube_channel_id
    try:
        stats = services.fetch_channel_stats(channel_id)
        vtuber.subscriber_count = int(stats.get("subscriber_count") or 0)
        vtuber.view_count = int(stats.get("view_count") or 0)
        vtuber.profile_image_url = stats.get("photo", "")
        vtuber.save(update_fields=["subscriber_count", "view_count", "profile_image_url"])
    except Exception as e:
        logger.warning("stats failed for %s: %s", vtuber.slug, e)

    try:
        video = services.fetch_last_past_video(channel_id)
        if video:
            upsert_past_video(vtuber, video)
    except Exception as e:
        logger.warning("past video failed for %s: %s", vtuber.slug, e)


# --- What the poller calls ----------------------------------------------------

def poll_live_once():
    """ONE batched Holodex call for every talent; returns slugs that changed."""
    vtubers = list(VTuber.objects.exclude(youtube_channel_id=""))
    if not vtubers:
        return []
    by_channel = services.fetch_live_status([v.youtube_channel_id for v in vtubers])
    return [
        v.slug for v in vtubers
        if run_and_broadcast(v, apply_live_batch, by_channel.get(v.youtube_channel_id, []))
    ]


def refresh_slow_all(pause=0.3):
    """Per-talent calls (2 each), spaced out to be polite to Holodex."""
    import time
    changed = []
    for v in VTuber.objects.exclude(youtube_channel_id=""):
        if run_and_broadcast(v, refresh_slow):
            changed.append(v.slug)
        time.sleep(pause)
    return changed
import time

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from tracker.models import StreamArchive, VTuber
from tracker import services

S = StreamArchive.Status

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
        from datetime import timedelta
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


class Command(BaseCommand):
    help = "Seed VTuber stats and current/past streams from Holodex."

    def handle(self, *args, **options):
        vtubers = list(VTuber.objects.exclude(youtube_channel_id=""))
        if not vtubers:
            self.stdout.write(self.style.WARNING("No VTubers with a youtube_channel_id yet — run seed_data first."))
            return

        # Step 1: one batched call covers live/upcoming status for everyone.
        self.stdout.write("Checking live/upcoming status for all channels...")
        live_by_channel = services.fetch_live_status([v.youtube_channel_id for v in vtubers])

        for vtuber in vtubers:
            entry = pick_entry(live_by_channel.get(vtuber.youtube_channel_id, []))
            if entry:
                upsert_live_or_upcoming(vtuber, entry)
            elif vtuber.is_live_youtube:
                vtuber.is_live_youtube = False
                vtuber.save(update_fields=["is_live_youtube"])

        # Step 2 + 3: per-talent stats and most-recent-past-video calls.
        for vtuber in vtubers:
            self.stdout.write(f"  {vtuber.name}...")
            try:
                stats = services.fetch_channel_stats(vtuber.youtube_channel_id)
                vtuber.subscriber_count = int(stats.get("subscriber_count") or 0)
                vtuber.view_count = int(stats.get("view_count") or 0)
                vtuber.profile_image_url = stats.get("photo", "")
                vtuber.save(update_fields=["subscriber_count", "view_count", "profile_image_url"])
            except Exception as e:
                self.stderr.write(f"    stats failed: {e}")

            try:
                video = services.fetch_last_past_video(vtuber.youtube_channel_id)
                if video:
                    upsert_past_video(vtuber, video)
            except Exception as e:
                self.stderr.write(f"    past video failed: {e}")

            time.sleep(0.1)  # be polite to Holodex's rate limits between per-channel calls

        self.stdout.write(self.style.SUCCESS("Bootstrap complete."))
import time

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from tracker import services
from tracker.models import StreamArchive, VTuber
from tracker.sync import pick_entry, upsert_live_or_upcoming, upsert_past_video

S = StreamArchive.Status

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
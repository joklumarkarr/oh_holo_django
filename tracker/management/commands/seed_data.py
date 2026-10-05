from django.core.management.base import BaseCommand

from tracker.models import VTuber
from tracker.seed_data import TALENTS


class Command(BaseCommand):
    help = "Create/update VTuber rows from tracker/seed_data.py. Safe to re-run on every deploy."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for slug, name, icon, youtube_channel_id, twitch_username in TALENTS:
            obj, was_created = VTuber.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "icon": icon,
                    "youtube_channel_id": youtube_channel_id,
                    "twitch_username": twitch_username,
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {created} created, {updated} updated, {len(TALENTS)} total."
        ))
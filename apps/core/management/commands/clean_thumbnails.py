"""Clear the sorl-thumbnail KVStore before committing db.sqlite3.

Why: sorl serves a thumbnail straight from the KVStore when a row exists, WITHOUT
checking that the cached file is present. If the committed db ships a populated
KVStore, a fresh deploy (whose media/cache may differ / be regenerated) serves URLs
for files that aren't there → broken product/article images.

Invariant: **the committed db's sorl KVStore stays empty.** With an empty KVStore
sorl always falls back to the on-disk check — it reuses a committed media/cache file
if present (no regeneration), or regenerates on demand otherwise. The media/cache
thumbnails ARE committed so the demo renders without regenerating.

Run this before `git add db.sqlite3`. See DEMO_TO_PRODUCTION.md / the dev-hygiene note.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear the sorl-thumbnail KVStore (keep media/cache files) before committing db.sqlite3."

    def handle(self, *args, **options):
        from sorl.thumbnail.models import KVStore

        n = KVStore.objects.count()
        KVStore.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            "Cleared %d sorl KVStore rows. Committed db is now safe; media/cache files kept."
            % n))

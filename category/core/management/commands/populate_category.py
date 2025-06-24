from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = "Import category from the old 'django_shop' database into this service."

    def handle(self, *args, **options):
        old_qs = Category.objects.using('old_data').all()
        self.stdout.write(f"Found {old_qs.count()} category in old DB.")

        for old in old_qs:
            if Category.objects.filter(name=old.name).exists():
                self.stdout.write(f"Skipping existing category: {old.name}")
                continue

            Category.objects.create(
                name=old.name,
            )
            
            self.stdout.write(f"Imported category {old.name}")

        self.stdout.write(self.style.SUCCESS("Import completed."))

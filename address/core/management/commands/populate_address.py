from django.core.management.base import BaseCommand
from core.models import Address

class Command(BaseCommand):
    help = "Import address from the old 'django_shop' database into this service."

    def handle(self, *args, **options):
        old_qs = Address.objects.using('old_data').all()
        self.stdout.write(f"Found {old_qs.count()} address in old DB.")

        for old in old_qs:
            if Address.objects.filter(user=old.user).exists():
                self.stdout.write(f"Skipping existing user addaress: {old.user}")
                continue

            Address.objects.create(
                street=old.street,
                city=old.city,
                province=old.province,
                zip=old.zip,
                country=old.country,
                phone=old.phone,
                user=old.user,
            )
            self.stdout.write(f"Imported address {old.street}")

        self.stdout.write(self.style.SUCCESS("Import completed."))

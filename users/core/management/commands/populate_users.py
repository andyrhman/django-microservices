from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = "Import users from the old 'django_shop' database into this service."

    def handle(self, *args, **options):
        old_qs = User.objects.using('old_users').all()
        self.stdout.write(f"Found {old_qs.count()} users in old DB.")

        for old in old_qs:
            if User.objects.filter(username=old.username).exists():
                self.stdout.write(f"Skipping existing user: {old.username}")
                continue

            new = User.objects.create(
                fullName=old.fullName,
                email=old.email,
                username=old.username,
                is_user=old.is_user,
            )
            new.password = old.password
            new.save()
            self.stdout.write(f"Imported user {old.username}")

        self.stdout.write(self.style.SUCCESS("Import completed."))

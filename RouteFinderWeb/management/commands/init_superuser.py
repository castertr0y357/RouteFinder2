from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Creates a default superuser from .env variables on startup if it does not already exist'

    def handle(self, *args, **options):
        # Pull from environment variables
        admin_user = os.environ.get('DEFAULT_ADMIN_USER', 'admin')
        admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
        admin_pass = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')

        if not User.objects.filter(username=admin_user).exists():
            User.objects.create_superuser(username=admin_user, email=admin_email, password=admin_pass)
            self.stdout.write(self.style.SUCCESS(f"Successfully injected default administrative superuser: {admin_user}"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{admin_user}' already securely exists. Bypassing generation."))

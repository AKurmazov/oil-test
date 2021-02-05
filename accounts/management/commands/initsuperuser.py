from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(self, *args, **options):
        credentials = settings.ADMIN_CREDENTIALS
        admin = get_user_model().objects.create_superuser(username=credentials['username'],
                                                           password=credentials['password'])
        admin.is_active = True
        admin.is_admin = True
        admin.save()

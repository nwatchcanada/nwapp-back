from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    """
    python manage.py clearcache.py
    """
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')

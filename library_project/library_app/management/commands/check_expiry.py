from django.core.management.base import BaseCommand
from library_app.tasks import check_expiry

class Command(BaseCommand):
    help = 'Check premium expiry and send warning emails'

    def handle(self, *args, **kwargs):
        check_expiry()
        self.stdout.write(self.style.SUCCESS('Expiry check completed'))
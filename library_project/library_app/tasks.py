from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import Premium


def check_expiry():
    warning_date = timezone.now().date() + timedelta(days=2)

    users = Premium.objects.filter(expiry_date=warning_date)

    for premium in users:
        send_mail(
            "Premium Expiring Soon ⚠",
            f"Hi {premium.user.username},\n\n"
            "Your premium access will expire in 2 days.\n"
            "Renew now to continue enjoying premium books.",
            "wavhalpuja053@gmail.com",   # your sender email
            [premium.user.email],
            fail_silently=True,
        )
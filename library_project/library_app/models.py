from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from datetime import date

# ---------------- BOOK MODEL ----------------
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    book_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)
    is_availible = models.BooleanField(default=True)

    # 👑 ADD THIS
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# ---------------- BORROW RECORD MODEL ----------------
class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(default=timezone.now)  # <- fixed
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
class Premium(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchased_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()

    def is_active(self):
        return self.expiry_date >= date.today()
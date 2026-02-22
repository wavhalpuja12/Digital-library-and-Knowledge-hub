from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from django.utils import timezone



# ---------------- CATEGORY MODEL ----------------
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     parent = models.ForeignKey(
#     'self',
#     on_delete=models.CASCADE,
#     blank=True,
#     null=True,
#     related_name='subcategories'  # now prefetch_related('subcategories') works
# )


#     def _str_(self):
#         return self.name
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    choices= (
        ('navbar', 'Navbar'),
        ('home', 'Home Page'),
    )
    show_in = models.CharField(max_length=10, choices=choices, default='home')

    def _str_(self):
        return self.name

# ---------------- BOOK MODEL ----------------
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    book_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)
    is_availible = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, related_name='liked_books', blank=True)
    is_premium = models.BooleanField(default=False) 

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='books'
    )

    def _str_(self):
        return self.title


# ---------------- BORROW RECORD MODEL ----------------
class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=7)
        super().save(*args, **kwargs)

    def _str_(self):
        return f"{self.user.username} borrowed {self.book.title}"


# ---------------- PREMIUM MODEL ----------------
class Premium(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        return self.expiry_date >= timezone.now().date()
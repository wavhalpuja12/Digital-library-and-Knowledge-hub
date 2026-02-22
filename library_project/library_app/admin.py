from django.contrib import admin
from .models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_premium')
    list_filter = ('is_premium', 'category')


admin.site.register(Category)
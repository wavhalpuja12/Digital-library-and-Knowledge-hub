from .models import Book, Category

def navbar_categories(request):

    return {

        'navbar_categories': Category.objects.filter(
            show_in='navbar',
            parent=None
        )

    }
def premium_books(request):
    return {
        'premium_books': Book.objects.filter(is_premium=True).order_by('-id')[:5]
    }
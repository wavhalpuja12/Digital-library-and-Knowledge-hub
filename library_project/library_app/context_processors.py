from .models import Category

def navbar_categories(request):

    return {

        'navbar_categories': Category.objects.filter(
            show_in='navbar',
            parent=None
        )

    }
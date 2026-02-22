from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('contact/', views.contact, name='contact'),
    path('literature/', views.literature, name='literature'),
    path('poetry/', views.poetry, name='poetry'),
    path('crime-mystery/', views.crime_mystery, name='crime_mystery'),
    path('Sci_fiction/', views.Sci_fiction, name='Sci_fiction'),


    # -------- USER URLs --------
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my_books/', views.my_books, name='my_books'),

    # -------- ADMIN URLs --------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
    path("manage-categories/", views.manage_categories, name="manage_categories"),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),


    # -------- TEMP ADMIN CREATION --------
    # path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('premium-members/', views.premium_members, name='premium_members'),
    path('upgrade-premium/', views.upgrade_premium, name='upgrade_premium'),
    path('activate-premium/', views.activate_premium, name='activate_premium'),
    path('categories/', views.categories, name='categories'),
    path('delete-category/<int:cat_id>', views.delete_category, name='delete_category'),
    path('delete_subcategory/<int:sub_id>', views.delete_subcategory, name='delete_subcategory'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('like/<int:id>/', views.like_book, name='like_book'),
    path('liked-books/', views.liked_books, name='liked_books'),
    path('category/<int:id>/', views.category_books, name='category_books'),
    path('premium-books/', views.premium_books_page, name='premium_books'),
    # path('activate-premium/', views.activate_premium, name='activate_premium'),
    path('payment-success/', views.payment_success, name='payment_success'),
    

    # path('delete-category/<int:id>/', views.delete_category, name='delete_category')


]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),

    # -------- USER URLs --------
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my_books/', views.my_books, name='my_books'),

    # -------- ADMIN URLs --------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),


    # -------- TEMP ADMIN CREATION --------
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('premium-members/', views.premium_members, name='premium_members'),
    path('upgrade-premium/', views.upgrade_premium, name='upgrade_premium'),
    path('activate-premium/', views.activate_premium, name='activate_premium'),
    path('categories/', views.categories, name='categories'),
    path('add-category/', views.add_category, name='add_category'),



]

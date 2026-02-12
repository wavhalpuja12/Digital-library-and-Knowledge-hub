from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # -------- USER URLs --------
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my_books/', views.my_books, name='my_books'),

    # -------- ADMIN URLs --------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-book/', views.add_book, name='add_book'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),

    # -------- AUTH URLs --------
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # -------- TEMP ADMIN CREATION --------
    # path("create-admin/", views.create_admin, name="create_admin"),

    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('premium-members/', views.premium_members, name='premium_members'),
    path('upgrade-premium/', views.upgrade_premium, name='upgrade_premium'),
    path('activate-premium/', views.activate_premium, name='activate_premium'),


]

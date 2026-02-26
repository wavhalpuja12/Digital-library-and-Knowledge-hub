from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('contact/', views.contact, name='contact'),


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
    path('search/', views.search_books, name='search_books'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('history/', views.history, name='history'),
    path('clear-history/', views.clear_history, name='clear_history'),
    path('remove-history/<int:id>/', views.remove_history, name='remove_history'),
    path('update-reading-time/<int:book_id>/', views.update_reading_time, name='update_reading_time'),
    
    # path('delete-category/<int:id>/', views.delete_category, name='delete_category')

    #blog pages
    path('blog_contend/',views.blog_contend,name='blog_contend'),
    path('blog_galaxy/',views.blog_galaxy,name='blog_galaxy'),

    #FAQ's Page

    path('faq/',views.faq,name='faq'),
   

]
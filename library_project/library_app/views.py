from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, BorrowRecord, Premium , Category
from django.db.models import Count
from django.db.models import Q


# ---------- HOME (SHOW ALL BOOKS WITHOUT LOGIN) ----------

def user_home(request):

    navbar_categories = Category.objects.filter(show_in='navbar', parent=None)

    home_categories = Category.objects.filter(show_in='home', parent=None).prefetch_related('books')

    context = {

        'navbar_categories': navbar_categories,

        'home_categories': home_categories

    }

    return render(request, 'user_home.html', context)

# 
def category_books(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = Book.objects.filter(category=category)

    return render(request, 'category_books.html', {
        'category': category,
        'books': books
    })

# ---------- BORROW BOOK ----------
@login_required(login_url='login')
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.is_availible:
        book.is_availible = False
        book.save()

        BorrowRecord.objects.create(
            user=request.user,
            book=book
        )

        messages.success(request, "Book borrowed successfully!")
    else:
        messages.error(request, "Book is not available.")

    return redirect('user_home')


# ---------- RETURN BOOK ----------
@login_required(login_url='login')
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    book = record.book

    book.is_availible = True
    book.save()

    record.delete()
    messages.success(request, "Book returned successfully!")

    return redirect('my_books')


# ---------- MY BOOKS ----------
@login_required(login_url='login')
def my_books(request):
    records = BorrowRecord.objects.filter(user=request.user)
    return render(request, 'my_books.html', {'records': records})


# ---------- ADMIN DASHBOARD ----------

@login_required(login_url='login')
def admin_dashboard(request):

    # 🔐 Allow only superuser
    if not request.user.is_superuser:
        return redirect('user_home')

    category_id = request.GET.get('category')
    search = request.GET.get('search')

    # ✅ convert category_id to int safely
    if category_id:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            category_id = None

    # 📚 BOOK QUERY
    books = Book.objects.select_related("category").all()

    # FILTER BY CATEGORY
    if category_id:
        books = books.filter(category_id=category_id)

    # SEARCH BY TITLE OR AUTHOR
    if search and search != "None":
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search)
        )

    # 📂 MAIN CATEGORIES + SUBCATEGORIES
    categories = Category.objects.filter(
        parent__isnull=True
    ).prefetch_related("subcategories")

    # 📊 DASHBOARD STATS
    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_availible=True).count()
    issued_books = BorrowRecord.objects.filter(return_date__isnull=True).count()
    total_users = User.objects.count()

    # 👑 PREMIUM SYSTEM
    premium_count = Premium.objects.count()
    normal_users = total_users - premium_count

    chart_labels = ['Premium Members', 'Normal Users']
    chart_data = [premium_count, normal_users]

    # 🕒 RECENT BORROW RECORDS
    records = BorrowRecord.objects.select_related(
        "user", "book"
    ).order_by("-borrowed_at")[:5]

    context = {
        # filters
        "books": books,
        "categories": categories,
        "selected_category": category_id,
        "search_query": search,

        # stats
        "total_books": total_books,
        "available_books": available_books,
        "issued_books": issued_books,
        "total_users": total_users,

        # premium
        "premium_count": premium_count,
        "chart_labels": chart_labels,
        "chart_data": chart_data,

        # recent records
        "records": records,
    }

    return render(request, "admin_dashboard.html", context)

@login_required(login_url='login')
def manage_categories(request):
    if request.method == "POST":
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        show_in = request.POST.get('show_in')

        parent = Category.objects.get(id=parent_id) if parent_id else None

        Category.objects.create(
            name=name,
            parent=parent,
            show_in=show_in
        )

    categories = Category.objects.filter(parent=None)

    return render(request, 'admin/manage_categories.html', {
        'categories': categories
    })

@login_required(login_url='login')
def premium_members(request):

    if not request.user.is_superuser:
        return redirect('home')

    members = Premium.objects.select_related('user').all()
    return render(request, 'premium_members.html', {'members': members})


# ---------- ADD BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def add_book(request):

    if not request.user.is_superuser:
        return redirect('user_home')

    # ✅ Fetch parent categories + subcategories
    categories = Category.objects.filter(
        parent__isnull=True
    ).prefetch_related('subcategories')

    if request.method == "POST":
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        book_pdf = request.FILES.get('book_pdf')
        is_premium = request.POST.get('is_premium') == 'on'

        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        Book.objects.create(
            title=title,
            author=author,
            description=description,
            image=image,
            book_pdf=book_pdf,
            is_premium=is_premium,
            category=category  # ✅ SAVE CATEGORY
        )

        messages.success(request, "Book added successfully!")
        return redirect('admin_dashboard')

    # ✅ SEND categories to template
    return render(request, 'add_book.html', {
        'categories': categories
    })



# ---------- DELETE BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def delete_book(request, book_id):

    if not request.user.is_superuser:
        return redirect('user_home')

    book = get_object_or_404(Book, id=book_id)
    book.delete()

    messages.success(request, "Book deleted successfully!")
    return redirect('admin_dashboard')



# ---------- BOOK DETAIL ----------
@login_required(login_url='login')
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)

    if book.is_premium:
        if not Premium.objects.filter(user=request.user).exists():
            messages.warning(request, "⚠ This is a Premium Book. Upgrade to access.")
            return redirect('upgrade_premium')

    return render(request, 'book_detail.html', {'book': book})
# def book_detail(request, id):
#     book = get_object_or_404(Book, id=id)
#     return render(request, 'books/book_detail.html', {'book': book})

def like_book(request, id):
    book = get_object_or_404(Book, id=id)
    
    # simple like logic (increase count)
    book.likes = book.likes + 1
    book.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))
def like_book(request, id):
    book = get_object_or_404(Book, id=id)

    if request.user.is_authenticated:
        book.liked_by.add(request.user)

    return redirect('liked_books')
@login_required
def like_book(request, id):
    book = get_object_or_404(Book, id=id)

    if request.user in book.liked_by.all():
        book.liked_by.remove(request.user)   # 👈 UNLIKE
    else:
        book.liked_by.add(request.user)      # 👈 LIKE

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login')
def liked_books(request):

    books = request.user.liked_books.all()

    return render(request, 'liked_books.html', {'books': books})

@login_required(login_url='login')
def upgrade_premium(request):
    return render(request, 'upgrade_premium.html')

@login_required(login_url='login')
def activate_premium(request):
    # Create premium record for user
    Premium.objects.get_or_create(user=request.user)

    messages.success(request, "🎉 Premium Activated Successfully!")
    return redirect('home')


def categories(request):
    return render(request, 'categories.html')

# -------------------Delete main Categories ---------------
# @login_required(login_url='login')
# def delete_category(request, id):

#     if not request.user.is_superuser:
#         return redirect('user_home')

#     category = get_object_or_404(Category, id=id)
#     category.delete()

#     messages.success(request, "Category deleted successfully!")
#     return redirect('manage_categories')

@login_required(login_url='login')
def delete_category(request, cat_id):

    if not request.user.is_superuser:
        return redirect('user_home')

    category = get_object_or_404(Category, id=cat_id)
    category.delete()

    messages.success(request, "Category deleted successfully!")
    return redirect('manage_categories')

@login_required(login_url='login')
def delete_subcategory(request,sub_id):

    if not request.user.is_superuser:
        return redirect('user_home')

    sub_cat = get_object_or_404(Category, id=sub_id)
    sub_cat.delete()

    messages.success(request, "Category deleted successfully!")
    return redirect('manage_categories')

def contact(request):
    return render(request, 'contact.html')

def literature(request):
    return render(request, 'Literature.html')

def poetry(request):
    return render(request, 'poetry.html')

def crime_mystery(request):
    return render(request, 'crime_mystery.html')

def Sci_fiction(request):
    return render(request, 'Science-Fiction & Fantasy.html')

def category_books(request, id):
    category = Category.objects.get(id=id)
    books = category.books.all()

    return render(request, 'category_books.html', {
        'category': category,
        'books': books
    })

@login_required(login_url='login')
def manage_categories(request):

    if request.method == "POST":

        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        show_in = request.POST.get('show_in')

        parent = Category.objects.get(id=parent_id) if parent_id else None

        Category.objects.create(
            name=name,
            parent_id=parent if parent else None,
            show_in=show_in
        )

    categories = Category.objects.filter(parent=None)

    return render(request, 'manage_categories.html', {
        'categories': categories
    })
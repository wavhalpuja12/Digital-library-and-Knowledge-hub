from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, BorrowRecord, Premium, Category
from django.db.models import Count


# ---------- HOME (SHOW ALL BOOKS WITHOUT LOGIN) ----------
def user_home(request):
    categories = Category.objects.prefetch_related('books').all()

    return render(request, 'user_home.html', {
        'categories': categories
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

    return redirect('home')


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

    if not request.user.is_superuser:
        return redirect('home')

    books = Book.objects.all()
    records = BorrowRecord.objects.all()

    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_availible=True).count()
    total_users = User.objects.count()

    # ✅ Premium System
    premium_count = Premium.objects.count()
    normal_users = total_users - premium_count

    # ✅ Updated Chart Data (Premium vs Normal Users)
    chart_labels = ['Premium Members', 'Normal Users']
    chart_data = [premium_count, normal_users]

    context = {
        'books': books,
        'records': records,
        'total_books': total_books,
        'available_books': available_books,
        'total_users': total_users,
        'premium_count': premium_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'admin_dashboard.html', context)


# ---------- PREMIUM MEMBERS LIST ----------
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
        return redirect('home')

    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        description = request.POST.get('description')
        image = request.FILES.get('image')
        book_pdf = request.FILES.get('book_pdf')
        category_id = request.POST.get('category')
        is_premium = request.POST.get('is_premium') == 'on'

        category = Category.objects.get(id=category_id)

        Book.objects.create(
            title=title,
            author=author,
            description=description,
            image=image,
            book_pdf=book_pdf,
            category=category,
            is_premium=is_premium
        )

        messages.success(request, "Book added successfully!")
        return redirect('admin_dashboard')

    return render(request, 'add_book.html', {'categories': categories})


# ---------- DELETE BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def delete_book(request, book_id):

    if not request.user.is_superuser:
        return redirect('home')

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

@login_required(login_url='login')
def add_category(request):

    if not request.user.is_superuser:
        return redirect('home')

    if request.method == "POST":
        name = request.POST.get('name')

        if not Category.objects.filter(name=name).exists():
            Category.objects.create(name=name)
            messages.success(request, "Category added successfully!")
        else:
            messages.error(request, "Category already exists!")

        return redirect('add_category')

    categories = Category.objects.all()
    return render(request, 'add_category.html', {'categories': categories})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, BorrowRecord, Premium
from django.db.models import Count


# ---------- HOME (SHOW ALL BOOKS WITHOUT LOGIN) ----------
def home(request):
    query = request.GET.get('q')

    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()

    context = {
        'books': books
    }

    if request.user.is_authenticated and request.user.is_superuser:
        context['total_books'] = Book.objects.count()
        context['total_records'] = BorrowRecord.objects.count()

    return render(request, 'home.html', context)


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

    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        description = request.POST.get('description')
        image = request.FILES.get('image')
        book_pdf = request.FILES.get('book_pdf')
        is_premium = request.POST.get('is_premium') == 'on'

        Book.objects.create(
            title=title,
            author=author,
            description=description,
            image=image,
            book_pdf=book_pdf,
            is_premium=is_premium
        )

        messages.success(request, "Book added successfully!")
        return redirect('admin_dashboard')

    return render(request, 'add_book.html')



# ---------- DELETE BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def delete_book(request, book_id):

    if not request.user.is_superuser:
        return redirect('home')

    book = get_object_or_404(Book, id=book_id)
    book.delete()

    messages.success(request, "Book deleted successfully!")
    return redirect('admin_dashboard')


# ---------- SIGNUP ----------
def signup_view(request):

    if request.method == "POST":
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        password2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'signup.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('/login/?signup=1')

    return render(request, 'signup.html')


# ---------- LOGIN ----------
def login_view(request):

    next_url = request.GET.get('next')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if next_url:
                return redirect(next_url)

            if user.is_superuser:
                return redirect('admin_dashboard')

            return redirect('home')

        else:
            messages.error(request, "Invalid username or password.")

    signup_success = request.GET.get('signup')
    if signup_success:
        messages.success(request, "Account created successfully! Please login.")

    return render(request, 'login.html')


# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect('home')


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



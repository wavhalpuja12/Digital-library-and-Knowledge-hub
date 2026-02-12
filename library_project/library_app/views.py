from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Book, BorrowRecord
from django.contrib import messages
from .models import Book

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

    # Extra info for admin
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

    return redirect('home')


# ---------- RETURN BOOK ----------
@login_required(login_url='login')
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    book = record.book

    book.is_availible = True
    book.save()

    record.delete()
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

    return render(request, 'admin_dashboard.html', {
        'books': books,
        'records': records
    })


# ---------- ADD BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def add_book(request):
    # Only allow admin users
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == "POST":
        title = request.POST['title']
        author = request.POST['author']
        description = request.POST.get('description')
        image = request.FILES.get('image')
        book_pdf = request.FILES.get('book_pdf')

        # Create new book
        Book.objects.create(
            title=title,
            author=author,
            description=description,
            image=image,
            book_pdf=book_pdf
        )

        return redirect('admin_dashboard')

    return render(request, 'add_book.html')


# ---------- DELETE BOOK (ADMIN ONLY) ----------
@login_required(login_url='login')
def delete_book(request, book_id):
    if not request.user.is_superuser:
        return redirect('home')

    book = get_object_or_404(Book, id=book_id)
    book.delete()

    return redirect('admin_dashboard')


# ---------- SIGNUP ----------
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'signup.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use another email.")
            return render(request, 'signup.html')

        # Check if passwords match
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

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

            # Redirect to the page user came from
            if next_url:
                return redirect(next_url)

            # Admin redirect
            if user.is_superuser:
                return redirect('admin_dashboard')

            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    # Check if redirected from signup
    signup_success = request.GET.get('signup')
    if signup_success:
        messages.success(request, "Account created successfully! Please login.")

    return render(request, 'login.html')

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect('home')


# ---------- CREATE ADMIN (RUN ONCE) ----------
def create_admin(request):
    User.objects.create_superuser(
        username="admin",
        password="admin123"
    )
    return redirect('login')


# ---------- BOOK DETAIL (LOGIN REQUIRED) ----------
@login_required(login_url='login')
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_detail.html', {'book': book})

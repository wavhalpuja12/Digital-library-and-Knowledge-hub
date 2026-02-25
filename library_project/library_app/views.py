from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, BookHistory, BorrowRecord, Premium , Category
from django.db.models import Count
from django.db.models import Q
import razorpay
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
    
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import redirect
from .models import Premium

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
import razorpay
from django.conf import settings

from .models import NewsletterSubscriber
from .models import Subscriber



# ---------- HOME (SHOW ALL BOOKS WITHOUT LOGIN) ----------

def user_home(request):

    navbar_categories = Category.objects.filter(show_in='navbar', parent=None)

    home_categories = Category.objects.filter(show_in='home', parent=None).prefetch_related('books')
    # premium_books = Book.objects.filter(is_premium=True)

    context = {

        'navbar_categories': navbar_categories,

        'home_categories': home_categories,
        # 'premium_books': premium_books,

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

def book_detail(request, id):
    book = get_object_or_404(Book, id=id)

    # 🔥 Allow admin to access all books
    if request.user.is_superuser:
        return render(request, "book_detail.html", {"book": book})

    # 🔐 Premium check
    if book.is_premium:
        if not request.user.is_authenticated:
            return redirect("login")

        try:
            premium = Premium.objects.get(user=request.user)

            if premium.expiry_date < timezone.now().date():
                return redirect("upgrade_premium")

        except Premium.DoesNotExist:
            return redirect("upgrade_premium")

    # ✅ SAVE HISTORY (FOR ALL BOOKS)
    if request.user.is_authenticated:
        BookHistory.objects.update_or_create(
            user=request.user,
            book=book
        )

    return render(request, "book_detail.html", {"book": book})
def history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    history = BookHistory.objects.filter(user=request.user).order_by('-viewed_at')

    # Convert seconds → minutes
    for item in history:
        item.minutes = item.reading_time // 60

    # Continue reading (latest book)
    continue_book = history.first().book if history else None

    return render(request, 'history.html', {
        'history': history,
        'continue_book': continue_book
    })

def clear_history(request):
    if request.user.is_authenticated:
        BookHistory.objects.filter(user=request.user).delete()
    return redirect('history')

def remove_history(request, id):
    if request.user.is_authenticated:
        BookHistory.objects.filter(user=request.user, id=id).delete()
    return redirect('history')

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
    
def premium_books_page(request):
    premium_books = Book.objects.filter(is_premium=True)

    return render(request, 'premium_book.html', {
        'premium_books': premium_books
    })
    


@login_required(login_url='login')
def activate_premium(request):

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    order = client.order.create({
        "amount": 9900,
        "currency": "INR"
    })

    # 🔥 STORE ORDER ID IN SESSION
    request.session['razorpay_order_id'] = order['id']

    return render(request, "payment.html", {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })


@csrf_exempt
@login_required(login_url='login')
def payment_success(request):

    if request.method == "POST":

        try:
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))

            stored_order_id = request.session.get('razorpay_order_id')

            if not stored_order_id:
                return HttpResponse("Order session expired. Please try again.")

            params_dict = {
                'razorpay_order_id': stored_order_id,
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }

            client.utility.verify_payment_signature(params_dict)

            # ✅ Activate Premium
            expiry_date = timezone.now().date() + timedelta(days=30)

            Premium.objects.update_or_create(
                user=request.user,
                defaults={"expiry_date": expiry_date}
            )

            # ✅ Send Email
            send_mail(
                subject="🎉 Premium Membership Activated - Digital Library",
                message=f"""
Hello {request.user.username},

Your payment was successful!

Your Premium Membership is now active.

🗓 Valid Until: {expiry_date}

You now have full access to all premium books.

Thank you for choosing Digital Library 📚

Happy Reading!
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            # Clear session
            del request.session['razorpay_order_id']

            return redirect("user_home")

        except Exception as e:
            return HttpResponse(f"Payment verification failed: {str(e)}")

    return HttpResponse("Invalid request")



def search_books(request):
    query = request.GET.get('q')

    if not query:
        return redirect('user_home')

    book = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    ).first()

    if book:
        return redirect('book_detail', id=book.id)
    else:
        messages.error(request, f'❌ "{query}" book is not available')
        return redirect('user_home')



def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"""
        New Contact Message

        Name: {name}
        Email: {email}

        Message:
        {message}
        """

        try:
            send_mail(
                subject=f"New Contact Message from {name}",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  # 👈 admin email
                fail_silently=False,
            )

            messages.success(request, "✅ Message sent successfully!")
        except Exception as e:
            messages.error(request, "❌ Failed to send message")

    return render(request, 'contact.html')



def subscribe_newsletter(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.warning(request, "⚠️ Email already subscribed!")
        else:
            NewsletterSubscriber.objects.create(email=email)
            messages.success(request, "✅ Subscribed successfully!")

    return redirect(request.META.get('HTTP_REFERER', 'user_home'))


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if not Subscriber.objects.filter(email=email).exists():
            Subscriber.objects.create(email=email)

            # Send welcome email
            send_mail(
                'Subscription Successful',
                'Thank you for subscribing to our book updates!',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        return redirect('user_home')
    
def unsubscribe(request, email):
    try:
        user = Subscriber.objects.get(email=email)
        user.is_active = False
        user.save()
        messages.success(request, "You have been unsubscribed successfully.")
    except Subscriber.DoesNotExist:
        messages.error(request, "Email not found.")

    return redirect('user_home')   # redirect to homepage

def update_reading_time(request, book_id):
    if request.method == "POST" and request.user.is_authenticated:
        time_spent = int(request.POST.get("time", 0))

        history = BookHistory.objects.filter(user=request.user, book_id=book_id).first()

        if history:
            history.reading_time += time_spent
            history.save()

    return HttpResponse(status=204)

def blog_contend(request):
    return render(request,'blog.html')

def blog_galaxy(request):
    return render(request,'blog2.html')

def faq(request):
    return render(request,'faq.html')


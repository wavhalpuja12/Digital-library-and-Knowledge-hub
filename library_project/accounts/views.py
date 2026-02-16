from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# ---------- SIGNUP ----------

def signup_view(request):
    if request.method == 'POST':
        # Get form data safely
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password2')  # Make sure your HTML input has name="password2"

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'signup.html')

        # Check if email is already taken
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'signup.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('/accounts/login/')

    # If GET request, just render the signup form
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

            return redirect('user_home')

        else:
            messages.error(request, "Invalid username or password.")

    signup_success = request.GET.get('signup')
    if signup_success:
        messages.success(request, "Account created successfully! Please login.")

    return render(request, 'login.html')

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect('user_home')




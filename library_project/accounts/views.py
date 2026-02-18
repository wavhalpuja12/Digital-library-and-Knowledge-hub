from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# ---------- SIGNUP ----------

def signup_view(request):

    if request.method == "POST":
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        password2 = request.POST['password2']

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'signup.html')

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'signup.html')

        # Password match check
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('/accounts/login/')

    return render(request, 'signup.html')

# def signup_view(request): 



# ---------- LOGIN ----------
# def login_view(request):

#     next_url = request.GET.get('next')

#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)

#         if user:
#             login(request, user)

#             if next_url:
#                 return redirect(next_url)

#             if user.is_superuser:
#                 return redirect('admin_dashboard')

#             return redirect('home')

#         else:
#             messages.error(request, "Invalid username or password.")

#     signup_success = request.GET.get('signup')
#     if signup_success:
#         messages.success(request, "Account created successfully! Please login.")

#     return render(request, 'login.html')

# def login_view(request):
#     if request.method == "POST":
#         us = request.POST.get("username")
#         pw = request.POST.get("Password")

#         try:
#             user = User.objects.get(username=us)
#         except User.DoesNotExist:
#             return render (request ,'login.html',{"error": " User is Not Found.. Please try Again..!"})
#         user = authenticate(request,username=us,passwod=pw)
#         if user is not None:
#             login(request,user)
#             return redirect("user_home")
#         else:
#             return render(request,'login.html',{"error":"inavalid User name.....!" })
#     else:
#         return render (request,'login.html')  
# 
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user_home')   # 👈 change this to your home URL name
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html") 

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect('user_home')




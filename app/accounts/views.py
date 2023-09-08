from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .forms import RegisterUserForm
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_email_verification import send_email, verify_view, verify_token
from django.contrib.auth.models import User

# Create your views here.
def help(request):
    if request.method == "GET":
        return render(request, 'accounts/help.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # form = CaptchaForm(request.POST)
        # if not form.is_valid():
        #     messages.error(request, ("Invalid captcha sign-up."))
        #     return redirect(reverse_lazy('signin'))
        
        is_active_user = User.objects.all().filter(username=username)
        if len(is_active_user) == 1:
            for user in is_active_user:
                check_pass = user.check_password(password)
                if not user.is_active and check_pass:
                    print(user.is_active)
                    send_email(user)
                    messages.success(request, ("Please verify your email."))
                    return redirect(reverse_lazy('signin'))

        user = authenticate(request, username=username, password=password)

                
        if user is None:
            messages.success(request, ("Invalid email or password."))
        
            return redirect(reverse_lazy('signin'))

        is_active_user = User.objects.get(username=username)



        login(request, user)
        return redirect(reverse_lazy('home'))
        

        




    else:
        # context = {"form" : CaptchaForm}
        return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('home'))

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():

            user = form.save()
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # user = authenticate(username=username, password=password)
            # login (request, user)
            user.is_active = False  # Example
            send_email(user)
            messages.success(request, ("Registration successful. Please verify your email."))
            return redirect(reverse_lazy('signin'))
        messages.error(request, "Unsuccessful registration. Invalid information.")
        return render(request, 'accounts/signup.html', {'form':form})
    else:
        form = RegisterUserForm()
        return render(request, 'accounts/signup.html', {'form':form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('change_password')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

def confirm(request, token):
    success, user = verify_token(token)
    return HttpResponse(f'Account verified, {user.username}' if success else 'Invalid token')

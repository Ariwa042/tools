from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, DepositForm, SpendForm, EmailAuthenticationForm
from .models import UserProfile, Deposit, Spend, Transactions
from django.db.models import Sum
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('account:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'account/register.html', {'form': form})


# User login view
from django.contrib.auth.forms import AuthenticationForm
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('account:profile')  # Redirect to your dashboard or home page
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'account/login.html', {'form': form})



# User logout view
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('account:login')


# User profile view
@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    total_deposits = Deposit.objects.filter(user=request.user, status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent = Spend.objects.filter(user=request.user, status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0
    transactions = Transactions.objects.filter(user=request.user)

    context = {
        'user_profile': user_profile,
        'total_deposits': total_deposits,
        'total_spent': total_spent,
        'transactions': transactions,
    }
    return render(request, 'account/profile.html', context)


# Deposit view
@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.status = 'PENDING'
            deposit.save()
            Transactions.objects.create(
                user=request.user,
                type='DEPOSIT',
                amount=deposit.amount,
                status='PENDING'
            )
            messages.success(request, 'Deposit created, pending approval.')
            return redirect('account:profile')
    else:
        form = DepositForm()

    return render(request, 'account/deposit.html', {'form': form})


# Spend view
@login_required
def spend(request):
    if request.method == 'POST':
        form = SpendForm(request.POST)
        if form.is_valid():
            spend = form.save(commit=False)
            user_profile = UserProfile.objects.get(user=request.user)

            if user_profile.xp_balance >= float(spend.amount):
                spend.user = request.user
                spend.status = 'PENDING'
                spend.save()
                Transactions.objects.create(
                    user=request.user,
                    type='SPENT',
                    amount=spend.amount,
                    status='PENDING'
                )
                messages.success(request, 'Payment initiated, pending approval.')
            else:
                messages.error(request, 'Insufficient XP balance.')

            return redirect('account:profile')
    else:
        form = SpendForm()

    return render(request, 'account/spend.html', {'form': form})


# Transaction history view
@login_required
def transaction_history(request):
    transactions = Transactions.objects.filter(user=request.user)

    context = {
        'transactions': transactions
    }
    return render(request, 'account/transactions.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account/change_password.html', {'form': form})
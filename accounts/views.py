from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify

from orders.models import Order
from vendor.forms import VendorForm
from vendor.models import Vendor
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test

from .utils import detectUser


# Restrict restaurant from accessing customer page
def check_role_restaurant(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict customer from accessing Restaurant page

def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


# Create your views here.

def registerUser(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in !')
        return redirect('custDashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.role = User.CUSTOMER
            user.set_password(password)
            user.save()

            # send verification email
            # send_verification_email(request, user)

            messages.success(request, "Your account has been created !")
            return redirect('registerUser')
        else:
            print(form.errors)


    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in !')
        return redirect('restDashboard')
    elif request.method == 'POST':
        # store data and create user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            contact = form.cleaned_data['contact']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, contact=contact,
                                            password=password, username=username)
            user.role = User.RESTAURANT
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification email
            # send_verification_email(request, user)

            messages.success(request, "Your account has been created ! Please wait for approval.")
            return redirect('registerVendor')
        else:
            print('Invalid Form')
            print(form.errors)

    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, 'accounts/registerVendor.html', context)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status
    return


def login(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in !')
        return redirect('dashboard')

    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "User Logged In Successfully !!")
            print(user.username)
            return redirect('myAccount')

        else:
            messages.error(request, "Incorrect email or password.")
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are now logged out !')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    # orders = Order.objects.filter(user=request.user, is_ordered=True)
    # context = {
    #     'orders': orders,
    # }
    # return render(request, 'accounts/custDashboard.html',context)
    user_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        '-created_at')
    recent_orders = user_orders[:5]

    context = {
        'user_orders':user_orders,
        'recent_orders':recent_orders,
    }
    return render(request, 'accounts/custDashboard.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def restDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    current_date = datetime.now()

    # Filtering orders based on the restaurant and that the order has been placed (is_ordered=True)
    orders = Order.objects.filter(vendors=vendor, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    total_orders = orders.count
    total_revenue = Order.objects.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    current_month_revenue = Order.objects.filter(
        vendors=vendor,
        is_ordered=True,
        created_at__year=current_date.year,
        created_at__month=current_date.month
    ).aggregate(Sum('total'))['total__sum'] or 0
    context = {
        'orders': orders,
        'recent_orders': recent_orders,
        'total_orders' : total_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/restDashboard.html', context)

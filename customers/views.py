from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from accounts.views import check_role_customer
from orders.models import Order, OrderedFood


# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)


def myorders(request):
    user_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        '-created_at')
    context = {
        'orders': user_orders,
    }
    return render(request, "customers/myorders.html", context)


def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        context = {
            'order': order,
            'ordered_food': ordered_food,
        }
    except:
        return redirect('customer')

    return render(request, "customers/order_detail.html", context)

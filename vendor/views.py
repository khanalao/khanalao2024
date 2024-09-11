from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_restaurant
from menu.forms import CategoryForm, FoodForm
from menu.models import Category, FoodItem
from .forms import VendorForm
from vendor.models import Vendor
from django.contrib.auth.decorators import login_required, user_passes_test


def get_rest(request):
    rest = Vendor.objects.get(user=request.user)
    return rest


# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def rprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        rest_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and rest_form.is_valid():
            profile_form.save()
            rest_form.save()
            messages.success(request, 'Profile Updated !')
            return redirect('rprofile')
        else:
            print(profile_form.errors)
            print(rest_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        rest_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'rest_form': rest_form
    }
    return render(request, 'restaurant/rprofile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def menu_builder(request):
    rest = get_rest(request)
    cat = Category.objects.filter(rest=rest).order_by('created_at')

    context = {
        'cat': cat,
    }
    return render(request, 'restaurant/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def foodItems_by_category(request, pk=None):
    rest = get_rest(request)
    cat = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(rest=rest, category=cat)

    context = {
        'fooditems': fooditems,
        'cat': cat
    }

    return render(request, 'restaurant/foodItems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat_name = form.cleaned_data['cat_name']
            category = form.save(commit=False)
            category.rest = get_rest(request)
            category.slug = slugify(cat_name)
            form.save()
            messages.success(request, "Category Added Successfully")
            return redirect('menu_builder')
        else:
            form.errors
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return render(request, 'restaurant/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def edit_category(request, pk=None):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            cat_name = form.cleaned_data['cat_name']
            category = form.save(commit=False)
            category.rest = get_rest(request)
            category.slug = slugify(cat_name)
            form.save()
            messages.success(request, "Category Updated Successfully")
            return redirect('menu_builder')
        else:
            form.errors
    else:
        form = CategoryForm(instance=cat)

    context = {
        'form': form,
        'cat': cat
    }
    return render(request, 'restaurant/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def delete_category(request, pk=None):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    messages.success(request, 'Category Deleted Successfully !')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.rest = get_rest(request)
            food.slug = slugify(food_title)
            form.save()
            messages.success(request, "Food Item Added Successfully")
            return redirect('foodItems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodForm()

        # modify form
        form.fields['category'].queryset = Category.objects.filter(rest=get_rest(request))

    context = {
        'form': form,
    }
    return render(request, 'restaurant/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            foods = form.save(commit=False)
            foods.rest = get_rest(request)
            foods.slug = slugify(food_title)
            form.save()
            messages.success(request, "Food Item Updated Successfully")
            return redirect('foodItems_by_category', food.category.id)
        else:
            form.errors
    else:
        form = FoodForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(rest=get_rest(request))

    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'restaurant/edit_food.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item Deleted Successfully !')
    return redirect('foodItems_by_category', food.category.id)

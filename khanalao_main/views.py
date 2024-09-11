from django.shortcuts import render
from django.http import HttpResponse

from menu.models import FoodItem, Category
from vendor.models import Vendor


def home(request):
    rest = Vendor.objects.filter(is_approved=True, user__is_active=True)
    food = Category.objects.all()
    context = {
        'rest': rest,
        'food': food,
    }
    return render(request, 'home.html', context)

import razorpay as razorpay
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from accounts.models import UserProfile
from khanalao_main import settings
from marketplace.context_processor import get_cart_counter, get_cart_amounts
from marketplace.models import Cart
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from orders.models import Payment, Order, OrderedFood
from vendor.models import Vendor
from decimal import Decimal
from django.db.models import Sum  # Add this line




# Create your views here.


@login_required(login_url='login')
def marketplace(request):
    rest = Vendor.objects.filter(is_approved=True, user__is_active=True)
    rest_count = rest.count()
    context = {
        'rest': rest,
        'rest_count': rest_count,
    }
    return render(request, 'marketplace/listings.html', context)


def rest_details(request, vendor_slug):
    rest = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    cat = Category.objects.filter(rest=rest).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    item = get_list_or_404(FoodItem)
    menu_items = rest.fooditem_set.all()

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'rest': rest,
        'cat': cat,
        'menu_items': menu_items,
    }
    return render(request, 'marketplace/rest_details.html', context)


# def add_to_cart(request, food_id=None):
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             try:
#                 fooditem = FoodItem.objects.get(id=food_id)
#                 # check if user has already added that food to the cart
#                 try:
#                     chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
#                     # Increase the cart quantity
#                     chkCart.quantity += 1
#                     chkCart.save()
#                     return JsonResponse({'status': 'Success', 'message': 'Food Item added to cart.'})
#                 except:
#                     chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
#                     return JsonResponse({'status': 'Success', 'message': 'Food Item added to cart.'})
#
#             except:
#                 return JsonResponse({'status': 'Success', 'message': 'This food does not exists! '})
#         else:
#             return JsonResponse({'status': 'Success', 'message': 'Invalid Request'})
#     else:
#         return JsonResponse({'status': 'Failed', 'message': 'Please log in to continue.'})

# def add_to_cart(request, food_id=None):
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             # Check if the food item exists
#             try:
#                 fooditem = FoodItem.objects.get(id=food_id)
#                 # Check if the user has already added that food to the cart
#                 try:
#                     chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
#                     # Increase the cart quantity
#                     chkCart.quantity += 1
#                     chkCart.save()
#                     return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity',
#                                          'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,
#                                          'cart_amount': get_cart_amounts(request)})
#                 except:
#                     chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
#                     return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart',
#                                          'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,
#                                          'cart_amount': get_cart_amounts(request)})
#             except:
#                 return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
#         else:
#             return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
#
#     else:
#         return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                except Cart.DoesNotExist:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)

                # Calculate the updated cart count
                cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
                print(cart_count)

                # messages.success(request, f"{fooditem.food_title} has been added to your cart!")
                return JsonResponse(
                    {'status': 'Success', 'message': 'Food Item added to cart.', 'cart_count': cart_count})

            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Please log in to continue.'})


@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    context = {
        'cart_items': cart_items
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # check if cart Item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Item successfully deleted',
                                         'cart_counter': get_cart_counter(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exists'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})



def checkout(request):
    user_profile = UserProfile.objects.get(user=request.user)
    default = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone':request.user.contact,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pincode
    }
    form = OrderForm(initial=default)
    cart_items = Cart.objects.filter(user=request.user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)


def process_payment(request):
    if request.method == 'POST':
        # Example values, replace these with actual values from your request or database
        subtotal = Decimal(request.POST.get('subtotal', '0.00'))
        delivery_charge = Decimal('25.00')  # Example delivery charge

        tax_rate = Decimal('0.10')  # Assuming 10% tax
        tax = subtotal * tax_rate  # Calculate tax as a Decimal

        total_amount = subtotal + tax + delivery_charge  # Sum up all amounts as Decimals

        client = razorpay.Client(auth=('your_razorpay_key', 'your_razorpay_secret'))
        payment = client.order.create({
            'amount': int(total_amount * 100),  # Amount should be in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        order = Order.objects.create(
            user=request.user,
            order_number=payment['id'],
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            country=request.POST.get('country'),
            pin_code=request.POST.get('pin_code'),
            total=total_amount,
            tax_data={'GST': {'tax_percentage': '10%', 'tax_amount': str(tax)}},
            total_tax=tax,
            payment_method='RazorPay',
            status='New',
            is_ordered=False
        )

        context = {
            'subtotal': subtotal,
            'tax': tax,
            'delivery_charge': delivery_charge,
            'total_amount': total_amount,
            'order_id': payment['id'],
            'user': request.user
        }

        return render(request, 'process_payment.html', context)

    return render(request, 'marketplace/checkout.html')

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')

    payment = get_object_or_404(Payment, transaction_id=order_id)
    payment.status = 'Completed'
    payment.save()

    order = get_object_or_404(Order, payment=payment)
    order.is_ordered = True
    order.status = 'Accepted'
    order.save()

    return render(request, 'payment_success.html', {'order': order})


def category_restaurants(request, category_slug):
    categories = Category.objects.filter(slug__icontains=category_slug)
    restaurants = Vendor.objects.filter(category__in=categories, is_approved=True).distinct()

    context = {
        'category': categories,
        'restaurants': restaurants,
    }

    return render(request, 'marketplace/category_restaurants.html', context)
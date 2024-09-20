import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from marketplace.context_processor import get_cart_amounts
from marketplace.models import Cart
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.utils import generate_order_number, generate_transaction_id


# Create your views here.

def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []

    for i in cart_items:
        if i.fooditem.rest.id not in vendors_ids:
            vendors_ids.append(i.fooditem.rest.id)

    cart_amounts = get_cart_amounts(request)
    subtotal = cart_amounts.get('subtotal', 0)
    tax = cart_amounts.get('tax', 0)
    delivery = cart_amounts.get('delivery', 0)
    total = cart_amounts.get('total', 0)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.subtotal = subtotal
            order.tax = tax
            order.delivery = delivery
            order.total = total
            order.payment_method = "COD"
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
            }

            return render(request, 'orders/placeorder.html', context)
        else:
            print(form.errors)  # Debug: Print form errors

    return render(request, 'orders/placeorder.html', {
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery,
        'total': total, }
                  )


# def payment(request):
#     order_number = request.POST.get('order_number')
#     transaction_id = generate_transaction_id()
#     payment_method = 'COD'
#     status = request.POST.get('status')
#
#     order = Order.objects.get(user=request.user, order_number=order_number)
#     payment = Payment(
#         transaction_id=transaction_id,
#         payment_method=payment_method,
#         amount=order.total,
#         status=status
#     )
#     payment.save()
#
#     order.payment=payment
#     order.is_ordered=True
#     order.save()

def payment(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = generate_transaction_id()
        payment_method = 'COD'
        status = request.POST.get('status')

        # Retrieve the order by order_number and user
        try:
            order = Order.objects.get(user=request.user, order_number=order_number)
        except Order.DoesNotExist:
            # Handle case where order is not found
            return render(request, 'error_page.html', {'message': 'Order not found.'})

        # Save the payment details
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status
        )
        payment.save()

        # Link the payment to the order and mark it as ordered
        order.payment = payment
        order.is_ordered = True
        order.status = status
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for items in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = items.fooditem
            ordered_food.quantity = items.quantity
            ordered_food.price = items.fooditem.price
            ordered_food.amount = items.fooditem.price * items.quantity
            ordered_food.save()

        cart_items.delete()

        # Redirect to success page
        return redirect('order_complete')  # Assuming you have an 'order_success' page

    return redirect('checkout')  # Redirect if method is not POST


def order_complete(request):
    return render(request, 'orders/order_complete.html', {'message': 'Your order has been successfully placed!'})


def order_complete(request):
        # Retrieve the latest order for the logged-in user
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

        # If no orders are found, redirect to an error page or handle accordingly
    if not orders:
        return render(request, 'error_page.html', {'message': 'No orders found.'})

        # Get the latest order (first in the ordered list)
    latest_order = orders.first()

        # Fetch items associated with the order
    items = OrderedFood.objects.filter(order=latest_order)

    context = {
            'order': latest_order,
            'items': items,
        }
    return render(request, 'orders/order_complete.html', context)
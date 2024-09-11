import json

from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.models import User
from marketplace.context_processor import get_cart_amounts
from marketplace.models import Cart
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderedFood
from orders.utils import generate_order_number

# Create your views here.

def placeorder(request):
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
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
        else:
            print(form.errors)  # Debug: Print form errors

    return render(request, 'orders/placeorder.html', {
        'subtotal': subtotal,
        'tax': tax,
        'delivery': delivery,
        'total': total, }
                  )


def place_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Create the Order entry
        order = Order.objects.create(
            user=User.objects.get(pk=data['user_id']),
            payment=Payment.objects.get(pk=data['payment_id']) if 'payment_id' in data else None,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=data['email'],
            address=data['address'],
            country=data['country'],
            state=data['state'],
            city=data['city'],
            pin_code=data['pin_code'],
            subtotal=data['subtotal'],
            tax=data['tax'],
            delivery=data['delivery'],
            total=data['total'],
            payment_method=data['payment_method'],
            status='New',
        )

        # Create the OrderedFood entries from the Order
        for item in data['items']:  # Assume data['items'] is a list of items
            food_item = FoodItem.objects.get(pk=item['fooditem_id'])
            OrderedFood.objects.create(
                order=order,
                payment=order.payment,
                user=order.user,
                fooditem=food_item,
                quantity=item['quantity'],
                price=item['price'],
                amount=item['quantity'] * item['price'],
            )

        # Mark the order as ordered
        order.is_ordered = True
        order.save()

        # Return a success response
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})
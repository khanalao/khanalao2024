from django.urls import path

from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),

    # cart
    path("cart/", views.cart, name='cart'),

    path('<slug:vendor_slug>/', views.rest_details, name='rest_details'),

    # Add to cart
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),

    # Delete cart Item
    path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),

    path('category/<slug:category_slug>/', views.category_restaurants, name='category_restaurants'),


]

from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('myorders/', views.myorders, name='customer_myorders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]
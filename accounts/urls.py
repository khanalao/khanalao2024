from django.urls import path, include

import vendor
from . import views

urlpatterns = [
    path(',', views.myAccount),
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myAccount/', views.myAccount, name='myAccount'),
    path('custDashboard/', views.custDashboard, name='custDashboard'),
    path('restDashboard/', views.restDashboard, name='restDashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('restaurant/', include('vendor.urls')),
    path('customers/', include('customers.urls')),
]

from django.urls import path
from . import views

urlpatterns = [
    path('placeorder/', views.placeorder, name='placeorder'),
    path('place-order/', views.place_order, name='place_order'),
]

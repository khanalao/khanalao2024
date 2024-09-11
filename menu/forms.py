from django import forms

from menu.models import Category, FoodItem


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['cat_name', 'description']


class FoodForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'price', 'image', 'description', 'is_available']

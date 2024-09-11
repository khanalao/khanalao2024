from django.contrib import admin

from .models import Category, FoodItem


# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('cat_name',)}
    list_display = ('cat_name', 'rest', 'updated_at')
    search_fields = ('cat_name', 'rest__vendor_name')


class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('food_title', 'category', 'price', 'rest', 'is_available', 'updated_at')
    search_fields = ('category__cat_name', 'rest__vendor_name', 'food_title', 'price')
    list_filter = ('is_available', )


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)

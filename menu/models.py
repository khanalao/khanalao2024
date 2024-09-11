from django.db import models

from vendor.models import Vendor


# Create your models here.

class Category(models.Model):
    rest = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    cat_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)  # url for the category is called slug
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def clean(self):
        self.cat_name = self.cat_name.capitalize()

    def __str__(self):
        return self.cat_name


class FoodItem(models.Model):
    rest = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=False)  # url for the category is called slug
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='foodImage')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title

    def clean(self):
        self.food_title = self.food_title.capitalize()

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import OneToOneField



# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, contact, password=None):
        if not email:
            raise ValueError('Enter Email')

        if not username:
            raise ValueError('Enter UserName')

        if not contact:
            raise ValueError('Enter Contact Number')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            contact=contact
        )

        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, first_name, last_name, username, email, contact, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            contact=contact
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    RESTAURANT = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (RESTAURANT, 'Restaurant'),
        (CUSTOMER, 'Customer')
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=70, unique=True)
    contact = models.CharField(max_length=12, unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # authentucation

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'contact']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, object=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_pic = models.ImageField(upload_to='users/cover_pic', blank=True, null=True)
    address_line1 = models.CharField(max_length=50, blank=True, null=True)
    address_line2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=8, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.email




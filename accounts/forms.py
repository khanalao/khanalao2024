from django import forms
from .models import User, UserProfile
from .validations import image_validator


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'contact', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match"
            )


class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn-btn-info'}),
                                      validators=[image_validator])
    cover_pic = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn-btn-info'}),
                                validators=[image_validator])

    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_pic', 'address', 'country', 'state', 'city',
                  'pincode', 'latitude', 'longitude']


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'contact']

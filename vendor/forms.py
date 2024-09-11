from django import forms

from accounts.validations import image_validator
from vendor.models import Vendor


class VendorForm(forms.ModelForm):
    cover_pic = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn-btn-info'}),
                                 validators=[image_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
import os.path

from django.core.exceptions import ValidationError

def image_validator(value):
    ext = os.path.splitext(value.name)[1]
    valid = ['.jpg', '.png', 'jpeg']
    if not ext.lower() in valid:
        raise ValidationError('Unsupported file extension.')
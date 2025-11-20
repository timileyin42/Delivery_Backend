import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Nigerian phone number validator
phone_regex = RegexValidator(
    regex=r'^\+?234?[0-9]{10}$',
    message="Phone number must be in format: '+234XXXXXXXXXX' or '0XXXXXXXXXX'"
)


def validate_nigerian_phone(value):
    """
    Validate Nigerian phone number format.
    """
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', value)
    
    # Check various formats
    patterns = [
        r'^\+234[0-9]{10}$',  # +234XXXXXXXXXX
        r'^234[0-9]{10}$',     # 234XXXXXXXXXX
        r'^0[0-9]{10}$',       # 0XXXXXXXXXX
        r'^[0-9]{10}$',        # XXXXXXXXXX
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            'Enter a valid Nigerian phone number (e.g., +234XXXXXXXXXX or 0XXXXXXXXXX)'
        )


def validate_file_size(value, max_size_mb=5):
    """
    Validate uploaded file size.
    """
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    if value.size > max_size:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB')


def validate_image_file(value):
    """
    Validate that uploaded file is an image.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = value.name.lower().split('.')[-1]
    
    if f'.{ext}' not in valid_extensions:
        raise ValidationError('Only image files are allowed (JPG, PNG, GIF)')

from django.core.exceptions import ValidationError
import re

def validate_bitlocker_key(value):
    """
    Validates that the input is a valid BitLocker recovery key format.
    BitLocker recovery keys are 48 digits, typically grouped in 8 sets of 6 digits.
    """
    # Remove any spaces or hyphens for validation
    clean_value = re.sub(r'[\s-]', '', value)
    
    # Check if it's exactly 48 digits
    if not re.match(r'^\d{48}$', clean_value):
        raise ValidationError(
            'BitLocker key must be 48 digits (typically grouped as 8 sets of 6 digits).'
        )
    
    # Optional: Verify the checksum if BitLocker uses one
    # This would depend on Microsoft's implementation
    return value
from django.utils.crypto import get_random_string

def generate_access_code():
    """Generate a secure 6-character access code using specified character set"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#&'
    return get_random_string(6, chars)

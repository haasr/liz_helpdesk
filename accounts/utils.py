from django.conf import settings as django_settings

def update_email_settings():
    """
    Updates Django's email settings based on the custom Settings model.
    This should be called when SMTP settings change or before sending emails.
    """
    from accounts.models import Settings
    
    db_settings = Settings.objects.first()
    if not db_settings:
        return
    
    if db_settings.smtp_enabled:
        # Update Django's email settings
        django_settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        django_settings.EMAIL_HOST = db_settings.smtp_host
        django_settings.EMAIL_PORT = db_settings.smtp_port
        django_settings.EMAIL_HOST_USER = db_settings.smtp_email
        django_settings.EMAIL_HOST_PASSWORD = db_settings.smtp_password
        django_settings.EMAIL_USE_TLS = db_settings.smtp_use_tls
        django_settings.DEFAULT_FROM_EMAIL = db_settings.smtp_from_email
    else:
        # Fall back to console backend if SMTP is disabled
        django_settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

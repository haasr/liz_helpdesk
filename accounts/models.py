from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        SYSTEM_MANAGER = 'MGR', 'System Manager'
        TECHNICIAN = 'TCH', 'Technician'

    user_type = models.CharField(
        max_length=3,
        choices=UserType.choices,
        default=UserType.TECHNICIAN
    )
    department = models.CharField(max_length=100)

    # Override groups and user_permissions with custom related_names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class SystemManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    departments = models.CharField(max_length=200)  # Comma-separated departments
    technicians = models.ManyToManyField(User, related_name='managed_by')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.job_title}"

class Settings(models.Model):
    ticket_visibility = models.BooleanField(
        default=False,
        help_text="Allow technicians to see all tickets"
    )
    ticket_self_assignment = models.BooleanField(
        default=False,
        help_text="Allow technicians to self-assign tickets"
    )
    asset_visibility = models.BooleanField(
        default=False,
        help_text="Allow technicians to see all assets"
    )
    can_modify_assigned_assets = models.BooleanField(
        default=True,
        help_text="Allow technicians to modify assets linked to their tickets"
    )
    can_modify_all_assets = models.BooleanField(
        default=False,
        help_text="Allow technicians to modify any asset"
    )

    # Notification Preferences
    notify_ticket_created = models.BooleanField(
        default=True,
        help_text="Send notifications for new tickets"
    )
    notify_status_changed = models.BooleanField(
        default=True,
        help_text="Send notifications when ticket status changes"
    )
    notify_new_message = models.BooleanField(
        default=True,
        help_text="Send notifications for new messages"
    )
    notify_ticket_assigned = models.BooleanField(
        default=True,
        help_text="Send notifications when tickets are assigned"
    )
    notify_ticket_resolved = models.BooleanField(
        default=True,
        help_text="Send notifications when tickets are resolved"
    )
    notify_approaching_sla = models.BooleanField(
        default=True,
        help_text="Send notifications when tickets are approaching SLA deadline"
    )
    notify_sla_breach = models.BooleanField(
        default=True,
        help_text="Send notifications when tickets breach SLA"
    )

    smtp_enabled = models.BooleanField(default=False)
    smtp_email = models.EmailField(blank=True)
    smtp_password = models.CharField(max_length=100, blank=True)
    smtp_host = models.CharField(max_length=100, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_from_email = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name_plural = 'Settings'

    def __str__(self):
        return 'System Settings'

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and Settings.objects.exists():
            return Settings.objects.first()
        return super().save(*args, **kwargs)
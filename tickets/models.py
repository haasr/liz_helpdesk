from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .security import generate_access_code
import datetime
import os

class TicketType(models.TextChoices):
    INCIDENT = 'INC', 'Incident'
    REQUEST = 'REQ', 'Request'

class TicketSubType(models.TextChoices):
    ACCOUNT = 'ACC', 'Account'
    LAB = 'LAB', 'Lab'
    NETWORK = 'NET', 'Network'
    WORKSTATION = 'WRK', 'Laptop/Workstation'
    PRINTER = 'PRT', 'Printer'
    SERVER = 'SRV', 'Server'
    SOFTWARE = 'SFT', 'Software'

class TicketStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    ASSIGNED = 'ASG', 'Assigned'
    IN_PROGRESS = 'PRG', 'In Progress'
    WAITING = 'WTG', 'Waiting for Response'
    RESOLVED = 'RES', 'Resolved'
    CLOSED = 'CLS', 'Closed'

def generate_ticket_number():
    """Generate a year-based ticket number"""
    year = datetime.datetime.now().year
    last_ticket = Ticket.objects.filter(
        ticket_number__startswith=f'{year}-'
    ).order_by('-ticket_number').first()

    if last_ticket:
        last_number = int(last_ticket.ticket_number.split('-')[1])
        new_number = last_number + 1
    else:
        new_number = 1001

    return f"{year}-{new_number}"

class Ticket(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True, default=generate_ticket_number)
    access_code = models.CharField(max_length=6, default=generate_access_code)
    time_created = models.DateTimeField(auto_now_add=True)
    requestor_email = models.EmailField()
    requestor_phone = models.CharField(max_length=20, blank=True)
    requestor_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=3, choices=TicketType.choices)
    subtype = models.CharField(max_length=3, choices=TicketSubType.choices)
    item = models.CharField(max_length=50)  # Detailed classification
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50)
    status = models.CharField(
        max_length=3,
        choices=TicketStatus.choices,
        default=TicketStatus.NEW
    )
    assigned_to = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets'
    )
    assets = models.ManyToManyField('assets.Asset', blank=True)
    has_new_responses = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = generate_ticket_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.title}"
    
    def generate_access_code(self):
        """Generate a 6-character access code using a limited character set"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#&'
        return get_random_string(6, chars)

    # You can then add this method to your Ticket model:
    def refresh_access_code(self):
        """Generate a new access code for the ticket"""
        self.access_code = generate_access_code()
        self.save(update_fields=['access_code'])
        return self.access_code

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.ticket.ticket_number}"
    
    def filename(self):
        return os.path.basename(self.file.name)

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sent_messages'
    )
    sender_email = models.EmailField()  # For messages from requestors
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_from_requestor = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_from_requestor:
            self.ticket.has_new_responses = True
            self.ticket.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message on {self.ticket.ticket_number} at {self.created_at}"

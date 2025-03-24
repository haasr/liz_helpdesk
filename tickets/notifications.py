from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as django_settings
from accounts.models import Settings
from .models import Ticket
from django.conf import settings as django_settings
from accounts.utils import update_email_settings

class NotificationManager:
    """
    Manages email notifications for the ticketing system.
    Handles notification preferences and email sending.
    """

    NOTIFICATION_TYPES = {
        'ticket_created': 'Ticket Creation',
        'status_changed': 'Status Changes',
        'new_message': 'New Messages',
        'ticket_assigned': 'Ticket Assignment',
        'ticket_resolved': 'Ticket Resolution',
    }

    def __init__(self):
        self.settings = Settings.objects.first()
        if not self.settings:
            self.settings = Settings.objects.create()

    def _should_send_notification(self, notification_type):
        """Check if notification should be sent based on settings."""
        if not hasattr(self.settings, f'notify_{notification_type}'):
            return True  # Default to sending if preference not set
        return getattr(self.settings, f'notify_{notification_type}')

    def _send_email(self, subject, template_name, context, recipient_list):
        """Helper method to send emails using templates."""
        update_email_settings()
        context['site_url'] = django_settings.SITE_URL

        html_message = render_to_string(f'tickets/email/{template_name}.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    def notify_ticket_created(self, ticket):
        """Send notification for new ticket creation."""
        if self._should_send_notification('ticket_created'):
            context = {
                'ticket': ticket,
                'access_code': ticket.access_code,
            }
            if django_settings.EMAIL_HOST_PASSWORD: # Check if setup
                self._send_email(
                    subject=f'Ticket Created - {ticket.ticket_number}',
                    template_name='ticket_created',
                    context=context,
                    recipient_list=[ticket.requestor_email]
                )

    def notify_status_changed(self, ticket, old_status):
        """Send notification for ticket status changes."""
        if self._should_send_notification('status_changed'):
            # Get the choices from the Ticket model directly
            status_dict = dict(Ticket.status.field.choices)
            
            old_status_display = status_dict.get(old_status, old_status)
            new_status_display = status_dict.get(ticket.status, ticket.status)
            
            context = {
                'ticket': ticket,
                'old_status': old_status_display,
                'new_status': new_status_display,
            }
            if django_settings.EMAIL_HOST_PASSWORD: # Check if setup
                self._send_email(
                    subject=f'Ticket Status Updated - {ticket.ticket_number}',
                    template_name='status_changed',
                    context=context,
                    recipient_list=[ticket.requestor_email]
                )

    def notify_new_message(self, ticket, message):
        """Send notification for new messages."""
        if self._should_send_notification('new_message'):
            context = {
                'ticket': ticket,
                'message': message,
            }
            # Determine recipient based on message sender
            if message.is_from_requestor and ticket.assigned_to:
                recipient = ticket.assigned_to.email
            else:
                recipient = ticket.requestor_email
            if django_settings.EMAIL_HOST_PASSWORD: # Check if setup
                self._send_email(
                    subject=f'New Message on Ticket {ticket.ticket_number}',
                    template_name='new_message',
                    context=context,
                    recipient_list=[recipient]
                )

    def notify_ticket_assigned(self, ticket, old_technician=None):
        """Send notification for ticket assignment changes."""
        if self._should_send_notification('ticket_assigned'):
            context = {
                'ticket': ticket,
                'old_technician': old_technician.get_full_name() if old_technician else 'Unassigned',
                'new_technician': ticket.assigned_to.get_full_name() if ticket.assigned_to else 'Unassigned',
            }
            recipients = [ticket.requestor_email]
            if ticket.assigned_to:
                recipients.append(ticket.assigned_to.email)
            
            if django_settings.EMAIL_HOST_PASSWORD: # Check if setup
                self._send_email(
                    subject=f'Ticket Assignment Updated - {ticket.ticket_number}',
                    template_name='ticket_assigned',
                    context=context,
                    recipient_list=recipients
                )

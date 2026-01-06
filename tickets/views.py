from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Ticket, TicketAttachment, TicketMessage
from .forms import TicketSubmissionForm, TicketAccessForm, TicketMessageForm
from .notifications import NotificationManager
from django.conf import settings
from accounts.models import Settings
from assets.models import Asset

def submit_ticket(request):
    """Public view for submitting new tickets"""
    if request.method == 'POST':
        form = TicketSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Create ticket but don't save yet
            ticket = form.save(commit=False)
            ticket.save()  # Now save to get an ID
            
            # Handle inventory number and assets
            inventory_number = form.cleaned_data.get('inventory_number')
            asset_type = form.cleaned_data.get('asset_type')
            
            if inventory_number:
                # Try to find existing asset
                asset = None
                try:
                    asset = Asset.objects.get(inventory_number=inventory_number)
                    # Optionally update the asset type if different
                    if asset_type and asset.type != asset_type:
                        asset.type = asset_type
                        asset.save()
                        messages.info(request, f"Updated asset type for {inventory_number}")
                except Asset.DoesNotExist:
                    # Create a new asset with user-provided type
                    asset = Asset.objects.create(
                        inventory_number=inventory_number,
                        name=f"Asset {inventory_number}",
                        type=asset_type,  # Use the user-selected type
                        location='Unknown',
                        details=f"Created from ticket {ticket.ticket_number}"
                    )
                    messages.info(request, f"Created new asset with inventory number {inventory_number}")
                
                # Associate asset with ticket
                if asset:
                    ticket.assets.add(asset)
            
            # Handle attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                TicketAttachment.objects.create(ticket=ticket, file=file)
            
            # Send notification
            notification_manager = NotificationManager()
            notification_manager.notify_ticket_created(ticket)
            
            messages.success(request, 'Ticket submitted successfully! Check your email for details.')
            return redirect('ticket_confirmation', ticket_number=ticket.ticket_number)
    else:
        form = TicketSubmissionForm()
    
    return render(request, 'tickets/submit_ticket.html', {'form': form})

def view_ticket(request, ticket_number, access_code):
    """Public view for requestors to view their tickets"""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number, access_code=access_code)
    notification_manager = NotificationManager()

    if request.method == 'POST':
        message_form = TicketMessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.sender_email = ticket.requestor_email
            message.is_from_requestor = True
            message.save()
    else:
        message_form = TicketMessageForm()

    context = {
        'ticket': ticket,
        'message_form': message_form,
    }
    return render(request, 'tickets/view_ticket.html', context)

def ticket_confirmation(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    return render(request, 'tickets/confirmation.html', {'ticket': ticket})

def access_ticket(request):
    if request.method == 'POST':
        form = TicketAccessForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            ticket_number = form.cleaned_data['ticket_number']
            access_code = form.cleaned_data['access_code']

            try:
                ticket = Ticket.objects.get(
                    ticket_number=ticket_number,
                    requestor_email=email,
                    access_code=access_code
                )
                return redirect('view_ticket', ticket_number=ticket.ticket_number, access_code=access_code)
            except Ticket.DoesNotExist:
                messages.error(request, 'Invalid ticket information. Please check your email and try again.')
    else:
        form = TicketAccessForm()

    return render(request, 'tickets/access_ticket.html', {'form': form})

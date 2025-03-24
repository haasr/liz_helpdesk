from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now
from .models import Ticket, TicketMessage
from accounts.models import Settings
from .forms import TicketMessageForm
from .notifications import NotificationManager
from django.contrib.auth import get_user_model
from assets.models import Asset

def is_system_manager(user):
    User = get_user_model()
    return user.is_authenticated and user.user_type == User.UserType.SYSTEM_MANAGER

@login_required
def dashboard(request):
    """Technician dashboard showing ticket queue"""
    # Get system settings
    settings = Settings.objects.first()
    notification_manager = NotificationManager()

    # Base queryset
    if (settings and settings.ticket_visibility) or (is_system_manager(request.user)):
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(assigned_to=request.user)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requestor_email__icontains=search_query) |
            Q(requestor_name__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        tickets = tickets.filter(type=type_filter)

    # Sort functionality
    sort_by = request.GET.get('sort', '-time_created')
    valid_sort_fields = [
        'time_created', '-time_created',
        'status', '-status',
        'type', '-type',
        'title', '-title'
    ]
    if sort_by in valid_sort_fields:
        tickets = tickets.order_by(sort_by)

    # Pagination
    paginator = Paginator(tickets, 20)  # 20 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count tickets by status
    status_counts = {
        'new': tickets.filter(status='NEW').count(),
        'assigned': tickets.filter(status='ASG').count(),
        'in_progress': tickets.filter(status='PRG').count(),
        'waiting': tickets.filter(status='WTG').count(),
        'resolved': tickets.filter(status='RES').count(),
        'closed': tickets.filter(status='CLS').count(),
    }

    context = {
        'page_obj': page_obj,
        'status_counts': status_counts,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'sort_by': sort_by,
        'settings': settings,
        'ticket_status_choices': Ticket.status.field.choices,
        'ticket_type_choices': Ticket.type.field.choices,
    }
    return render(request, 'tickets/technician/dashboard.html', context)

@login_required
def manage_ticket(request, ticket_number):
    """Handle ticket management operations"""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    settings = Settings.objects.first()
    notification_manager = NotificationManager()

    if not is_system_manager(request.user):
        # Check if technician has access to this ticket
        if not settings.ticket_visibility and ticket.assigned_to != request.user:
            messages.error(request, "You don't have permission to view this ticket.")
            return redirect('technician_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            old_status = ticket.status # This is a string, such as 'NEW'
            new_status = request.POST.get('status')
            if new_status in dict(Ticket.status.field.choices):
                ticket.status = new_status
                ticket.save()

                notification_manager.notify_status_changed(ticket, old_status)
                messages.success(request, 'Ticket status updated successfully.')

        elif action == 'add_message':
            message_form = TicketMessageForm(request.POST)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.ticket = ticket
                message.sender = request.user
                message.sender_email = request.user.email
                message.save()

                # Generate new access code when technician responds
                ticket.access_code = ticket.generate_access_code()
                ticket.save()

                notification_manager.notify_new_message(ticket, message)
                messages.success(request, 'Message added successfully.')

        elif action == 'assign_ticket':
            old_technician = ticket.assigned_to
            technician_id = request.POST.get('technician')

            if technician_id:
                User = get_user_model()
                try:
                    technician = User.objects.get(id=technician_id)
                    ticket.assigned_to = technician
                    ticket.status = 'ASG'  # Update status to Assigned
                    ticket.save()

                    notification_manager.notify_ticket_assigned(ticket, old_technician)
                    messages.success(request, f'Ticket assigned to {technician.get_full_name()}')
                except User.DoesNotExist:
                    messages.error(request, 'Selected technician not found.')
            else:
                ticket.assigned_to = None
                ticket.status = 'NEW'  # Update status to New
                ticket.save()

                notification_manager.notify_ticket_assigned(ticket, old_technician)
                messages.success(request, 'Ticket unassigned.')

        # Handle asset removal
        elif action == 'remove_asset':
            asset_id = request.POST.get('asset_id')
            if asset_id:
                try:
                    asset = Asset.objects.get(id=asset_id)
                    ticket.assets.remove(asset)
                    messages.success(request, f"Asset {asset.inventory_number} removed from ticket.")
                except Asset.DoesNotExist:
                    messages.error(request, "Asset not found.")
            else:
                messages.error(request, "No asset specified.")

    message_form = TicketMessageForm()

    # Get available technicians for assignment:
    User = get_user_model()
    available_technicians = User.objects.filter(id=request.user.id) # First get current user (in case they are sys manager, then they can self-assign)
    available_technicians = available_technicians | User.objects.filter(user_type='TCH') # union

    context = {
        'ticket': ticket,
        'message_form': message_form,
        'available_technicians': available_technicians,
        'settings': settings,
        'status_choices': Ticket.status.field.choices,
    }
    return render(request, 'tickets/technician/manage_ticket.html', context)

@login_required
def add_asset_to_ticket(request, ticket_number):
    """Add an asset to a ticket"""
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    settings = Settings.objects.first()
    
    if not is_system_manager(request.user):
        # Check if technician has access to this ticket
        if (not settings.ticket_visibility and ticket.assigned_to != request.user):
            messages.error(request, "You don't have permission to modify this ticket.")
            return redirect('technician_dashboard')
    
    if request.method == 'POST':
        inventory_number = request.POST.get('inventory_number')
        if inventory_number:
            try:
                asset = Asset.objects.get(inventory_number=inventory_number)
                # Check if asset is already associated with the ticket
                if asset in ticket.assets.all():
                    messages.warning(request, f"Asset {inventory_number} is already associated with this ticket.")
                else:
                    ticket.assets.add(asset)
                    messages.success(request, f"Asset {inventory_number} added to ticket.")
            except Asset.DoesNotExist:
                messages.error(request, f"No asset found with inventory number {inventory_number}.")
        else:
            messages.error(request, "No inventory number provided.")
    
    return redirect('manage_ticket', ticket_number=ticket.ticket_number)

@login_required
def self_assign_ticket(request, ticket_number):
    """Allow technicians to assign tickets to themselves"""
    settings = Settings.objects.first()
    notification_manager = NotificationManager()

    if not settings or not settings.ticket_self_assignment:
        messages.error(request, 'Self-assignment is not allowed.')
        return redirect('technician_dashboard')

    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    if ticket.assigned_to:
        messages.error(request, 'This ticket is already assigned.')
    else:
        old_technician = None
        ticket.assigned_to = request.user
        ticket.status = 'ASG'  # Update status to Assigned
        ticket.save()

        notification_manager.notify_ticket_assigned(ticket, old_technician)
        messages.success(request, 'Ticket self-assigned successfully.')

    return redirect('manage_ticket', ticket_number=ticket_number)

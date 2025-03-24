from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CustomLoginForm, TechnicianCreationForm, SystemManagerCreationForm
from django.contrib.auth.views import PasswordResetView
from .models import User, Settings
from .forms import SettingsForm
from .utils import update_email_settings

def is_system_manager(user):
    return user.is_authenticated and user.user_type == User.UserType.SYSTEM_MANAGER

@login_required
@user_passes_test(is_system_manager)
def manage_settings(request):
    """System settings management view"""
    from accounts.utils import update_email_settings
    
    settings = Settings.objects.first()
    if not settings:
        settings = Settings.objects.create()

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            # Update email settings after saving
            update_email_settings()
            messages.success(request, 'Settings updated successfully.')
            return redirect('manage_settings')
    else:
        form = SettingsForm(instance=settings)

    return render(request, 'accounts/manage_settings.html', {
        'form': form,
        'settings': settings
    })

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password."

    def form_valid(self, form):
        """Ensure only ETSU email addresses can request password resets"""
        email = form.cleaned_data['email']
        if not email.endswith('@etsu.edu'):
            form.add_error('email', 'Password reset is only available for ETSU email addresses.')
            return self.form_invalid(form)
        return super().form_valid(form)

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('technician_dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Get the next page from the URL or default to dashboard
            next_page = request.GET.get('next', 'technician_dashboard')
            return redirect(next_page)
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def is_system_manager(user):
    """Check if user is a system manager"""
    return user.is_authenticated and user.user_type == User.UserType.SYSTEM_MANAGER

# User Management Views (these should already exist in your views.py)
@login_required
@user_passes_test(is_system_manager)
def manage_users(request):
    """View for managing users (system managers only)"""
    technicians = User.objects.filter(user_type=User.UserType.TECHNICIAN)
    system_managers = User.objects.filter(user_type=User.UserType.SYSTEM_MANAGER)

    context = {
        'technicians': technicians,
        'system_managers': system_managers,
    }
    return render(request, 'accounts/manage_users.html', context)

@login_required
@user_passes_test(is_system_manager)
def add_technician(request):
    """Add new technician (system managers only)"""
    if request.method == 'POST':
        form = TechnicianCreationForm(request.POST)
        if form.is_valid():
            technician = form.save()
            messages.success(request, f'Technician {technician.get_full_name()} created successfully.')
            return redirect('manage_users')
    else:
        form = TechnicianCreationForm()

    return render(request, 'accounts/add_technician.html', {'form': form})

@login_required
@user_passes_test(is_system_manager)
def add_system_manager(request):
    """Add new system manager (system managers only)"""
    if request.method == 'POST':
        form = SystemManagerCreationForm(request.POST)
        if form.is_valid():
            manager = form.save()
            messages.success(request, f'System Manager {manager.get_full_name()} created successfully.')
            return redirect('manage_users')
    else:
        form = SystemManagerCreationForm()

    return render(request, 'accounts/add_system_manager.html', {'form': form})

@login_required
@user_passes_test(is_system_manager)
def toggle_user_active(request, user_id):
    """Toggle user active status (system managers only)"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:  # Prevent self-deactivation
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} {status} successfully.')
    else:
        messages.error(request, 'You cannot deactivate your own account.')
    return redirect('manage_users')

@login_required
@user_passes_test(is_system_manager)
def delete_user(request, user_id):
    """Delete a user (technician or system manager)"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('manage_users')
    
    # Check if user has assigned tickets
    assigned_tickets = user.assigned_tickets.all()
    tickets_count = assigned_tickets.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm_delete':
            # Handle assigned tickets if any
            if tickets_count > 0:
                reassign_option = request.POST.get('reassign_option')
                if reassign_option == 'unassign':
                    # Unassign all tickets
                    for ticket in assigned_tickets:
                        ticket.assigned_to = None
                        ticket.status = 'NEW'  # Reset to new status
                        ticket.save()
                elif reassign_option == 'reassign' and request.POST.get('new_technician'):
                    # Reassign to another technician
                    new_technician_id = request.POST.get('new_technician')
                    try:
                        new_technician = User.objects.get(id=new_technician_id)
                        for ticket in assigned_tickets:
                            ticket.assigned_to = new_technician
                            ticket.save()
                    except User.DoesNotExist:
                        messages.error(request, "Selected technician not found.")
                        return redirect('delete_user', user_id=user_id)
                else:
                    messages.error(request, "Please select a valid reassignment option.")
                    return redirect('delete_user', user_id=user_id)
            
            # Now delete the user
            username = user.username
            user.delete()
            messages.success(request, f"User '{username}' has been permanently deleted.")
            return redirect('manage_users')
    
    # For GET request or if POST didn't process
    # Get other technicians for reassignment options
    other_technicians = User.objects.filter(user_type='TCH').exclude(id=user_id)
    
    context = {
        'user_to_delete': user,
        'tickets_count': tickets_count,
        'other_technicians': other_technicians,
    }
    return render(request, 'accounts/delete_user.html', context)

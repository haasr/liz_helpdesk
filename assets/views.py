from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Asset
from .forms import AssetForm
from accounts.models import Settings
from django.contrib.auth import get_user_model

def is_system_manager(user):
    User = get_user_model()
    return user.is_authenticated and user.user_type == User.UserType.SYSTEM_MANAGER

@login_required
def asset_list(request):
    """View for listing assets with search and filtering"""
    # Get system settings
    settings = Settings.objects.first()
    
    # Check permission based on settings - Sys Manager should see all
    if (settings and settings.asset_visibility) or is_system_manager(request.user):
        assets = Asset.objects.all()
    else:
        # Get assets linked to tickets assigned to the user
        assets = Asset.objects.filter(ticket__assigned_to=request.user).distinct()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        assets = assets.filter(
            Q(inventory_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(details__icontains=search_query)
        )
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        assets = assets.filter(type=type_filter)
    
    # Filter by active status
    active_filter = request.GET.get('active', '')
    if active_filter:
        is_active = active_filter == 'true'
        assets = assets.filter(is_active=is_active)
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'inventory_number')
    valid_sort_fields = [
        'inventory_number', '-inventory_number',
        'name', '-name',
        'type', '-type',
        'location', '-location'
    ]
    if sort_by in valid_sort_fields:
        assets = assets.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(assets, 20)  # 20 assets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'active_filter': active_filter,
        'sort_by': sort_by,
        'settings': settings,
        'asset_type_choices': Asset.type.field.choices,
    }
    return render(request, 'assets/asset_list.html', context)

@login_required
def asset_detail(request, inventory_number):
    """View for viewing asset details"""
    asset = get_object_or_404(Asset, inventory_number=inventory_number)
    settings = Settings.objects.first()
    User = get_user_model()
    
    # Check if user has permission to view this asset
    has_permission = False
    if (settings and settings.asset_visibility) or is_system_manager(request.user):
        has_permission = True
    elif settings and settings.can_modify_assigned_assets:
        # Check if asset is linked to any ticket assigned to the user
        has_permission = asset.ticket_set.filter(assigned_to=request.user).exists()
    
    if not has_permission:
        messages.error(request, "You don't have permission to view this asset.")
        return redirect('asset_list')
    
    # Get related tickets
    related_tickets = asset.ticket_set.all()
    
    context = {
        'asset': asset,
        'related_tickets': related_tickets,
        'settings': settings,
    }
    return render(request, 'assets/asset_detail.html', context)

@login_required
def asset_create(request):
    """View for creating new assets"""
    settings = Settings.objects.first()
    
    # Check if user has permission to create assets
    if not ((settings and settings.can_modify_all_assets) or (is_system_manager(request.user))):
        messages.error(request, "You don't have permission to create assets.")
        return redirect('asset_list')
    
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save()
            messages.success(request, f"Asset {asset.inventory_number} created successfully.")
            return redirect('asset_detail', inventory_number=asset.inventory_number)
    else:
        form = AssetForm(user=request.user)
    
    context = {
        'form': form,
        'back_to_asset_detail': False,
    }
    return render(request, 'assets/asset_form.html', context)

@login_required
def asset_update(request, inventory_number, back_to_asset_detail=1):
    """View for updating existing assets"""
    asset = get_object_or_404(Asset, inventory_number=inventory_number)
    settings = Settings.objects.first()
    User = get_user_model()

    # Check if user has permission to update this asset
    has_permission = False
    if (settings and settings.can_modify_all_assets) or (is_system_manager(request.user)):
        has_permission = True
    elif settings and settings.can_modify_assigned_assets:
        # Check if asset is linked to any ticket assigned to the user
        has_permission = asset.ticket_set.filter(assigned_to=request.user).exists()
    
    if not has_permission:
        messages.error(request, "You don't have permission to update this asset.")
        return redirect('asset_list')
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Asset {asset.inventory_number} updated successfully.")
            return redirect('asset_detail', inventory_number=asset.inventory_number)
    else:
        form = AssetForm(instance=asset, user=request.user)

    context = {
        'form': form,
        'asset': asset,
        'back_to_asset_detail': bool(back_to_asset_detail),
    }
    return render(request, 'assets/asset_form.html', context)

@login_required
def asset_delete(request, inventory_number):
    """View for deleting assets"""
    asset = get_object_or_404(Asset, inventory_number=inventory_number)
    settings = Settings.objects.first()
    
    # Check if user has permission to delete assets
    if not ((settings and settings.can_modify_all_assets) or (is_system_manager(request.user))):
        messages.error(request, "You don't have permission to delete assets.")
        return redirect('asset_list')
    
    if request.method == 'POST':
        # Check if asset is linked to any tickets
        if asset.ticket_set.exists():
            messages.error(request, "Cannot delete asset that is linked to tickets.")
            return redirect('asset_detail', inventory_number=asset.inventory_number)
        
        asset_number = asset.inventory_number
        asset.delete()
        messages.success(request, f"Asset {asset_number} deleted successfully.")
        return redirect('asset_list')
    
    context = {
        'asset': asset,
    }
    return render(request, 'assets/asset_confirm_delete.html', context)

"""
Views for user authentication and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from .models import User, UserProfile, UserSession
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, 
    UserProfileForm, UserUpdateForm, PasswordChangeForm
)


def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(
                request, 
                'Account created successfully! Please wait for admin approval.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Track user session
                    UserSession.objects.create(
                        user=user,
                        session_key=request.session.session_key,
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Your account is inactive.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    User logout view.
    """
    # Deactivate current session
    try:
        session = UserSession.objects.get(
            user=request.user,
            session_key=request.session.session_key
        )
        session.is_active = False
        session.save()
    except UserSession.DoesNotExist:
        pass
    
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    """
    User profile view.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """
    Change password view.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def user_list_view(request):
    """
    List all users (admin/authority only).
    """
    if not (request.user.is_admin() or request.user.is_railway_authority()):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    
    # Filter by user type
    user_type_filter = request.GET.get('user_type')
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_types': User.USER_TYPE_CHOICES,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
def user_detail_view(request, user_id):
    """
    User detail view (admin/authority only).
    """
    if not (request.user.is_admin() or request.user.is_railway_authority()):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    context = {
        'user_detail': user,
        'user_profile': user_profile,
    }
    return render(request, 'accounts/user_detail.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """
    Toggle user active status (admin only).
    """
    if not request.user.is_admin():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
    })


@login_required
@require_http_methods(["POST"])
def verify_user(request, user_id):
    """
    Verify user account (admin/authority only).
    """
    if not (request.user.is_admin() or request.user.is_railway_authority()):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    user.is_verified = not user.is_verified
    user.save()
    
    return JsonResponse({
        'success': True,
        'is_verified': user.is_verified,
        'message': f'User {"verified" if user.is_verified else "unverified"} successfully'
    })


# API Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_user_info(request):
    """
    API endpoint to get current user information.
    """
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'user_type': user.user_type,
        'user_type_display': user.get_user_type_display(),
        'employee_id': user.employee_id,
        'phone_number': user.phone_number,
        'department': user.department,
        'designation': user.designation,
        'is_verified': user.is_verified,
        'profile': {
            'bio': profile.bio,
            'company_name': profile.company_name,
            'railway_zone': profile.railway_zone,
            'railway_division': profile.railway_division,
            'work_location': profile.work_location,
        }
    }
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_sessions(request):
    """
    API endpoint to get user's active sessions.
    """
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')
    
    data = []
    for session in sessions:
        data.append({
            'id': session.id,
            'ip_address': session.ip_address,
            'login_time': session.login_time,
            'last_activity': session.last_activity,
            'is_current': session.session_key == request.session.session_key,
        })
    
    return Response(data)

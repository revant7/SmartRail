"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    """
    list_display = (
        'username', 'email', 'get_full_name', 'user_type', 
        'employee_id', 'department', 'is_verified', 'is_active', 'date_joined'
    )
    list_filter = (
        'user_type', 'is_verified', 'is_active', 'is_staff', 
        'is_superuser', 'date_joined'
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name', 
        'employee_id', 'department'
    )
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Professional info', {
            'fields': ('user_type', 'employee_id', 'department', 'designation')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified',
                      'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 
                      'user_type', 'employee_id', 'phone_number'),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model.
    """
    list_display = (
        'user', 'company_name', 'authority_level', 
        'vendor_category', 'railway_zone', 'created_at'
    )
    list_filter = (
        'authority_level', 'vendor_category', 'railway_zone', 'created_at'
    )
    search_fields = (
        'user__username', 'user__email', 'company_name', 
        'railway_zone', 'railway_division'
    )
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'profile_picture', 'bio', 'address', 'emergency_contact')
        }),
        ('Railway Authority Info', {
            'fields': ('authority_level', 'jurisdiction'),
            'classes': ('collapse',)
        }),
        ('Vendor Info', {
            'fields': ('company_name', 'company_registration', 'vendor_category'),
            'classes': ('collapse',)
        }),
        ('Employee Info', {
            'fields': ('railway_zone', 'railway_division', 'work_location'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin for UserSession model.
    """
    list_display = (
        'user', 'ip_address', 'login_time', 
        'last_activity', 'is_active'
    )
    list_filter = ('is_active', 'login_time', 'last_activity')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('session_key', 'login_time', 'last_activity')
    raw_id_fields = ('user',)
    
    def has_add_permission(self, request):
        return False

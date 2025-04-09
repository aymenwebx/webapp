from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type', 'student_id', 'teacher_subject', 'parent_phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

admin.site.register(User, CustomUserAdmin)
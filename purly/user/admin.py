from django.contrib import admin

from .models import User, UserActivity


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "date_joined",
        "last_login",
    ]
    list_filter = ["is_active", "date_joined", "last_login"]


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "user_agent", "session_key", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["user", "ip_address", "user_agent", "session_key", "created_at"]


admin.site.register(User, UserAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

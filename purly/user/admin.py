from django.contrib import admin

from .models import User, UserActivity, UserProfile


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
    search_fields = ["username", "first_name", "last_name", "email"]

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "job_title", "department", "phone", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "job_title", "department", "phone", "bio"]
    readonly_fields = ["created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        return False


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "user_agent", "session_key", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "ip_address", "user_agent", "session_key"]
    readonly_fields = ["user", "ip_address", "user_agent", "session_key", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

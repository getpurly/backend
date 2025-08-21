from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, UserActivity, UserProfile

admin.site.unregister(EmailAddress)
admin.site.unregister(Group)


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
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

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.filter(is_active=True)

        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    list_display = ["id", "user", "job_title", "department", "phone", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "job_title", "department", "phone", "bio"]
    readonly_fields = ["created_at", "updated_at"]

    def has_delete_permission(self, request, obj=None):
        return False


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "ip_address", "user_agent", "session_key", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "ip_address", "user_agent", "session_key"]
    readonly_fields = ["user", "ip_address", "user_agent", "session_key", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "email", "verified", "primary"]
    list_filter = ["verified", "primary"]
    search_fields = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

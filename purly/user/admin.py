from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User, UserActivity, UserProfile


class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("username", "password", "first_name", "last_name", "email"),
            },
        ),
        (
            "Permission Settings",
            {
                "fields": ("user_permissions", "groups", "is_staff", "is_superuser"),
            },
        ),
        (
            "Misc",
            {
                "classes": ["collapse"],
                "fields": ("date_joined", "last_login", "is_active"),
            },
        ),
    )
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        from django.contrib.auth.models import Permission

        if db_field.name == "user_permissions":
            kwargs["queryset"] = Permission.objects.all().select_related("content_type")

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.filter(is_active=True).order_by("username")

        return queryset, use_distinct

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("user", "job_title", "department", "phone"),
            },
        ),
        (
            "Misc",
            {
                "classes": ["collapse"],
                "fields": ("created_at", "created_by", "updated_at", "updated_by", "deleted"),
            },
        ),
    )
    list_display = ["id", "user", "job_title", "department", "phone", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "job_title", "department", "phone", "bio"]
    readonly_fields = ["user", "created_at", "created_by", "updated_at", "updated_by", "deleted"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


class UserActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("user", "action", "context", "ip_address", "user_agent", "session_key"),
            },
        ),
        (
            "Misc",
            {
                "classes": ["collapse"],
                "fields": ("created_at",),
            },
        ),
    )

    list_display = [
        "id",
        "user",
        "action",
        "context",
        "ip_address",
        "user_agent",
        "session_key",
        "created_at",
    ]
    list_filter = ["action", "created_at"]
    search_fields = [
        "id",
        "user__username",
        "action",
        "context",
        "ip_address",
        "user_agent",
        "session_key",
    ]
    readonly_fields = [
        "user",
        "action",
        "context",
        "ip_address",
        "user_agent",
        "session_key",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "email", "verified", "primary"]
    list_filter = ["verified", "primary"]
    search_fields = ["user__username", "email"]


admin.site.unregister(EmailAddress)
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
# admin.site.register(EmailAddress, EmailAddressAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserActivity


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "user_agent", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["user", "ip_address", "user_agent", "created_at"]


admin.site.register(User, UserAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

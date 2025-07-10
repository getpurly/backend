from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.db import models

from .utils import get_ip_address, get_user_agent


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(max_length=255, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_activity"
        verbose_name = "user activity"
        verbose_name_plural = "user activity"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username


def record_user_activity(sender, request, user, **kwargs):
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)

    new_activity = UserActivity(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        session_key=request.session.session_key,
    )
    new_activity.save()


user_logged_in.connect(record_user_activity)

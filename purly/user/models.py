from allauth.account.signals import (
    email_added,
    email_changed,
    email_removed,
    password_changed,
    password_reset,
    user_logged_in,
    user_logged_out,
    user_signed_up,
)
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in as user_logged_in_admin
from django.contrib.auth.signals import user_logged_out as user_logged_out_admin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from purly.base import ModelBase

from .utils import get_ip_address, get_user_agent


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username


class UserProfile(ModelBase):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    job_title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    bio = models.TextField(blank=True)

    class Meta(ModelBase.Meta):
        db_table = "user_profile"
        verbose_name = "profile"
        verbose_name_plural = "profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"User profile: {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.update_or_create(user=instance)


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    context = models.TextField(blank=True)
    action = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(
        max_length=255, blank=True, null=True, verbose_name="IP address"
    )
    user_agent = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_activity"
        verbose_name = "activity"
        verbose_name_plural = "activity"
        ordering = ["-created_at"]

    def __str__(self):
        return f"User activity: {self.user.username}"


USER_SIGNALS = {
    user_signed_up: "Sign up",
    user_logged_in: "Login",
    user_logged_in_admin: "Login",
    user_logged_out: "Logout",
    user_logged_out_admin: "Logout",
    password_changed: "Password change",
    password_reset: "Password reset",
    email_changed: "Email change",
    email_added: "Email add",
    email_removed: "Email remove",
}


@receiver(
    [
        user_signed_up,
        user_logged_in,
        user_logged_in_admin,
        user_logged_out,
        user_logged_out_admin,
        password_changed,
        password_reset,
        email_changed,
        email_added,
        email_removed,
    ]
)
def record_user_activity(  # noqa: PLR0913
    sender,
    signal,
    request,
    user,
    email_address=None,
    from_email_address=None,
    to_email_address=None,
    **kwargs,
):
    ip_address = get_ip_address(request)
    user_agent = get_user_agent(request)

    action = USER_SIGNALS.get(signal, "")

    if signal == email_changed:
        if from_email_address:
            context = f"Primary email changed from {from_email_address} to {to_email_address}"
        else:
            context = f"Primary email set to: {to_email_address}"
    elif signal == email_added:
        context = f"Email added: {email_address}"
    elif signal == email_removed:
        context = f"Email removed: {email_address}"
    else:
        context = ""

    new_activity = UserActivity(
        user=user,
        action=action,
        context=context,
        ip_address=ip_address,
        user_agent=user_agent,
        session_key=request.session.session_key,
    )

    new_activity.save()

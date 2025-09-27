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
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from purly.approval.services import cancel_user_approvals
from purly.base import ModelBase

from .utils import get_ip_address, get_user_agent


class UserActivityActionChoices(models.TextChoices):
    SIGNUP = ("signup", "signup")
    LOGIN = ("login", "login")
    LOGOUT = ("logout", "logout")
    PASSWORD_CHANGE = ("password_change", "password_change")
    PASSWORD_RESET = ("password_reset", "password_reset")
    EMAIL_CHANGE = ("email_change", "email_change")
    EMAIL_ADD = ("email_add", "email_add")
    EMAIL_REMOVE = ("email_remove", "email_remove")


class User(AbstractUser):
    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def deactivate_approvals(sender, instance, **kwargs):
    if instance.is_active is False:
        cancel_user_approvals(instance)


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
    action = models.CharField(choices=UserActivityActionChoices)
    context = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(
        max_length=255, blank=True, null=True, verbose_name="IP address"
    )
    user_agent = models.TextField(blank=True)
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
    user_signed_up: UserActivityActionChoices.SIGNUP,
    user_logged_in: UserActivityActionChoices.LOGIN,
    user_logged_out: UserActivityActionChoices.LOGOUT,
    password_changed: UserActivityActionChoices.PASSWORD_CHANGE,
    password_reset: UserActivityActionChoices.PASSWORD_RESET,
    email_changed: UserActivityActionChoices.EMAIL_CHANGE,
    email_added: UserActivityActionChoices.EMAIL_ADD,
    email_removed: UserActivityActionChoices.EMAIL_REMOVE,
}


@receiver(list(USER_SIGNALS.keys()))
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
    if request:
        ip_address = get_ip_address(request)
        user_agent = get_user_agent(request)
    else:
        ip_address = None
        user_agent = ""

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
        session_key=request.session.session_key if request.session.session_key else "",
    )

    new_activity.save()

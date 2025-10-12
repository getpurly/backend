from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader

from purly.requisition.models import Requisition

from .models import Approval


@shared_task
def send_approval_email(requisition_id, approval_id):
    requisition = Requisition.objects.get(pk=requisition_id)
    approval = Approval.objects.get(pk=approval_id)

    context = {
        "approver": approval.approver.username,
        "approval_id": approval.pk,
        "requisition_id": requisition.pk,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "justification": requisition.justification,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "email_subject_prefix": settings.APP_EMAIL_SUBJECT_PREFIX,
        "site_url": settings.SITE_URL,
        "site_name": settings.SITE_NAME,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/approval_subject.txt", context)
    body = loader.render_to_string("approval/email/approval.txt", context)

    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [approval.approver.email])

    email.send()


@shared_task
def send_reject_email(requisition_id, approval_id):
    requisition = Requisition.objects.get(pk=requisition_id)
    approval = Approval.objects.get(pk=approval_id)

    context = {
        "requisition_id": requisition.pk,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "rejected_at": requisition.rejected_at,
        "rejected_by": approval.approver.username,
        "rejected_comment": approval.comment,
        "email_subject_prefix": settings.APP_EMAIL_SUBJECT_PREFIX,
        "site_url": settings.SITE_URL,
        "site_name": settings.SITE_NAME,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/rejected_subject.txt", context)
    body = loader.render_to_string("approval/email/rejected.txt", context)

    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [requisition.owner.email])

    email.send()


@shared_task
def send_fully_approved_email(requisition_id):
    requisition = Requisition.objects.get(pk=requisition_id)

    context = {
        "requisition_id": requisition.pk,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "approved_at": requisition.approved_at,
        "email_subject_prefix": settings.APP_EMAIL_SUBJECT_PREFIX,
        "site_url": settings.SITE_URL,
        "site_name": settings.SITE_NAME,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/fully_approved_subject.txt", context)
    body = loader.render_to_string("approval/email/fully_approved.txt", context)

    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [requisition.owner.email])

    email.send()

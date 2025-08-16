from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader


def send_approval_email(requisition, approval):
    context = {
        "approver": approval.approver.username,
        "approval_id": approval.id,
        "requisition_id": requisition.id,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "justification": requisition.justification,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "site_url": settings.SITE_URL,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/approval_subject.txt", context)
    body = loader.render_to_string("approval/email/approval.txt", context)

    email = EmailMessage(subject, body, settings.EMAIL_FROM, [approval.approver.email])

    email.send()


def send_reject_email(approval, requisition):
    context = {
        "requisition_id": requisition.id,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "rejected_at": requisition.rejected_at,
        "rejected_by": approval.approver.username,
        "rejected_comment": approval.comment,
        "site_url": settings.SITE_URL,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/rejected_subject.txt", context)
    body = loader.render_to_string("approval/email/rejected.txt", context)

    email = EmailMessage(subject, body, settings.EMAIL_FROM, [requisition.owner.email])

    email.send()


def send_fully_approved_email(requisition):
    context = {
        "requisition_id": requisition.id,
        "owner": requisition.owner,
        "supplier": requisition.supplier,
        "total_amount": requisition.total_amount,
        "currency": requisition.currency,
        "submitted_at": requisition.submitted_at,
        "approved_at": requisition.approved_at,
        "site_url": settings.SITE_URL,
    }

    if requisition.project is not None:
        context["project_name"] = requisition.project.name

    subject = loader.render_to_string("approval/email/fully_approved_subject.txt", context)
    body = loader.render_to_string("approval/email/fully_approved.txt", context)

    email = EmailMessage(subject, body, settings.EMAIL_FROM, [requisition.owner.email])

    email.send()

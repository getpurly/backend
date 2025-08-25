from django.core.management.base import BaseCommand

from purly.address.models import Address
from purly.approval.models import ApprovalGroup
from purly.project.models import Project
from purly.requisition.models import Requisition
from purly.user.models import User, UserProfile


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Requisition.objects.all().delete()
        Address.objects.all().delete()
        Project.objects.all().delete()
        ApprovalGroup.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().exclude(id=1).delete()

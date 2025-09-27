from django.core.management.base import BaseCommand

from purly.address.models import Address
from purly.approval.models import ApprovalChain, ApprovalGroup
from purly.project.models import Project
from purly.requisition.models import Requisition
from purly.user.models import CustomUser, UserProfile


class Command(BaseCommand):
    help = "Delete fake data from database."

    def handle(self, *args, **kwargs):
        Requisition.objects.all().delete()
        Address.objects.all().delete()
        Project.objects.all().delete()
        ApprovalGroup.objects.all().delete()
        ApprovalChain.objects.all().delete()
        UserProfile.objects.all().delete()
        CustomUser.objects.all().exclude(id=1).delete()

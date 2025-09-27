import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from purly.address.models import Address
from purly.approval.models import ApprovalChain, ApprovalChainModeChoices, ApprovalGroup
from purly.project.models import Project
from purly.requisition.models import (
    LineTypeChoices,
    Requisition,
    RequisitionLine,
    RequisitionStatusChoices,
)
from purly.user.models import CustomUser, UserActivity, UserActivityActionChoices, UserProfile

fake = Faker("en_US")

NUMBER_OF_USERS = 100
NUMBER_OF_ADDRESSES = 250
NUMBER_OF_PROJECTS = 30
NUMBER_OF_APPROVAL_GROUPS = 30
NUMBER_OF_SERVICE_REQUISITIONS = 500
NUMBER_OF_GOODS_REQUISITIONS = 500

CURRENCY = ["usd"]
CATEGORIES = ["Advertising", "IT", "Food", "Furniture", "Vehicle Rental"]
PAYMENT_TERMS = ["net_30", "net_45", "net_90"]
UOM = ["each", "box"]


class Command(BaseCommand):
    help = "Create fake data in database."

    created_users = []
    created_user_profiles = []
    created_addresses = []
    created_projects = []
    created_approval_groups = []
    created_approval_chains = []

    def handle(self, *args, **kwargs):
        users = []

        usernames = [
            f"{fake.user_name()}{fake.random_number(digits=6)}" for _ in range(NUMBER_OF_USERS)
        ]

        for i in range(NUMBER_OF_USERS):
            user = CustomUser(
                username=usernames[i],
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=fake.sha256(),
            )

            users.append(user)

        self.created_users = CustomUser.objects.bulk_create(users, batch_size=NUMBER_OF_USERS)

        profiles = []

        for user in self.created_users:
            profile = UserProfile(
                user=user,
                job_title=fake.job(),
                department=fake.word(),
                phone=fake.phone_number(),
                bio=fake.sentence(),
            )

            profiles.append(profile)

        UserProfile.objects.bulk_create(profiles, batch_size=NUMBER_OF_USERS)

        user_activities = []

        for user in self.created_users:
            activity = UserActivity(
                user=user,
                action=UserActivityActionChoices.LOGIN,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                session_key=fake.uuid4(),
                created_at=fake.date(),
            )

            user_activities.append(activity)

        UserActivity.objects.bulk_create(user_activities, batch_size=NUMBER_OF_USERS)

        self.create_addresses()
        self.create_projects()
        self.create_approval_groups()
        self.create_approval_chains()
        self.create_service_requisitions()
        self.create_goods_requisitions()

    def create_addresses(self, *args, **kwargs):
        addresses = []

        for _ in range(NUMBER_OF_ADDRESSES):
            user = random.choice(self.created_users)

            address = Address(
                name=f"{fake.word()}{fake.random_number(digits=6)}",
                address_code=fake.uuid4(),
                description=fake.sentence(),
                attention=f"{user.first_name} {user.last_name}",
                phone=fake.basic_phone_number(),
                street1=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.postcode(),
                country=fake.current_country_code(),
                delivery_instructions=fake.sentence(),
                owner=user,
                created_at=fake.date(),
                created_by=user,
                updated_at=fake.date(),
                updated_by=user,
            )

            addresses.append(address)

        self.created_addresses = Address.objects.bulk_create(
            addresses, batch_size=NUMBER_OF_ADDRESSES
        )

    def create_projects(self, *args, **kwargs):
        projects = []

        for _ in range(NUMBER_OF_PROJECTS):
            user = random.choice(self.created_users)

            project = Project(
                name=f"{fake.word()}{fake.random_number(digits=6)}",
                project_code=fake.uuid4(),
                description=fake.sentence(),
                start_date=fake.date(pattern="%Y-%m-%d"),
                end_date=fake.date(pattern="%Y-%m-%d"),
                created_at=fake.date(),
                created_by=user,
                updated_at=fake.date(),
                updated_by=user,
            )

            projects.append(project)

        self.created_projects = Project.objects.bulk_create(projects, batch_size=NUMBER_OF_PROJECTS)

    def create_approval_groups(self, *args, **kwargs):
        groups = []

        for _ in range(NUMBER_OF_APPROVAL_GROUPS):
            user1, user2 = random.sample(self.created_users, 2)

            group = ApprovalGroup.objects.create(
                name=f"{fake.word()}{fake.random_number(digits=6)}",
                description=fake.sentence(),
            )

            group.approver.add(user1, user2)

            groups.append(group)

        self.created_approval_groups = groups

    def create_approval_chains(self, *args, **kwargs):
        approval_chains = []

        user = random.choice(self.created_users)
        group = random.choice(self.created_approval_groups)

        approval_chain1 = ApprovalChain.objects.create(
            name=f"{fake.word()}{fake.random_number(digits=6)}",
            approver_mode=ApprovalChainModeChoices.GROUP,
            approver_group=group,
            sequence_number=1,
            min_amount=Decimal("0.01"),
            active=True,
        )

        approval_chain2 = ApprovalChain.objects.create(
            name=f"{fake.word()}{fake.random_number(digits=6)}",
            approver_mode=ApprovalChainModeChoices.INDIVIDUAL,
            approver=user,
            sequence_number=2,
            min_amount=Decimal("0.01"),
            active=True,
        )

        approval_chains.append(approval_chain1)
        approval_chains.append(approval_chain2)

        self.created_approval_chains = approval_chains

    def create_service_requisitions(self, *args, **kwargs):
        requisitions = []
        lines = []

        for _ in range(NUMBER_OF_SERVICE_REQUISITIONS):
            user = random.choice(self.created_users)
            project = random.choice(self.created_projects)
            currency = random.choice(CURRENCY)

            requisition = Requisition(
                name=f"{fake.word()}{fake.random_number(digits=6)}",
                external_reference=fake.uuid4(),
                status=RequisitionStatusChoices.DRAFT,
                owner=user,
                project=project,
                supplier=fake.company(),
                justification=fake.sentence(),
                total_amount=Decimal(100),
                currency=currency,
                created_at=fake.date(),
                created_by=user,
                updated_at=fake.date(),
                updated_by=user,
            )

            requisitions.append(requisition)

        created_requisitions = Requisition.objects.bulk_create(
            requisitions, batch_size=NUMBER_OF_SERVICE_REQUISITIONS
        )

        for requisition in created_requisitions:
            category = random.choice(CATEGORIES)
            address = random.choice(self.created_addresses)
            payment_term = random.choice(PAYMENT_TERMS)

            line = RequisitionLine(
                line_number=1,
                line_type=LineTypeChoices.SERVICE,
                description=fake.sentence(),
                category=category,
                line_total=Decimal(50),
                payment_term=payment_term,
                need_by=fake.future_date(),
                created_at=fake.date(),
                created_by=requisition.owner,
                updated_at=fake.date(),
                updated_by=requisition.owner,
                requisition=requisition,
                ship_to=address,
            )

            lines.append(line)

            line = RequisitionLine(
                line_number=2,
                line_type=LineTypeChoices.SERVICE,
                description=fake.sentence(),
                category=category,
                line_total=Decimal(50),
                payment_term=payment_term,
                need_by=fake.future_date(),
                created_at=fake.date(),
                created_by=requisition.owner,
                updated_at=fake.date(),
                updated_by=requisition.owner,
                requisition=requisition,
                ship_to=address,
            )

            lines.append(line)

        RequisitionLine.objects.bulk_create(lines, batch_size=NUMBER_OF_SERVICE_REQUISITIONS * 2)

    def create_goods_requisitions(self, *args, **kwargs):
        requisitions = []
        lines = []

        for _ in range(NUMBER_OF_GOODS_REQUISITIONS):
            user = random.choice(self.created_users)
            project = random.choice(self.created_projects)
            currency = random.choice(CURRENCY)

            requisition = Requisition(
                name=f"{fake.word()}{fake.random_number(digits=6)}",
                external_reference=fake.uuid4(),
                status=RequisitionStatusChoices.DRAFT,
                owner=user,
                project=project,
                supplier=fake.company(),
                justification=fake.sentence(),
                total_amount=Decimal(100),
                currency=currency,
                created_at=fake.date(),
                created_by=user,
                updated_at=fake.date(),
                updated_by=user,
            )

            requisitions.append(requisition)

        created_requisitions = Requisition.objects.bulk_create(
            requisitions, batch_size=NUMBER_OF_GOODS_REQUISITIONS
        )

        for requisition in created_requisitions:
            category = random.choice(CATEGORIES)
            address = random.choice(self.created_addresses)
            payment_term = random.choice(PAYMENT_TERMS)
            unit_of_measure = random.choice(UOM)

            line = RequisitionLine(
                line_number=1,
                line_type=LineTypeChoices.GOODS,
                description=fake.sentence(),
                category=category,
                manufacturer=fake.company(),
                manufacturer_part_number=fake.ean(length=8),
                quantity=2,
                unit_of_measure=unit_of_measure,
                unit_price=Decimal(25),
                line_total=Decimal(50),
                payment_term=payment_term,
                need_by=fake.future_date(),
                created_at=fake.date(),
                created_by=requisition.owner,
                updated_at=fake.date(),
                updated_by=requisition.owner,
                requisition=requisition,
                ship_to=address,
            )

            lines.append(line)

            line = RequisitionLine(
                line_number=2,
                line_type=LineTypeChoices.GOODS,
                description=fake.sentence(),
                category=category,
                manufacturer=fake.company(),
                manufacturer_part_number=fake.ean(length=8),
                quantity=4,
                unit_of_measure=unit_of_measure,
                unit_price=Decimal("12.50"),
                line_total=Decimal(50),
                payment_term=payment_term,
                need_by=fake.future_date(),
                created_at=fake.date(),
                created_by=requisition.owner,
                updated_at=fake.date(),
                updated_by=requisition.owner,
                requisition=requisition,
                ship_to=address,
            )

            lines.append(line)

        RequisitionLine.objects.bulk_create(lines, batch_size=NUMBER_OF_GOODS_REQUISITIONS * 2)

import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from purly.address.models import Address
from purly.project.models import Project
from purly.requisition.models import Requisition, RequisitionLine, StatusChoices
from purly.user.models import User

fake = Faker("en_US")

NUMBER_OF_USERS = 100
NUMBER_OF_ADDRESSES = 250
NUMBER_OF_PROJECTS = 30
NUMBER_OF_SERVICE_REQUISITIONS = 500
NUMBER_OF_GOODS_REQUISITIONS = 500

CURRENCY = ["usd"]
CATEGORIES = ["Advertising", "IT", "Food", "Furniture", "Vehicle Rental"]
PAYMENT_TERMS = ["net_30", "net_45", "net_90"]
UOM = ["each", "box"]


class Command(BaseCommand):
    created_users = []
    created_addresses = []
    created_projects = []

    def handle(self, *args, **kwargs):
        users = []

        usernames = [fake.unique.user_name() for _ in range(NUMBER_OF_USERS)]

        for i in range(NUMBER_OF_USERS):
            user = User(
                username=f"{usernames[i]}{fake.random_number(digits=6)}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=fake.sha256(),
            )

            users.append(user)

        self.created_users = User.objects.bulk_create(users, batch_size=NUMBER_OF_USERS)

        self.create_addresses()
        self.create_projects()
        self.create_service_requisitions()
        self.create_goods_requisitions()

    def create_addresses(self, *args, **kwargs):
        addresses = []

        for _ in range(NUMBER_OF_ADDRESSES):
            user = random.choice(self.created_users)

            address = Address(
                name=fake.word(),
                address_code=fake.uuid4(),
                description=fake.sentence(),
                attention=f"{user.first_name} {user.last_name}",
                phone=fake.basic_phone_number(),
                street1=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.postcode(),
                country=fake.current_country_code(),
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
                name=fake.word(),
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

    def create_service_requisitions(self, *args, **kwargs):
        requisitions = []
        lines = []

        for _ in range(NUMBER_OF_SERVICE_REQUISITIONS):
            user = random.choice(self.created_users)
            project = random.choice(self.created_projects)
            currency = random.choice(CURRENCY)

            requisition = Requisition(
                name=fake.word(),
                external_reference=fake.uuid4(),
                status=StatusChoices.PENDING_APPROVAL,
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
                line_type="service",
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
                line_type="service",
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
                name=fake.word(),
                external_reference=fake.uuid4(),
                status=StatusChoices.PENDING_APPROVAL,
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
                line_type="goods",
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
                line_type="goods",
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

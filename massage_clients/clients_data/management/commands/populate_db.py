import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from ...models import Client, Visit, Payment


class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')  # Russian language for names
        for _ in range(50):
            name = fake.first_name() + ' ' + fake.last_name()
            phone_number = '0' + ''.join(random.choices('0123456789', k=9))
            sex = random.choice(['М', 'Ж'])
            age = random.randint(20, 80)
            illnesses = fake.paragraph()
            more_info = fake.paragraph()
            balance = random.randint(0, 10000)
            deposit = random.randint(0, 1000)

            client = Client.objects.create(
                name=name,
                phone_number=phone_number,
                sex=sex,
                age=age,
                illnesses=illnesses,
                more_info=more_info,
                balance=balance,
                deposit=deposit
            )

            # Create payment records for the client
            for _ in range(random.randint(1, 5)):
                payment_date = timezone.now() - timezone.timedelta(days=random.randint(1, 1095))
                pay_amount = random.randint(1000, 20000)
                Payment.objects.create(client=client, payment_date=payment_date, pay_amount=pay_amount)

            # Create visit records for the client
            for _ in range(random.randint(1, 5)):
                visit_date = timezone.datetime(2023, 9, random.randint(1, 30), random.randint(8, 19), 0)
                visit_time = visit_date.time()
                massage_type = random.choice(['spine', 'neck', 'total', 'anti-cellulite', 'hands', 'chest', 'legs'])
                visit_price = random.randint(1000, 5000)
                Visit.objects.create(
                    client=client,
                    visit_date=visit_date,
                    visit_time=visit_time,
                    massage_type=massage_type,
                    visit_price=visit_price,
                    completed=True
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully created data for client: {name}'))

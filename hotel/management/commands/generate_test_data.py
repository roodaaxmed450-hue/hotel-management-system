import random
import string
from django.core.management.base import BaseCommand
from django.utils import timezone
from hotel.models import User, Room, Guest, Booking, Payment, Expense, AdditionalCharge
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate 100 test data entries for each major model'

    def handle(self, *args, **kwargs):
        user = User.objects.filter(role='admin').first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found. Please create a user first.'))
            return

        # 1. Generate 100 Rooms
        self.stdout.write('Generating 100 Rooms...')
        room_types = ['Single', 'Family']
        current_rooms_count = Room.objects.count()
        for i in range(1, 101):
            room_number = f"R{i + 100 + current_rooms_count}" 
            # Check if room number already exists to avoid unique constraint error
            if not Room.objects.filter(room_number=room_number).exists():
                Room.objects.create(
                    room_number=room_number,
                    room_type=random.choice(room_types),
                    price_per_night=Decimal(random.randint(50, 200)),
                    capacity=random.randint(1, 4),
                    status='Available'
                )

        # 2. Generate 100 Guests
        self.stdout.write('Generating 100 Guests...')
        for i in range(1, 101):
            Guest.objects.create(
                full_name=f"Test Guest {random.randint(1000, 9999)} {i}",
                phone_number=f"252-{random.randint(100000, 999999)}",
                id_card=f"ID-{random.randint(1000, 9999)}",
                address=f"Street {i}, Mogadishu"
            )

        # 3. Generate 100 Bookings
        self.stdout.write('Generating 100 Bookings...')
        guests = list(Guest.objects.all().order_by('-id')[:100])
        rooms = list(Room.objects.all().order_by('-id')[:100])
        statuses = ['Reserved', 'Confirmed', 'Checked-In', 'Checked-Out']
        
        created_bookings = []
        for i in range(100):
            guest = random.choice(guests)
            room = random.choice(rooms)
            check_in = timezone.now().date() + timedelta(days=random.randint(-30, 30))
            check_out = check_in + timedelta(days=random.randint(1, 10))
            
            # Simple check to avoid overlapping bookings for the same room (basic)
            # Actually for test data we might not care as much, but let's try to be somewhat realistic
            booking = Booking.objects.create(
                guest=guest,
                room=room,
                number_of_guests=random.randint(1, room.capacity if room.capacity > 0 else 1),
                check_in_date=check_in,
                check_out_date=check_out,
                status=random.choice(statuses),
                notes=f"Test booking {i}"
            )
            created_bookings.append(booking)

        # 4. Generate 100 Payments
        self.stdout.write('Generating 100 Payments...')
        payment_types = ['Deposit', 'Payment']
        payment_methods = ['Cash', 'Mobile', 'Bank', 'Card']
        
        for i in range(100):
            booking = random.choice(created_bookings)
            Payment.objects.create(
                booking=booking,
                payment_type=random.choice(payment_types),
                amount=Decimal(random.randint(20, 100)),
                payment_method=random.choice(payment_methods),
                recorded_by=user,
                notes=f"Test payment {i}"
            )

        # 5. Generate 100 Expenses
        self.stdout.write('Generating 100 Expenses...')
        categories = ['Maintenance', 'Food', 'Utility', 'Salary']
        expense_statuses = ['Pending', 'Approved']
        
        for i in range(1, 101):
            Expense.objects.create(
                title=f"Test Expense {i}",
                category=random.choice(categories),
                amount=Decimal(random.randint(10, 500)),
                date=timezone.now().date() - timedelta(days=random.randint(0, 60)),
                status=random.choice(expense_statuses),
                created_by=user
            )

        # 6. Generate 100 Additional Charges
        self.stdout.write('Generating 100 Additional Charges...')
        charge_types = ['Minibar', 'Room Service', 'Laundry', 'Restaurant']
        
        for i in range(100):
            booking = random.choice(created_bookings)
            AdditionalCharge.objects.create(
                booking=booking,
                charge_type=random.choice(charge_types),
                description=f"Extra service {i}",
                amount=Decimal(random.randint(5, 50)),
                added_by=user
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated 100 entries for all major models.'))

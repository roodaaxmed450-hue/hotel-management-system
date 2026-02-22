"""
Complete Hotel Management System Test
Testing workflow for three arriving guests:
1. Mohamed Ahmed Ali
2. Idiris Abdi Aadan
3. Suhayb Aadan Ahmed
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khms.settings')
django.setup()

from hotel.models import User, Room, Guest, Booking, Payment, Invoice
from django.utils import timezone

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_system():
    """Run complete system test"""
    
    print_section("HOTEL MANAGEMENT SYSTEM - COMPLETE TEST")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check System Status
    print_section("STEP 1: System Status Check")
    users = User.objects.all()
    rooms = Room.objects.all()
    print(f"[OK] Total Users: {users.count()}")
    print(f"[OK] Total Rooms: {rooms.count()}")
    
    # Show available rooms
    available_rooms = Room.objects.filter(status='Available')
    print(f"[OK] Available Rooms: {available_rooms.count()}")
    if available_rooms.exists():
        print("\nAvailable Rooms:")
        for room in available_rooms[:5]:
            print(f"  - Room {room.room_number}: {room.room_type} (${room.price_per_night}/night)")
    
    # Step 2: Create Three Guests
    print_section("STEP 2: Creating Three Guests")
    
    guests_data = [
        {
            'full_name': 'Mohamed Ahmed Ali',
            'phone_number': '+252-61-1234567',
            'id_card': 'ID001234',
            'address': 'Mogadishu, Somalia'
        },
        {
            'full_name': 'Idiris Abdi Aadan',
            'phone_number': '+252-61-2345678',
            'id_card': 'ID002345',
            'address': 'Hargeisa, Somalia'
        },
        {
            'full_name': 'Suhayb Aadan Ahmed',
            'phone_number': '+252-61-3456789',
            'id_card': 'ID003456',
            'address': 'Kismayo, Somalia'
        }
    ]
    
    created_guests = []
    for guest_data in guests_data:
        # Check if guest already exists
        guest, created = Guest.objects.get_or_create(
            full_name=guest_data['full_name'],
            defaults=guest_data
        )
        created_guests.append(guest)
        status = "Created" if created else "Already exists"
        print(f"✓ {status}: {guest.full_name} - {guest.phone_number}")
    
    # Step 3: Create Bookings for Each Guest
    print_section("STEP 3: Creating Bookings")
    
    check_in_date = timezone.now().date()
    check_out_date = check_in_date + timedelta(days=3)
    
    print(f"Check-in Date: {check_in_date}")
    print(f"Check-out Date: {check_out_date}")
    print(f"Duration: 3 nights\n")
    
    created_bookings = []
    for i, guest in enumerate(created_guests):
        # Get an available room
        room = available_rooms[i] if i < available_rooms.count() else available_rooms.first()
        
        # Create booking
        booking, created = Booking.objects.get_or_create(
            guest=guest,
            room=room,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            defaults={'status': 'Confirmed'}
        )
        
        if created:
            # Update room status
            room.status = 'Booked'
            room.save()
        
        created_bookings.append(booking)
        status = "Created" if created else "Already exists"
        print(f"✓ {status} Booking #{booking.id}")
        print(f"  Guest: {guest.full_name}")
        print(f"  Room: {room.room_number} ({room.room_type})")
        print(f"  Total Amount: ${booking.get_net_total()}")
        print()
    
    # Step 4: Check-In Process
    print_section("STEP 4: Check-In Process")
    
    for booking in created_bookings:
        if booking.status in ['Pending', 'Confirmed']:
            booking.status = 'Checked-In'
            booking.room.status = 'Occupied'
            booking.room.save()
            booking.save()
            print(f"✓ Checked-In: {booking.guest.full_name}")
            print(f"  Room {booking.room.room_number} is now OCCUPIED")
        else:
            print(f"⚠ {booking.guest.full_name} already checked in")
        print()
    
    # Step 5: Generate Invoices
    print_section("STEP 5: Invoice Generation")
    
    for booking in created_bookings:
        invoice, created = Invoice.objects.get_or_create(booking=booking)
        status = "Generated" if created else "Already exists"
        print(f"✓ {status} Invoice for {booking.guest.full_name}")
        print(f"  Total Amount: ${invoice.total_amount}")
        print(f"  Amount Paid: ${invoice.amount_paid}")
        print(f"  Balance: ${invoice.balance}")
        print(f"  Status: {invoice.status}")
        print()
    
    # Step 6: Process Payments
    print_section("STEP 6: Payment Processing")
    
    # Get the receptionist or admin user
    user = User.objects.filter(role='admin').first() or User.objects.first()
    
    for i, booking in enumerate(created_bookings):
        # Pay full amount for first guest, partial for second, none for third
        if i == 0:
            # Full payment
            payment_amount = booking.get_net_total()
            payment_method = 'Cash'
        elif i == 1:
            # Partial payment (50%)
            payment_amount = booking.get_net_total() / 2
            payment_method = 'Mobile'
        else:
            # No payment yet
            payment_amount = 0
            payment_method = None
        
        if payment_amount > 0:
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                amount=payment_amount,
                defaults={
                    'payment_method': payment_method,
                    'recorded_by': user
                }
            )
            status = "Recorded" if created else "Already exists"
            print(f"✓ {status} Payment for {booking.guest.full_name}")
            print(f"  Amount: ${payment.amount}")
            print(f"  Method: {payment.payment_method}")
            print(f"  Recorded by: {user.username}")
        else:
            print(f"⚠ No payment for {booking.guest.full_name} (Balance: ${booking.get_net_total()})")
        print()
    
    # Step 7: Check-Out First Guest
    print_section("STEP 7: Check-Out Process")
    
    first_booking = created_bookings[0]
    if first_booking.status == 'Checked-In':
        first_booking.status = 'Checked-Out'
        first_booking.room.status = 'Available'
        first_booking.room.save()
        first_booking.save()
        print(f"✓ Checked-Out: {first_booking.guest.full_name}")
        print(f"  Room {first_booking.room.room_number} is now AVAILABLE")
        print(f"  Final Amount: ${first_booking.get_actual_total()}")
        print(f"  Payment Status: {first_booking.invoice.status}")
    else:
        print(f"⚠ {first_booking.guest.full_name} is not checked in")
    
    # Step 8: System Summary
    print_section("STEP 8: Final System Summary")
    
    total_bookings = Booking.objects.count()
    checked_in = Booking.objects.filter(status='Checked-In').count()
    checked_out = Booking.objects.filter(status='Checked-Out').count()
    total_revenue = sum(b.get_net_total() for b in Booking.objects.all())
    total_payments = sum(p.amount for p in Payment.objects.all())
    
    print(f"Total Bookings: {total_bookings}")
    print(f"Currently Checked-In: {checked_in}")
    print(f"Checked-Out: {checked_out}")
    print(f"Total Revenue: ${total_revenue}")
    print(f"Total Payments Received: ${total_payments}")
    print(f"Outstanding Balance: ${total_revenue - total_payments}")
    
    # Room Status
    print("\nRoom Status:")
    for status in ['Available', 'Occupied', 'Booked', 'Maintenance']:
        count = Room.objects.filter(status=status).count()
        if count > 0:
            print(f"  {status}: {count}")
    
    # Guest Details
    print("\nCurrent Guests:")
    current_bookings = Booking.objects.filter(status='Checked-In')
    for booking in current_bookings:
        print(f"  - {booking.guest.full_name} in Room {booking.room.room_number}")
    
    print_section("TEST COMPLETED SUCCESSFULLY")
    print("All three guests have been processed through the system!")
    print("\nNext Steps:")
    print("1. Login to the web interface at http://localhost:8000")
    print("2. View the dashboard to see updated statistics")
    print("3. Check bookings list to see all three guests")
    print("4. View reports to see revenue summary")
    print("5. Process remaining check-outs when ready")

if __name__ == '__main__':
    try:
        test_system()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

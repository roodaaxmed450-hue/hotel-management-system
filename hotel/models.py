from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Default queryset excludes both soft-deleted and permanently archived items
        return super().get_queryset().filter(is_deleted=False, is_permanently_deleted=False)

    def deleted(self):
        # Items in the recycle bin: marked as deleted but NOT yet permanently archived
        return super().get_queryset().filter(is_deleted=True, is_permanently_deleted=False)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    is_permanently_deleted = models.BooleanField(default=False) # For archiving items with history
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.is_permanently_deleted = False
        self.deleted_at = None
        self.save()

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin/Owner'),
        ('receptionist', 'Receptionist'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_receptionist(self):
        return self.role == 'receptionist'

class Room(SoftDeleteModel):
    ROOM_TYPES = (
        ('Single', 'Single'),
        ('Family', 'Family'),
    )
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Booked', 'Reserved'),
        ('Occupied', 'Checked-In'),
        ('Maintenance', 'Maintenance'),
    )
    room_number = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available', db_index=True)

    @property
    def display_room_number(self):
        """Returns the clean room number without the archiving suffix"""
        if "_archived_" in self.room_number:
            return self.room_number.split("_archived_")[0]
        return self.room_number

    def __str__(self):
        return f"{self.display_room_number} - {self.get_room_type_display()}"

class Guest(SoftDeleteModel):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    id_card = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Booking(SoftDeleteModel):
    STATUS_CHOICES = (
        ('Reserved', 'Reserved'),
        ('Confirmed', 'Confirmed'),
        ('Checked-In', 'Checked-In'),
        ('Checked-Out', 'Checked-Out'),
        ('No-Show', 'No-Show'),
        ('Cancelled', 'Cancelled'),
    )
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    number_of_guests = models.PositiveIntegerField(default=1)
    
    # Planned dates (for reservation)
    check_in_date = models.DateField(db_index=True)
    check_out_date = models.DateField(db_index=True)
    
    # Actual timestamps (for billing)
    actual_checkin = models.DateTimeField(null=True, blank=True)
    actual_checkout = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed', db_index=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    
    # Room rate at booking time (locked in)
    room_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deposit
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Discount
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Lock in room rate if not set
        if not self.room_rate and self.room:
            from decimal import Decimal
            if self.room.room_type == 'Single':
                if self.number_of_guests == 1:
                    self.room_rate = Decimal('8.00')
                elif self.number_of_guests == 2:
                    self.room_rate = Decimal('12.00')
                else:
                    self.room_rate = Decimal('12.00') # Fallback, validation should catch this
            elif self.room.room_type == 'Family':
                self.room_rate = Decimal('16.00')
            else:
                # Default fallback to room's default price if any
                self.room_rate = self.room.price_per_night
        
        # Calculate deposit (30% of estimated total)
        if not self.deposit_amount:
            estimated_days = (self.check_out_date - self.check_in_date).days
            if estimated_days < 1:
                estimated_days = 1
            estimated_total = estimated_days * self.room_rate
            from decimal import Decimal
            self.deposit_amount = estimated_total * Decimal('0.30')
        
        super().save(*args, **kwargs)
    
    def get_room_charges(self):
        """Room charges based on duration and rate"""
        if self.status == 'Cancelled':
            from decimal import Decimal
            return Decimal('0.00')
        
        # Base calculation: Use actual times if available (Checked-Out), else planned dates
        if self.actual_checkin and self.actual_checkout:
            import math
            time_diff = self.actual_checkout - self.actual_checkin
            hours = time_diff.total_seconds() / 3600
            days = math.ceil(hours / 24)
            if days < 1:
                days = 1
            return days * self.room_rate
        else:
            # Fallback to planned duration if not checked out yet
            days = (self.check_out_date - self.check_in_date).days
            if days < 1:
                days = 1
            return days * self.room_rate
    
    @property
    def total_additional_charges(self):
        """Total sum of all additional charges"""
        return sum(charge.amount for charge in self.additional_charges.all())

    def get_total_gross(self):
        """Total before any discounts (Room + Services)"""
        return self.get_room_charges() + self.total_additional_charges

    def get_total_discounted(self):
        """All discounts (flat field + ledger entries)"""
        ledger_discounts = sum(p.amount for p in self.payments.filter(payment_type='Discount'))
        return self.discount + ledger_discounts

    def get_total_paid(self):
        """Total cash collected (Deposits + Payments)"""
        return sum(p.amount for p in self.payments.filter(payment_type__in=['Deposit', 'Payment']))

    def get_total_refunded(self):
        """Total cash returned"""
        return sum(p.amount for p in self.payments.filter(payment_type='Refund'))

    def get_net_total(self):
        """Final amount guest is expected to pay (Gross - Discounts)"""
        return self.get_total_gross() - self.get_total_discounted()

    def get_balance(self):
        """Outstanding amount (Net Total - (Paid - Refunded))"""
        if self.status == 'Cancelled':
            # For cancelled bookings, we check if there's any un-refunded money
            # If paid 100 and refunded 0, balance is -100 (hotel owes guest or guest has credit)
            # If paid 100 and refunded 100, balance is 0.
            return self.get_net_total() - (self.get_total_paid() - self.get_total_refunded())
            
        return self.get_net_total() - (self.get_total_paid() - self.get_total_refunded())

    def get_actual_total(self):
        """Legacy helper for backward compatibility - returns Net Total"""
        return self.get_net_total()
    
    def get_payment_status(self):
        """Payment status"""
        balance = self.get_balance()
        paid = self.get_total_paid()
        
        if self.status in ['Reserved', 'Confirmed']:
            if paid >= self.deposit_amount:
                return 'Deposit Paid'
            else:
                return 'Deposit Pending'
        elif self.status in ['Checked-In', 'Checked-Out']:
            if balance <= 0:
                return 'Fully Paid'
            elif paid > 0:
                return 'Partially Paid'
            else:
                return 'Unpaid'
        return 'N/A'

    @property
    def is_overdue(self):
        """Check if booking is overdue for checkout"""
        if self.status != 'Checked-In':
            return False
        return self.check_out_date <= timezone.now().date()

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.room:
            # number_of_guests must not exceed room.capacity
            if self.number_of_guests > self.room.capacity:
                raise ValidationError(f"Number of guests ({self.number_of_guests}) exceeds room capacity ({self.room.capacity}).")
            
            # Single rooms must reject more than 2 guests
            if self.room.room_type == 'Single' and self.number_of_guests > 2:
                raise ValidationError("Single rooms cannot accommodate more than 2 guests.")

        if self.pk:
            old_instance = Booking.objects.get(pk=self.pk)
            # Prevent occupancy changes once booking status is Confirmed or Checked-In
            if old_instance.status in ['Confirmed', 'Checked-In'] and old_instance.number_of_guests != self.number_of_guests:
                raise ValidationError("Occupancy (number of guests) cannot be modified once a booking is Confirmed or Checked-In.")
            
            # If a single room is booked for 1 guest, it is fully reserved and cannot later be converted to 2 guests.
            if self.room.room_type == 'Single' and old_instance.number_of_guests == 1 and self.number_of_guests > 1:
                 raise ValidationError("This single room was booked for 1 guest and is now locked. It cannot be converted to 2 guests.")

    def __str__(self):
        return f"Booking {self.id} - {self.guest.full_name}"

class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import uuid
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        return self.booking.get_net_total()
    
    @property
    def amount_paid(self):
        """Net amount collected (Paid - Refunded)"""
        return self.booking.get_total_paid() - self.booking.get_total_refunded()
    
    @property
    def amount_discounted(self):
        return self.booking.get_total_discounted()
    
    @property
    def balance(self):
        return self.booking.get_balance()
    
    @property
    def status(self):
        return self.booking.get_payment_status()

class Payment(SoftDeleteModel):
    PAYMENT_TYPE_CHOICES = (
        ('Deposit', 'Deposit'),
        ('Payment', 'Payment'),
        ('Refund', 'Refund'),
        ('Discount', 'Discount'),
        ('Adjustment', 'Adjustment'),
    )
    
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Mobile', 'Mobile Money'),
        ('Bank', 'Bank Transfer'),
        ('Card', 'Credit/Debit Card'),
    )
    
    booking = models.ForeignKey(Booking, related_name='payments', on_delete=models.PROTECT)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='Payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    reference_number = models.CharField(max_length=50, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import uuid
            self.reference_number = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_payment_type_display()} - ${self.amount} ({self.booking.guest.full_name})"

class Expense(SoftDeleteModel):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, related_name='approved_expenses', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

class AdditionalCharge(models.Model):
    CHARGE_TYPE_CHOICES = (
        ('Minibar', 'Minibar'),
        ('Room Service', 'Room Service'),
        ('Laundry', 'Laundry'),
        ('Restaurant', 'Restaurant'),
        ('Spa', 'Spa Services'),
        ('Damage', 'Damage Charge'),
        ('Late Checkout', 'Late Checkout Fee'),
        ('Other', 'Other'),
    )
    
    booking = models.ForeignKey(Booking, related_name='additional_charges', on_delete=models.PROTECT)
    charge_type = models.CharField(max_length=50, choices=CHARGE_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_charge_type_display()} - ${self.amount}"

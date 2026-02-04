from django import forms
from .models import Guest, Booking, Payment, Expense, Room, User

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['full_name', 'phone_number', 'id_card', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'id_card': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'address': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest', 'room', 'check_in_date', 'check_out_date']
        widgets = {
            'guest': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'room': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'check_in_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')

        if check_in and check_out and room:
            # Simple overlap check
            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).exclude(status='Cancelled')
            if self.instance.pk:
                 overlapping_bookings = overlapping_bookings.exclude(pk=self.instance.pk)
            
            if overlapping_bookings.exists():
                raise forms.ValidationError("Room is already booked for these dates.")
        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded', 'step': '0.01'}),
            'payment_type': forms.Select(attrs={'class': 'w-full p-2 border rounded', 'id': 'id_payment_type'}),
            'payment_method': forms.Select(attrs={'class': 'w-full p-2 border rounded', 'id': 'id_payment_method'}),
            'notes': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': 'Reason for discount/payment notes'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'category', 'amount', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'category': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night', 'capacity', 'status']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'room_type': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.instance and self.instance.pk:
            # Check for active bookings associated with this room
            from .models import Booking
            active_booking = Booking.objects.filter(
                room=self.instance,
                status__in=['Checked-In', 'Confirmed']
            ).exists()

            # If the room is currently managed by the booking system (Occupied or Booked)
            # we block manual status overrides that bypass the check-out/cancellation flow.
            if active_booking:
                if status == 'Available':
                    raise forms.ValidationError(
                        "integrity Error: This room is currently active in the booking system. "
                        "You cannot manually set it to 'Available' until the guest is checked out."
                    )
                if status == 'Maintenance':
                    raise forms.ValidationError(
                        "Safety Alert: Cannot put an active/occupied room into maintenance. "
                        "Please check-out or relocate the guest first."
                    )
            
            # If the room was already in maintenance and we are making it available, that's fine.
            # But we should not allow making a room 'Booked' or 'Occupied' manually without a booking.
            if not active_booking and status in ['Booked', 'Occupied']:
                raise forms.ValidationError(
                    "Workflow Error: You cannot manually set a room to 'Booked' or 'Occupied'. "
                    "These statuses are automatically handled when you create a new reservation or check-in a guest."
                )

        return status

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2 border rounded'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded'}),
            'role': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

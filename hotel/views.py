from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from .models import Room, Booking, Payment, Expense, Guest, Invoice, User
from .forms import BookingForm, GuestForm, PaymentForm, ExpenseForm, RoomForm, UserForm

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return admin_dashboard(request)
    else:
        return receptionist_dashboard(request)

def admin_dashboard(request):
    total_rooms = Room.objects.count()
    occupied_count = Room.objects.filter(status='Occupied').count()
    booked_count = Room.objects.filter(status='Booked').count()
    available_count = Room.objects.filter(status='Available').count()
    maintenance_count = Room.objects.filter(status='Maintenance').count()
    
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0
    
    today = timezone.now().date()
    todays_income = Payment.objects.filter(date__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Expense.objects.filter(status='Approved').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_expenses = Expense.objects.filter(status='Pending').count()
    
    monthly_income = Payment.objects.filter(date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = Expense.objects.filter(date__month=today.month, date__year=today.year, status='Approved').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_profit = monthly_income - monthly_expenses

    # Recent Activity
    recent_bookings = Booking.objects.order_by('-booking_date')[:5]
    
    # Financial Chart Data: Last 6 months
    from datetime import datetime, timedelta
    chart_labels = []
    income_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        
        month_name = datetime(y, m, 1).strftime('%b')
        chart_labels.append(month_name)
        
        inc = Payment.objects.filter(date__year=y, date__month=m).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Expense.objects.filter(date__year=y, date__month=m, status='Approved').aggregate(Sum('amount'))['amount__sum'] or 0
        
        income_data.append(float(inc))
        expense_data.append(float(exp))

    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_count,
        'available_rooms': available_count,
        'booked_rooms': booked_count,
        'maintenance_rooms': maintenance_count,
        'occupancy_rate': round(occupancy_rate, 1),
        'todays_income': todays_income,
        'total_expenses': total_expenses,
        'pending_expenses': pending_expenses,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_profit': monthly_profit,
        'bookings_count': Booking.objects.filter(booking_date__month=today.month, booking_date__year=today.year).count(),
        'chart_labels': chart_labels,
        'chart_income': income_data,
        'chart_expenses': expense_data,
        'recent_bookings': recent_bookings,
        'room_status_counts': [
            {'status': 'Available', 'count': available_count, 'percentage': round((available_count/total_rooms*100), 1) if total_rooms > 0 else 0},
            {'status': 'Occupied', 'count': occupied_count, 'percentage': round((occupied_count/total_rooms*100), 1) if total_rooms > 0 else 0},
            {'status': 'Booked', 'count': booked_count, 'percentage': round((booked_count/total_rooms*100), 1) if total_rooms > 0 else 0},
            {'status': 'Maintenance', 'count': maintenance_count, 'percentage': round((maintenance_count/total_rooms*100), 1) if total_rooms > 0 else 0},
        ]
    }
    return render(request, 'hotel/admin_dashboard.html', context)

def receptionist_dashboard(request):
    today = timezone.now().date()
    
    # KPIs
    available_rooms_count = Room.objects.filter(status='Available').count()
    arrivals_today = Booking.objects.filter(check_in_date=today).count()
    checkouts_due = Booking.objects.filter(check_out_date=today, status='Checked-In').count()
    total_collected_today = Payment.objects.filter(date__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent bookings for list
    recent_bookings = Booking.objects.order_by('-booking_date')[:5]
    
    # All Rooms for the grid
    all_rooms = Room.objects.all().order_by('room_number')
    
    context = {
        'all_rooms': all_rooms,
        'available_rooms_count': available_rooms_count,
        'arrivals_today': arrivals_today,
        'checkouts_due': checkouts_due,
        'total_collected_today': total_collected_today,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'hotel/receptionist_dashboard.html', context)

@login_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'hotel/room_list.html', {'rooms': rooms})

@login_required
def guest_list(request):
    guests = Guest.objects.all()
    return render(request, 'hotel/guest_list.html', {'guests': guests})

@login_required
def add_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guest added successfully')
            return redirect('guest_list')
    else:
        form = GuestForm()
    return render(request, 'hotel/guest_form.html', {'form': form})

@login_required
def edit_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guest updated successfully')
            return redirect('guest_list')
    else:
        form = GuestForm(instance=guest)
    return render(request, 'hotel/guest_form.html', {'form': form, 'edit_mode': True})

@login_required
@login_required
def delete_guest(request, guest_id):
    if request.user.role != 'admin':
        messages.error(request, 'Security Alert: Only administrators can remove guest profiles.')
        return redirect('guest_list')
        
    guest = get_object_or_404(Guest, id=guest_id)
    # Check if guest has active stay or future reservations
    active_reservations = guest.bookings.exclude(status__in=['Checked-Out', 'Cancelled'])
    if active_reservations.exists():
        messages.error(request, 'integrity Error: Cannot delete a guest who has an active stay or upcoming reservation.')
    else:
        guest.soft_delete()
        messages.success(request, 'Guest moved to Recycle Bin.')
    return redirect('guest_list')

@login_required
def booking_list(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    return render(request, 'hotel/booking_list.html', {'bookings': bookings})

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            # Create Invoice automatically
            Invoice.objects.create(booking=booking)
            messages.success(request, 'Booking created successfully')
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'hotel/booking_form.html', {'form': form})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payments = booking.payments.all()
    invoice = getattr(booking, 'invoice', None)
    if not invoice:
        invoice = Invoice.objects.create(booking=booking)
    
    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            payment.booking = booking
            payment.recorded_by = request.user
            payment.save()
            messages.success(request, 'Payment recorded')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        payment_form = PaymentForm()

    return render(request, 'hotel/booking_detail.html', {
        'booking': booking,
        'payments': payments,
        'invoice': invoice,
        'payment_form': payment_form
    })

@login_required
def check_in(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'Confirmed' or booking.status == 'Pending':
        booking.status = 'Checked-In'
        booking.actual_checkin = timezone.now()
        booking.save()
        booking.room.status = 'Occupied'
        booking.room.save()
        messages.success(request, f'Checked in guest {booking.guest.full_name}')
    return redirect('booking_detail', booking_id=booking.id)

@login_required
def check_out(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    invoice = booking.invoice
    if invoice.balance > 0:
        messages.error(request, 'Cannot check out. Outstanding balance remains.')
        return redirect('booking_detail', booking_id=booking.id)
    
    booking.status = 'Checked-Out'
    booking.actual_checkout = timezone.now()
    booking.save()
    booking.room.status = 'Available' # Or Maintenance -> Dirty? Requirement says Available.
    booking.room.save()
    messages.success(request, f'Checked out guest {booking.guest.full_name}')
    return redirect('booking_detail', booking_id=booking.id)

@login_required
def update_booking_dates(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        new_checkin = request.POST.get('check_in_date')
        new_checkout = request.POST.get('check_out_date')
        from datetime import datetime
        try:
            if new_checkin:
                booking.check_in_date = datetime.strptime(new_checkin, '%Y-%m-%d').date()
            if new_checkout:
                booking.check_out_date = datetime.strptime(new_checkout, '%Y-%m-%d').date()
            
            if booking.check_out_date <= booking.check_in_date:
                messages.error(request, "Check-out date must be after check-in date.")
            else:
                # Check for overlaps
                overlaps = Booking.objects.filter(
                    room=booking.room,
                    check_in_date__lt=booking.check_out_date,
                    check_out_date__gt=booking.check_in_date
                ).exclude(id=booking.id).exclude(status='Cancelled')
                
                if overlaps.exists():
                    messages.error(request, "Room is already booked for these new dates.")
                else:
                    booking.save()
                    messages.success(request, "Dates updated successfully.")
        except ValueError:
            messages.error(request, "Invalid date format.")
    return redirect('booking_detail', booking_id=booking.id)

@login_required
def apply_discount(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        discount_amount = request.POST.get('discount')
        try:
            from decimal import Decimal
            booking.discount = Decimal(discount_amount)
            booking.save()
            messages.success(request, f"Discount of ${discount_amount} applied.")
        except:
            messages.error(request, "Invalid discount amount.")
    return redirect('booking_detail', booking_id=booking.id)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status not in ['Reserved', 'Confirmed', 'Pending']:
        messages.error(request, 'Cannot cancel a booking that has already started.')
        return redirect('booking_detail', booking_id=booking.id)
    
    total_paid = booking.get_total_paid()
    
    # Logic: When cancelling, we set the status and free the room.
    # If there was a deposit, we should probably record it as a refund 
    # if the hotel returned it, or leave it if it's a 'cancellation fee'.
    
    # For "most correct" logic: we'll automatically create a Refund record 
    # to balance the account to zero if the user chooses 'Full Refund'
    refund_type = request.GET.get('refund', 'none') # Default to none
    
    booking.status = 'Cancelled'
    booking.save()
    
    if refund_type == 'full' and total_paid > 0:
        Payment.objects.create(
            booking=booking,
            payment_type='Refund',
            amount=total_paid,
            payment_method='Cash', # Defaulting to Cash for auto-refund
            notes="Automatic refund on cancellation",
            recorded_by=request.user
        )
        messages.success(request, f'Booking cancelled and full refund of ${total_paid} recorded.')
    else:
        messages.warning(request, f'Booking cancelled. Note: ${total_paid} remains in records as paid/deposit.')
    
    # Free up room
    booking.room.status = 'Available'
    booking.room.save()
    
    return redirect('booking_list')

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    return render(request, 'hotel/expense_list.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, 'Expense recorded, waiting approval')
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'hotel/expense_form.html', {'form': form})

@login_required
def approve_expense(request, expense_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('expense_list')
    
    expense = get_object_or_404(Expense, id=expense_id)
    expense.status = 'Approved'
    expense.approved_by = request.user
    expense.save()
    messages.success(request, 'Expense approved')
    return redirect('expense_list')

@login_required
def reject_expense(request, expense_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('expense_list')
    
    expense = get_object_or_404(Expense, id=expense_id)
    expense.status = 'Rejected'
    expense.approved_by = request.user
    expense.save()
    messages.success(request, 'Expense rejected')
    return redirect('expense_list')

@login_required
def flexible_report(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    from datetime import timedelta, datetime
    today = timezone.now().date()
    
    # Defaults
    start_date = today.replace(day=1) # Default to beginning of current month
    end_date = today
    
    # Parse filter type
    filter_type = request.GET.get('filter', 'month')
    custom_start = request.GET.get('start_date')
    custom_end = request.GET.get('end_date')
    
    if custom_start and custom_end:
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
            filter_type = 'custom'
        except ValueError:
            pass # Fallback to defaults
    elif filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif filter_type == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    # 'month' is already default
    
    # Financial Query
    # Use 'date__range' which includes start AND end date boundaries inclusive in most DBs (or handle time properly)
    # Since DateField, range is inclusive.
    payments = Payment.objects.filter(date__date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date], status='Approved')
    
    income_total = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = income_total - expense_total
    
    # Guest Manifest (Migration Report)
    # Guests who were checked-in at ANY point during this range.
    # Logic: Booking overlaps range if (check_in <= range_end) AND (check_out >= range_start)
    # Actually for "Daily Report" govt often wants "Who arrived" or "Who is currently in house". 
    # Let's provide "Guests Active in Period"
    active_bookings = Booking.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    ).exclude(status='Cancelled')
    
    # Statistics: Top Rooms
    from django.db.models import Count
    # Rooms booked most often in this period (by number of bookings starting in period)
    top_rooms = Booking.objects.filter(booking_date__date__range=[start_date, end_date])\
        .values('room__room_number', 'room__room_type')\
        .annotate(count=Count('id'), revenue=Sum('room__price_per_night'))\
        .order_by('-count')[:5]
        
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
        'report_data': {
            'income': income_total,
            'expenses': expense_total,
            'profit': profit,
            'payments': payments.order_by('-date'),
            'expenses_list': expenses.order_by('-date'),
            'active_bookings': active_bookings,
            'top_rooms': top_rooms,
        }
    }
    return render(request, 'hotel/reports.html', context)

@login_required
def invoice_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    invoice = booking.invoice
    return render(request, 'hotel/invoice.html', {'invoice': invoice})

@login_required
def user_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'hotel/user_list.html', {'users': users})

@login_required
def add_user(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'hotel/user_form.html', {'form': form})

@login_required
def toggle_user_status(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj == request.user:
        messages.error(request, 'Cannot deactivate yourself')
        return redirect('user_list')
        
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status = 'activated' if user_obj.is_active else 'deactivated'
    messages.success(request, f'User {user_obj.username} {status}')
    return redirect('user_list')

@login_required
def add_room(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room added successfully')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'hotel/room_form.html', {'form': form})

@login_required
def edit_room(request, room_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
        
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotel/room_form.html', {'form': form, 'edit_mode': True})

@login_required
@login_required
def delete_room(request, room_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access Denied: Room deletion is restricted to Admins.')
        return redirect('room_list')
    room = get_object_or_404(Room, id=room_id)
    # Strict validation: prevent breaking history
    if room.bookings.exists():
        messages.error(request, 'Audit Lock: This room has booking history and cannot be deleted. Try changing its status to Maintenance instead.')
    else:
        room.soft_delete()
        messages.success(request, 'Room moved to Recycle Bin.')
    return redirect('room_list')

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(instance=booking)
    return render(request, 'hotel/booking_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_booking(request, booking_id):
    if request.user.role != 'admin':
        messages.error(request, 'Security Alert: Only Admins can permanently delete reservation records.')
        return redirect('booking_list')
        
    booking = get_object_or_404(Booking, id=booking_id)
    # Validation: If checked in or has payments, forbid deletion to preserve audit trail
    if booking.status in ['Checked-In', 'Checked-Out']:
        messages.error(request, 'Audit Trail Lock: Cannot delete a booking that is currently active or has already been completed.')
    elif booking.payments.exists():
        messages.error(request, 'Financial Lock: This booking has associated payments. It must be Cancelled instead of Deleted to maintain the ledger.')
    else:
        booking.room.status = 'Available'
        booking.room.save()
        booking.soft_delete()
        messages.success(request, 'Booking moved to Recycle Bin.')
    return redirect('booking_list')

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if expense.status != 'Pending' and request.user.role != 'admin':
        messages.error(request, 'Audit Lock: Only admins can edit approved/rejected expenses.')
        return redirect('expense_list')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'hotel/expense_form.html', {'form': form, 'edit_mode': True})

@login_required
def delete_expense(request, expense_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access Denied: Expense records can only be removed by administrators.')
        return redirect('expense_list')
        
    expense = get_object_or_404(Expense, id=expense_id)
    # Logic: If it's already approved/rejected, it's part of the monthly report
    if expense.status != 'Pending':
        messages.error(request, 'Financial Lock: Cannot delete processed expenses. They are part of the permanent accounting record.')
    else:
        expense.soft_delete()
        messages.success(request, 'Expense moved to Recycle Bin.')
    return redirect('expense_list')

@login_required
def delete_payment(request, payment_id):
    if request.user.role != 'admin':
        messages.error(request, 'Security Alert: Only administrators can remove payment records.')
        return redirect('booking_list')
        
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking
    
    # Validation: Prevent breaking financial history of completed stays
    if booking.status == 'Checked-Out':
        messages.error(request, 'Financial Lock: Cannot delete payments for completed bookings. Use adjustments instead to maintain audit trail.')
    else:
        payment.soft_delete()
        messages.success(request, 'Payment moved to Recycle Bin.')
        
    return redirect('booking_detail', booking_id=booking.id)

@login_required
def recycle_bin(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access Denied')
        return redirect('dashboard')
    
    # Auto-cleanup logic: Remove items older than 7 days
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(days=7)
    
    # Hard delete old items
    if Guest.objects.deleted().filter(deleted_at__lt=cutoff).exists():
        Guest.objects.deleted().filter(deleted_at__lt=cutoff).delete()
    if Room.objects.deleted().filter(deleted_at__lt=cutoff).exists():
        Room.objects.deleted().filter(deleted_at__lt=cutoff).delete()
    if Booking.objects.deleted().filter(deleted_at__lt=cutoff).exists():
        Booking.objects.deleted().filter(deleted_at__lt=cutoff).delete()
    if Expense.objects.deleted().filter(deleted_at__lt=cutoff).exists():
        Expense.objects.deleted().filter(deleted_at__lt=cutoff).delete()
    if Payment.objects.deleted().filter(deleted_at__lt=cutoff).exists():
        Payment.objects.deleted().filter(deleted_at__lt=cutoff).delete()

    deleted_items = []
    
    for obj in Guest.objects.deleted():
        deleted_items.append({'type': 'Guest', 'id': obj.id, 'desc': obj.full_name, 'date': obj.deleted_at})
    
    for obj in Room.objects.deleted():
        deleted_items.append({'type': 'Room', 'id': obj.id, 'desc': f"Room {obj.room_number}", 'date': obj.deleted_at})
        
    for obj in Booking.objects.deleted():
        deleted_items.append({'type': 'Booking', 'id': obj.id, 'desc': f"Booking for {obj.guest.full_name}", 'date': obj.deleted_at})
        
    for obj in Expense.objects.deleted():
        deleted_items.append({'type': 'Expense', 'id': obj.id, 'desc': f"{obj.title} (${obj.amount})", 'date': obj.deleted_at})

    for obj in Payment.objects.deleted():
        deleted_items.append({'type': 'Payment', 'id': obj.id, 'desc': f"{obj.get_payment_type_display()} - ${obj.amount}", 'date': obj.deleted_at})
    
    deleted_items.sort(key=lambda x: x['date'] if x['date'] else timezone.now(), reverse=True)
    
    return render(request, 'hotel/recycle_bin.html', {'deleted_items': deleted_items})

@login_required
def restore_item(request, item_type, item_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access Denied')
        return redirect('dashboard')
    
    model_map = {
        'Guest': Guest,
        'Room': Room,
        'Booking': Booking,
        'Expense': Expense,
        'Payment': Payment
    }
    
    model = model_map.get(item_type)
    if model:
        obj = get_object_or_404(model.objects.deleted(), id=item_id)
        obj.restore()
        messages.success(request, f'{item_type} restored successfully.')
        if item_type == 'Booking':
             messages.warning(request, 'Booking restored. Please check Room Availability manually.')
    
    return redirect('recycle_bin')

@login_required
def permanent_delete_item(request, item_type, item_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access Denied')
        return redirect('dashboard')
    
    model_map = {
        'Guest': Guest,
        'Room': Room,
        'Booking': Booking,
        'Expense': Expense,
        'Payment': Payment
    }
    
    model = model_map.get(item_type)
    if model:
        from django.db.models import ProtectedError
        try:
            obj = get_object_or_404(model.objects.deleted(), id=item_id)
            obj.delete()
            messages.success(request, f'{item_type} permanently deleted.')
        except ProtectedError:
            messages.error(request, f'Financial Audit Lock: Cannot permanently delete this {item_type} because it is linked to other records (like payments or bookings) that are required for the financial ledger.')
    
    return redirect('recycle_bin')

@login_required
def search(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        messages.warning(request, "Search query must be at least 2 characters")
        # Referer logic to redirect back to where they came from, or dashboard
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
    # Search Guests
    guests = Guest.objects.filter(
        Q(full_name__icontains=query) | 
        Q(phone_number__icontains=query) |
        Q(id_card__icontains=query)
    )
    
    # Search Bookings
    bookings = Booking.objects.filter(
        Q(id__icontains=query) |
        Q(guest__full_name__icontains=query) |
        Q(room__room_number__icontains=query)
    )
    
    context = {
        'query': query,
        'guests': guests,
        'bookings': bookings
    }
    return render(request, 'hotel/search_results.html', context)

@login_required
def guest_report(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
        
    from datetime import timedelta, datetime
    today = timezone.now().date()
    
    # Defaults
    start_date = today
    end_date = today
    
    filter_type = request.GET.get('filter', 'today')
    custom_start = request.GET.get('start_date')
    custom_end = request.GET.get('end_date')
    
    if custom_start and custom_end:
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
            filter_type = 'custom'
        except ValueError:
            pass
    elif filter_type == 'week':
        start_date = today - timedelta(days=7)
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        
    # Logic: "Guests who entered" means Check-in Date is within range
    # OR "Guests currently staying" means ranges overlap.
    # For Immigration "Daily Entry Report", usually it's just Check-ins.
    bookings = Booking.objects.filter(
        check_in_date__range=[start_date, end_date]
    ).order_by('check_in_date')
    
    context = {
        'bookings': bookings,
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
    }
    return render(request, 'hotel/guest_report.html', context)

@login_required
def api_search(request):
    """API endpoint for live search functionality"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
        
    results = []
    
    # Search Guests
    guests = Guest.objects.filter(
        Q(full_name__icontains=query) | 
        Q(phone_number__icontains=query) |
        Q(id_card__icontains=query)
    )[:5] # Limit to 5
    
    for guest in guests:
        results.append({
            'type': 'guest',
            'title': guest.full_name,
            'subtitle': f"Ph: {guest.phone_number}",
            'url': reverse('edit_guest', args=[guest.id])
        })
        
    # Search Bookings
    bookings = Booking.objects.filter(
        Q(id__icontains=query) |
        Q(guest__full_name__icontains=query) |
        Q(room__room_number__icontains=query)
    ).select_related('guest', 'room')[:5]
    
    for booking in bookings:
        results.append({
            'type': 'booking',
            'title': f"Booking #{booking.id} - {booking.guest.full_name}",
            'subtitle': f"Room {booking.room.room_number} • {booking.status}",
            'url': reverse('booking_detail', args=[booking.id])
        })
        
    # Search Rooms
    rooms = Room.objects.filter(
        Q(room_number__icontains=query) |
        Q(room_type__icontains=query)
    )[:5]
    
    for room in rooms:
        results.append({
            'type': 'room',
            'title': f"Room {room.room_number}",
            'subtitle': f"{room.room_type} • {room.status}",
            'url': reverse('edit_room', args=[room.id])
        })
    
    # Search Expenses
    expenses = Expense.objects.filter(
        Q(title__icontains=query) |
        Q(category__icontains=query)
    )[:5]
    
    for expense in expenses:
        results.append({
            'type': 'expense',
            'title': expense.title,
            'subtitle': f"${expense.amount} • {expense.status}",
            'url': reverse('expense_list')
        })
    
    return JsonResponse({'results': results})

@login_required
def printable_financial_report(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    from datetime import timedelta, datetime
    today = timezone.now().date()
    
    filter_type = request.GET.get('filter', 'month')
    custom_start = request.GET.get('start_date')
    custom_end = request.GET.get('end_date')
    
    start_date = today.replace(day=1)
    end_date = today
    
    if custom_start and custom_end:
        try:
            start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
            filter_type = 'custom'
        except ValueError:
            pass
    elif filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif filter_type == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today

    payments = Payment.objects.filter(date__date__range=[start_date, end_date])
    expenses = Expense.objects.filter(date__range=[start_date, end_date], status='Approved')
    
    income_total = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = income_total - expense_total
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
        'report_data': {
            'income': income_total,
            'expenses': expense_total,
            'profit': profit,
            'payments': payments.order_by('-date'),
            'expenses_list': expenses.order_by('-date'),
        }
    }
    return render(request, 'hotel/financial_report_printable.html', context)

@login_required
def add_additional_charge(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        charge_type = request.POST.get('charge_type')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        
        try:
            from .models import AdditionalCharge
            from decimal import Decimal
            AdditionalCharge.objects.create(
                booking=booking,
                charge_type=charge_type,
                description=description,
                amount=Decimal(amount),
                added_by=request.user
            )
            messages.success(request, f"Charge of ${amount} added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding charge: {str(e)}")
            
    return redirect('booking_detail', booking_id=booking.id)

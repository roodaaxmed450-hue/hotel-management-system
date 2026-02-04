# Real-World Hotel Management System - Button-Based Workflow

**System Philosophy:** Bill based on ACTUAL check-in and check-out times, not planned dates.

---

## Core Principles

### 1. Timestamp-Based Billing
```
Billing Formula:
  Days Stayed = (actual_checkout_time - actual_checkin_time)
  Total Amount = Days Stayed × Room Rate
  
NOT based on:
  ❌ Planned check-in date
  ❌ Planned check-out date
  
ONLY based on:
  ✅ Actual check-in timestamp
  ✅ Actual check-out timestamp
```

### 2. Button Flow
```
Booking Created → [CHECK IN] → Guest Staying → [CHECK OUT] → Billing & Payment
```

### 3. Room Status Lifecycle
```
Available → [Booking Created] → Reserved
Reserved → [CHECK IN] → Occupied  
Occupied → [CHECK OUT] → Available
```

---

## Scenario 1: Standard Stay (On-Time Check-In & Check-Out)

### Real-World Situation
Guest arrives on time, stays the planned duration, and checks out as expected.

### Timeline
```
Booking Created: Jan 30, 2026
  - Planned Check-in: Feb 1, 2026 (2:00 PM)
  - Planned Check-out: Feb 4, 2026 (12:00 PM)
  - Room: 105 ($50/night)
  - Status: Reserved
  - Room Status: Reserved
```

### Check-In Process
**Feb 1, 2026 at 2:15 PM**
- Receptionist clicks **[CHECK IN]** button
- System records: `actual_checkin = 2026-02-01 14:15:00`
- Room 105 status: Reserved → **Occupied**
- Booking status: Reserved → **Checked-In**

### Check-Out Process
**Feb 4, 2026 at 11:45 AM**
- Receptionist clicks **[CHECK OUT]** button
- System records: `actual_checkout = 2026-02-04 11:45:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 14:15:00
actual_checkout = 2026-02-04 11:45:00

Time Stayed = 2 days, 21 hours, 30 minutes
Days Billed = 3 days (hotel rounds up partial days)

Total Amount = 3 days × $50 = $150
```

### Payment & Room Status
- Invoice generated: $150
- Payment collected: $150 (Cash/Mobile/Bank)
- Room 105 status: Occupied → **Available**
- Booking status: Checked-In → **Checked-Out**

---

## Scenario 2: Early Check-Out

### Real-World Situation
Guest checks out 1 day earlier than planned due to change in travel plans.

### Timeline
```
Booking Created: Jan 30, 2026
  - Planned Check-in: Feb 1, 2026
  - Planned Check-out: Feb 5, 2026 (4 nights planned)
  - Room: 102 ($50/night)
  - Advance Payment: $200 (full amount)
```

### Check-In
**Feb 1, 2026 at 3:00 PM**
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 15:00:00`
- Room 102: Reserved → Occupied

### Early Check-Out
**Feb 4, 2026 at 10:00 AM** (1 day early!)
- Guest requests early checkout
- Receptionist clicks **[CHECK OUT]**
- `actual_checkout = 2026-02-04 10:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 15:00:00
actual_checkout = 2026-02-04 10:00:00

Time Stayed = 2 days, 19 hours
Days Billed = 3 days (rounded up)

Actual Amount = 3 days × $50 = $150
Paid Amount = $200 (advance)
Refund Due = $200 - $150 = $50
```

### Payment Handling
- Original payment: $200
- Actual charges: $150
- **Refund to guest: $50**
- Room 102: Occupied → **Available** (now free for new bookings)

### Key Point
**Ignore planned checkout date (Feb 5).** Bill only for actual time stayed (Feb 1-4).

---

## Scenario 3: Overstay (Late Check-Out)

### Real-World Situation
Guest extends stay beyond planned checkout date.

### Timeline
```
Booking Created: Jan 28, 2026
  - Planned Check-in: Feb 1, 2026
  - Planned Check-out: Feb 3, 2026 (2 nights)
  - Room: 107 ($80/night)
  - Advance: $160 (paid)
```

### Check-In
**Feb 1, 2026 at 1:30 PM**
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 13:30:00`
- Room 107: Reserved → Occupied

### Overstay Check-Out
**Feb 5, 2026 at 11:00 AM** (2 days late!)
- Guest stayed 2 extra days
- Receptionist clicks **[CHECK OUT]**
- `actual_checkout = 2026-02-05 11:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 13:30:00
actual_checkout = 2026-02-05 11:00:00

Time Stayed = 3 days, 21 hours, 30 minutes
Days Billed = 4 days (rounded up)

Actual Amount = 4 days × $80 = $320
Paid Amount = $160 (advance)
Additional Due = $320 - $160 = $160
```

### Payment Handling
- Original payment: $160 (for 2 nights)
- Actual charges: $320 (for 4 nights)
- **Additional payment required: $160**
- Collect at checkout: $160 (Cash/Mobile/Bank)
- Room 107: Occupied → **Available**

### Key Point
**Ignore planned checkout (Feb 3).** Bill for actual stay (Feb 1-5).

---

## Scenario 4: No-Show

### Real-World Situation
Guest never arrives, never checks in.

### Timeline
```
Booking Created: Jan 25, 2026
  - Planned Check-in: Feb 1, 2026 (2:00 PM)
  - Planned Check-out: Feb 4, 2026
  - Room: 103 ($50/night)
  - Advance: $50 (deposit)
  - Status: Reserved
```

### No-Show Handling
**Feb 1, 2026 at 8:00 PM** (6 hours past expected arrival)
- Guest never arrived
- Never clicked **[CHECK IN]**
- Receptionist marks booking as "No-Show"

### Billing Calculation
```python
actual_checkin  = NULL (never checked in)
actual_checkout = NULL (never checked in)

Days Stayed = 0
Billing = $0

Advance Payment = $50 (forfeited per hotel policy)
```

### Payment & Room Handling
- **No billing** (guest never stayed)
- Advance payment: **$50 forfeited** (no-show penalty)
- Room 103: Reserved → **Available** (released immediately)
- Booking status: Reserved → **No-Show**

### Key Point
**No check-in = No billing.** Only advance deposit is kept as penalty.

---

## Scenario 5: Late Arrival (Check-In After Midnight)

### Real-World Situation
Guest arrives very late, after midnight.

### Timeline
```
Booking Created: Jan 30, 2026
  - Planned Check-in: Feb 1, 2026 (2:00 PM)
  - Planned Check-out: Feb 3, 2026
  - Room: 104 ($50/night)
```

### Late Check-In
**Feb 2, 2026 at 1:30 AM** (11.5 hours late!)
- Guest arrives after midnight
- Receptionist clicks **[CHECK IN]**
- `actual_checkin = 2026-02-02 01:30:00`
- Room 104: Reserved → Occupied

### Check-Out
**Feb 3, 2026 at 11:00 AM**
- Click **[CHECK OUT]**
- `actual_checkout = 2026-02-03 11:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-02 01:30:00
actual_checkout = 2026-02-03 11:00:00

Time Stayed = 1 day, 9 hours, 30 minutes
Days Billed = 2 days (rounded up)

Total Amount = 2 days × $50 = $100
```

### Key Point
**Ignore planned check-in date (Feb 1).** Bill from actual check-in (Feb 2).
Guest only pays for 2 days, not the originally planned 2 nights.

---

## Scenario 6: Sudden Departure (Emergency Checkout)

### Real-World Situation
Guest must leave immediately due to emergency.

### Timeline
```
Booking Created: Jan 28, 2026
  - Planned Check-in: Feb 1, 2026
  - Planned Check-out: Feb 7, 2026 (6 nights)
  - Room: 108 ($60/night)
  - Advance: $360 (full payment)
```

### Check-In
**Feb 1, 2026 at 2:00 PM**
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 14:00:00`
- Room 108: Reserved → Occupied

### Emergency Check-Out
**Feb 2, 2026 at 8:00 AM** (next morning!)
- Family emergency
- Receptionist clicks **[CHECK OUT]**
- `actual_checkout = 2026-02-02 08:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 14:00:00
actual_checkout = 2026-02-02 08:00:00

Time Stayed = 18 hours
Days Billed = 1 day (rounded up)

Actual Amount = 1 day × $60 = $60
Paid Amount = $360 (advance)
Refund Due = $360 - $60 = $300
```

### Payment Handling
- Original payment: $360 (for 6 nights)
- Actual charges: $60 (for 1 night)
- **Refund: $300** (processed immediately)
- Room 108: Occupied → **Available**

---

## Scenario 7: Room Change Mid-Stay

### Real-World Situation
Guest requests room upgrade after 2 days.

### Timeline
```
Initial Booking:
  - Room: 100 (Single - $50/night)
  - Planned: Feb 1-6 (5 nights)
```

### Check-In to Room 100
**Feb 1, 2026 at 3:00 PM**
- Click **[CHECK IN]** for Room 100
- `actual_checkin_room100 = 2026-02-01 15:00:00`
- Room 100: Reserved → Occupied

### Room Change
**Feb 3, 2026 at 11:00 AM** (after 2 nights)
- Guest requests upgrade to Suite
- Receptionist processes room change:
  1. Click **[CHECK OUT]** from Room 100
  2. `actual_checkout_room100 = 2026-02-03 11:00:00`
  3. Click **[CHECK IN]** to Room 110 (Suite - $120/night)
  4. `actual_checkin_room110 = 2026-02-03 11:00:00`

### Final Check-Out
**Feb 6, 2026 at 12:00 PM**
- Click **[CHECK OUT]** from Room 110
- `actual_checkout_room110 = 2026-02-06 12:00:00`

### Billing Calculation
```python
# Room 100 (Single)
Time in Room 100 = 2026-02-03 11:00 - 2026-02-01 15:00
                 = 1 day, 20 hours
Days Billed = 2 days × $50 = $100

# Room 110 (Suite)
Time in Room 110 = 2026-02-06 12:00 - 2026-02-03 11:00
                 = 3 days, 1 hour
Days Billed = 4 days × $120 = $480

Total Amount = $100 + $480 = $580
```

### Room Status Changes
- Room 100: Occupied → **Available** (Feb 3, 11 AM)
- Room 110: Available → **Occupied** (Feb 3, 11 AM)
- Room 110: Occupied → **Available** (Feb 6, 12 PM)

---

## Scenario 8: Partial Payment with Balance at Checkout

### Real-World Situation
Guest pays advance, settles remaining balance at checkout.

### Timeline
```
Booking Created: Jan 30, 2026
  - Room: 105 ($50/night)
  - Planned: Feb 1-5 (4 nights estimated)
  - Advance: $100 (partial)
```

### Check-In
**Feb 1, 2026 at 2:30 PM**
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 14:30:00`
- Room 105: Reserved → Occupied
- Payment status: $100 paid, balance TBD

### Check-Out & Final Billing
**Feb 4, 2026 at 11:30 AM**
- Click **[CHECK OUT]**
- `actual_checkout = 2026-02-04 11:30:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 14:30:00
actual_checkout = 2026-02-04 11:30:00

Time Stayed = 2 days, 21 hours
Days Billed = 3 days

Total Amount = 3 days × $50 = $150
Advance Paid = $100
Balance Due = $150 - $100 = $50
```

### Payment at Checkout
```
Invoice Summary:
  Room Charges: $150
  Advance Payment: -$100
  Balance Due: $50
  
Payment Collected: $50 (Mobile Money)
Total Paid: $150
Balance: $0
Status: PAID ✓
```

### Room Status
- Room 105: Occupied → **Available**

---

## Scenario 9: Same-Day Check-In and Check-Out

### Real-World Situation
Guest only needs room for a few hours (day use).

### Timeline
```
Walk-in Guest: Feb 1, 2026
  - Room: 106 ($50/night)
  - No advance booking
```

### Check-In
**Feb 1, 2026 at 10:00 AM**
- Walk-in guest
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 10:00:00`
- Room 106: Available → Occupied

### Same-Day Check-Out
**Feb 1, 2026 at 6:00 PM** (8 hours later)
- Click **[CHECK OUT]**
- `actual_checkout = 2026-02-01 18:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 10:00:00
actual_checkout = 2026-02-01 18:00:00

Time Stayed = 8 hours
Days Billed = 1 day (minimum charge)

Total Amount = 1 day × $50 = $50
```

### Payment & Room
- Charge: $50 (minimum 1 day)
- Payment: $50 (Cash)
- Room 106: Occupied → **Available** (same day)

### Key Point
**Minimum billing = 1 day**, even for partial day use.

---

## Scenario 10: Multiple Payments During Stay

### Real-World Situation
Long-term guest makes weekly payments.

### Timeline
```
Booking: Jan 30, 2026
  - Room: 109 (Suite - $100/night)
  - Long-term stay (open-ended)
```

### Check-In
**Feb 1, 2026 at 2:00 PM**
- Click **[CHECK IN]**
- `actual_checkin = 2026-02-01 14:00:00`
- Room 109: Reserved → Occupied

### Payment Schedule
```
Week 1 (Feb 1-7):
  - Payment: $700 (7 days × $100)
  - Date: Feb 7
  - Method: Bank Transfer
  
Week 2 (Feb 8-14):
  - Payment: $700
  - Date: Feb 14
  - Method: Bank Transfer
  
Week 3 (Feb 15-21):
  - Payment: $700
  - Date: Feb 21
  - Method: Bank Transfer
```

### Final Check-Out
**Feb 23, 2026 at 11:00 AM**
- Click **[CHECK OUT]**
- `actual_checkout = 2026-02-23 11:00:00`

### Billing Calculation
```python
actual_checkin  = 2026-02-01 14:00:00
actual_checkout = 2026-02-23 11:00:00

Time Stayed = 21 days, 21 hours
Days Billed = 22 days

Total Amount = 22 days × $100 = $2,200
Payments Made = $700 + $700 + $700 = $2,100
Balance Due = $2,200 - $2,100 = $100
```

### Final Payment
- Collect at checkout: $100
- Total paid: $2,200
- Room 109: Occupied → **Available**

---

## System Implementation Requirements

### Database Schema Updates

```python
class Booking(models.Model):
    # Existing fields
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    # Planned dates (for reservation only)
    planned_checkin_date = models.DateField()
    planned_checkout_date = models.DateField()
    
    # ACTUAL timestamps (for billing)
    actual_checkin = models.DateTimeField(null=True, blank=True)
    actual_checkout = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('Reserved', 'Reserved'),
            ('Checked-In', 'Checked-In'),
            ('Checked-Out', 'Checked-Out'),
            ('No-Show', 'No-Show'),
            ('Cancelled', 'Cancelled'),
        ]
    )
    
    def calculate_actual_amount(self):
        """Calculate based on ACTUAL check-in/out times"""
        if not self.actual_checkin or not self.actual_checkout:
            return 0
        
        time_diff = self.actual_checkout - self.actual_checkin
        hours = time_diff.total_seconds() / 3600
        days = math.ceil(hours / 24)  # Round up partial days
        
        return days * self.room.price_per_night
    
    def get_balance(self):
        """Get remaining balance"""
        total = self.calculate_actual_amount()
        paid = sum(p.amount for p in self.payments.all())
        return total - paid
```

### Button Actions

```python
# CHECK IN Button
def check_in(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    # Record actual check-in time
    booking.actual_checkin = timezone.now()
    booking.status = 'Checked-In'
    booking.room.status = 'Occupied'
    
    booking.save()
    booking.room.save()
    
    messages.success(request, f"Guest checked in at {booking.actual_checkin}")
    return redirect('booking_detail', booking_id)

# CHECK OUT Button
def check_out(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    
    # Record actual check-out time
    booking.actual_checkout = timezone.now()
    booking.status = 'Checked-Out'
    booking.room.status = 'Available'
    
    # Calculate final bill
    total_amount = booking.calculate_actual_amount()
    paid_amount = sum(p.amount for p in booking.payments.all())
    balance = total_amount - paid_amount
    
    booking.save()
    booking.room.save()
    
    # Show billing summary
    context = {
        'booking': booking,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'balance': balance,
    }
    
    return render(request, 'hotel/checkout_billing.html', context)
```

---

## Key Takeaways

### ✅ DO:
1. **Use actual timestamps** for all billing calculations
2. **Round up partial days** (industry standard)
3. **Release rooms immediately** after checkout
4. **Calculate balance** at checkout based on actual stay
5. **Allow refunds** for early checkouts
6. **Charge extra** for overstays

### ❌ DON'T:
1. **Don't bill based on planned dates**
2. **Don't assume guests stay full duration**
3. **Don't keep rooms occupied** after checkout
4. **Don't ignore partial days** in calculations
5. **Don't charge no-show guests** for full stay

### 🎯 Industry Standards:
- **Minimum charge:** 1 day (even for few hours)
- **Partial day:** Round up to full day
- **Check-in time:** Usually 2:00 PM
- **Check-out time:** Usually 12:00 PM (noon)
- **Late checkout fee:** Often 50% of daily rate
- **No-show penalty:** Forfeit advance deposit

---

**Document Version:** 1.0  
**Created:** January 31, 2026  
**System:** KHMS Real-World Workflow

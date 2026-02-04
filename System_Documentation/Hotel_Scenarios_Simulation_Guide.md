# Hotel Management System - Comprehensive Scenario Simulation Guide

**System:** KHMS (Kismayo Hotel Management System)  
**Version:** 1.0  
**Date:** January 30, 2026

---

## Table of Contents

1. [Early Checkout](#1-early-checkout)
2. [Late Checkout / Overstay](#2-late-checkout--overstay)
3. [Booking Cancellation](#3-booking-cancellation)
4. [Partial Payment / Advance](#4-partial-payment--advance)
5. [Expenses During Stay](#5-expenses-during-stay)
6. [Room Change During Stay](#6-room-change-during-stay)
7. [Overlapping / Double Booking](#7-overlapping--double-booking)
8. [No-Show Guest](#8-no-show-guest)
9. [Long-Term Booking Adjustment](#9-long-term-booking-adjustment)
10. [Invoice & Reporting](#10-invoice--reporting)
11. [Admin Approval Required](#11-admin-approval-required)
12. [Audit Trail / Change Tracking](#12-audit-trail--change-tracking)
13. [Early Check-In](#13-early-check-in)
14. [Room Maintenance / Blocked Room](#14-room-maintenance--blocked-room)
15. [Group Booking](#15-group-booking)
16. [Lost Booking / Missing Payment](#16-lost-booking--missing-payment)
17. [Discounts / Promotions](#17-discounts--promotions)
18. [Booking Modification](#18-booking-modification)
19. [Lost or Damaged Items](#19-lost-or-damaged-items)
20. [Room Upgrade](#20-room-upgrade)
21. [Guest Special Requests](#21-guest-special-requests)
22. [Late Payment at Check-Out](#22-late-payment-at-check-out)
23. [Multiple Booking Adjustments](#23-multiple-booking-adjustments)
24. [Emergency / Early Evacuation](#24-emergency--early-evacuation)
25. [Special Events / Peak Season](#25-special-events--peak-season)

---

## Scenario Simulations

### 1. Early Checkout

**Scenario:** Guest checks out 2 days earlier than planned

**Initial Booking:**
- Guest: Ahmed Hassan
- Room: 105 (Single - $50/night)
- Check-in: Jan 30, 2026
- Planned Check-out: Feb 5, 2026 (6 nights)
- Total: $300
- Status: Checked-In
- Payment: $300 (Pre-paid)

**Action Steps:**
1. Receptionist navigates to Bookings → Booking #4
2. Clicks "Check Out" button
3. System detects early checkout (Feb 3 vs Feb 5)
4. System recalculates: 4 nights × $50 = $200

**System Updates:**
```
Booking Status: Checked-In → Checked-Out
Check-out Date: Feb 5 → Feb 3
Total Amount: $300 → $200
Refund Due: $100
Room 105 Status: Occupied → Available
```

**Payment Handling:**
- Original Payment: $300
- New Total: $200
- Refund: $100 (to be processed)

**Notification:**
- Admin receives alert: "Early checkout - Booking #4 - Refund $100"

---

### 2. Late Checkout / Overstay

**Scenario:** Guest extends stay by 2 additional days

**Initial Booking:**
- Guest: Fatima Ali
- Room: 102 (Single - $50/night)
- Check-in: Jan 28, 2026
- Planned Check-out: Jan 31, 2026 (3 nights)
- Total: $150
- Status: Checked-In
- Payment: $150 (Paid)

**Action Steps:**
1. Guest requests extension on Jan 31
2. Receptionist checks Room 102 availability
3. Updates checkout date to Feb 2, 2026
4. System recalculates charges

**System Updates:**
```
Check-out Date: Jan 31 → Feb 2
Total Nights: 3 → 5
Total Amount: $150 → $250
Additional Charge: $100
Room 102 Status: Remains Occupied
```

**Payment Handling:**
- Original Payment: $150
- New Total: $250
- Balance Due: $100

**Notification:**
- Admin alert: "Booking extended - Additional $100 charge"

---

### 3. Booking Cancellation

**Scenario:** Guest cancels 3 days before check-in

**Initial Booking:**
- Guest: Omar Yusuf
- Room: 107 (Double - $80/night)
- Check-in: Feb 5, 2026
- Check-out: Feb 10, 2026 (5 nights)
- Total: $400
- Status: Confirmed
- Payment: $100 (Advance)

**Cancellation Policy:**
- More than 48 hours: 50% refund
- Less than 48 hours: No refund

**Action Steps:**
1. Receptionist navigates to Booking #5
2. Changes status to "Cancelled"
3. System applies refund policy

**System Updates:**
```
Booking Status: Confirmed → Cancelled
Room 107 Status: Booked → Available
Refund Amount: $50 (50% of advance)
```

**Payment Handling:**
- Advance Paid: $100
- Refund: $50
- Cancellation Fee: $50

---

### 4. Partial Payment / Advance

**Scenario:** Guest pays 30% advance, rest at checkout

**Booking:**
- Guest: Amina Mohamed
- Room: 103 (Single - $50/night)
- Duration: 4 nights
- Total: $200
- Advance: $60 (30%)

**Payment Timeline:**

**At Booking:**
```python
Payment #1:
  Amount: $60
  Method: Mobile Money
  Date: Jan 30
  Status: Confirmed
  Balance: $140
```

**At Check-out:**
```python
Payment #2:
  Amount: $140
  Method: Cash
  Date: Feb 3
  Status: Paid
  Balance: $0
```

**Invoice Display:**
```
Total Amount: $200.00
Payments:
  - Jan 30: $60.00 (Mobile)
  - Feb 3: $140.00 (Cash)
Total Paid: $200.00
Balance: $0.00
Status: PAID
```

---

### 5. Expenses During Stay

**Scenario:** Hotel incurs expenses, some charged to guest

**Expenses:**

**Expense #1 - Guest Minibar:**
```
Title: Minibar - Room 105
Category: Guest Services
Amount: $25
Date: Feb 1, 2026
Status: Approved
Charged to: Booking #4
```

**Expense #2 - Hotel Maintenance:**
```
Title: AC Repair - Room 108
Category: Maintenance
Amount: $150
Date: Feb 1, 2026
Status: Approved
Charged to: Hotel (not guest)
```

**Guest Invoice Update:**
```
Room Charges: $200
Additional Charges:
  - Minibar: $25
Subtotal: $225
Payments: $200
Balance Due: $25
```

---

### 6. Room Change During Stay

**Scenario:** Guest requests room upgrade mid-stay

**Original Booking:**
- Guest: Hassan Ibrahim
- Room: 100 (Single - $50/night)
- Days Remaining: 3 nights
- Status: Checked-In

**New Room:**
- Room: 110 (Suite - $120/night)
- Price Difference: $70/night

**Action Steps:**
1. Check Room 110 availability
2. Update booking to Room 110
3. Recalculate charges

**System Updates:**
```
Room: 100 → 110
Rate: $50/night → $120/night
Additional Charge: $70 × 3 = $210
Room 100 Status: Occupied → Available
Room 110 Status: Available → Occupied
```

**Payment:**
- Original Total: $250 (5 nights × $50)
- Days Completed: 2 ($100)
- Remaining: 3 nights × $120 = $360
- New Total: $100 + $360 = $460
- Additional Payment: $210

---

### 7. Overlapping / Double Booking Prevention

**Scenario:** System prevents double booking

**Existing Booking:**
- Room: 102
- Dates: Feb 1-5, 2026
- Status: Confirmed

**New Booking Attempt:**
- Room: 102
- Dates: Feb 3-7, 2026

**System Response:**
```
ERROR: Room 102 not available
Conflict with Booking #6
Occupied: Feb 1-5, 2026

Suggested Alternatives:
- Room 103 (Single - $50/night) ✓ Available
- Room 104 (Single - $50/night) ✓ Available
- Room 106 (Double - $80/night) ✓ Available
```

**Validation Logic:**
```python
def check_availability(room, check_in, check_out):
    conflicts = Booking.objects.filter(
        room=room,
        status__in=['Confirmed', 'Checked-In'],
        check_in_date__lt=check_out,
        check_out_date__gt=check_in
    )
    return conflicts.count() == 0
```

---

### 8. No-Show Guest

**Scenario:** Guest doesn't arrive, no communication

**Booking:**
- Guest: Ali Abdi
- Room: 104
- Check-in: Feb 1, 2026 (Expected 2 PM)
- Check-out: Feb 4, 2026
- Total: $150
- Advance: $50
- Status: Confirmed

**Timeline:**
- Feb 1, 2 PM: Expected arrival
- Feb 1, 6 PM: No show, no contact
- Feb 1, 8 PM: Receptionist marks as No-Show

**System Updates:**
```
Booking Status: Confirmed → No-Show
Room 104 Status: Booked → Available
Advance Payment: $50 (Forfeited)
Remaining: $100 (Cancelled)
```

**Financial Impact:**
- Advance Kept: $50
- Room Released: Available for new bookings
- Revenue Loss: $100

---

### 9. Long-Term Booking Adjustment

**Scenario:** Monthly guest extends stay

**Original Booking:**
- Guest: Mohamed Jama (Business Traveler)
- Room: 109 (Suite - $100/night)
- Duration: 30 days (Jan 15 - Feb 14)
- Total: $3,000
- Status: Checked-In

**Extension Request:**
- Additional: 15 days (Feb 14 - Mar 1)

**System Updates:**
```
Check-out: Feb 14 → Mar 1
Total Nights: 30 → 45
Total Amount: $3,000 → $4,500
Additional Charge: $1,500
```

**Payment Plan:**
- Original: $3,000 (Paid)
- Extension: $1,500
- Payment Method: Bank Transfer
- Due Date: Feb 10

---

### 10. Invoice & Reporting

**Scenario:** Generate comprehensive invoice

**Booking Details:**
- Booking #7
- Guest: Khadija Ahmed
- Room: 105 (Single)
- Check-in: Jan 28, 2026
- Check-out: Feb 2, 2026
- Nights: 5

**Invoice Breakdown:**
```
═══════════════════════════════════════
        HOTEL INVOICE #INV-007
═══════════════════════════════════════

Guest: Khadija Ahmed
Phone: +252-61-7654321
Room: 105 (Single)

Check-in:  Jan 28, 2026
Check-out: Feb 2, 2026
Nights: 5

CHARGES:
─────────────────────────────────────
Room Charges:
  5 nights × $50/night        $250.00

Additional Services:
  Laundry Service              $15.00
  Room Service                 $30.00
  Minibar                      $20.00
─────────────────────────────────────
Subtotal:                     $315.00
Tax (0%):                       $0.00
─────────────────────────────────────
TOTAL:                        $315.00

PAYMENTS:
─────────────────────────────────────
Jan 28 - Advance (Cash)       $100.00
Feb 2  - Balance (Mobile)     $215.00
─────────────────────────────────────
Total Paid:                   $315.00
Balance Due:                    $0.00

STATUS: PAID ✓

═══════════════════════════════════════
Thank you for staying with us!
═══════════════════════════════════════
```

---

## Implementation Status

### Currently Implemented ✅
1. ✅ Basic booking creation
2. ✅ Check-in/Check-out process
3. ✅ Payment recording (multiple methods)
4. ✅ Invoice generation
5. ✅ Room status management
6. ✅ Expense tracking with approval
7. ✅ Monthly reports
8. ✅ User role management

### Recommended Enhancements 🔧

#### High Priority:
1. **Booking Modification**
   - Edit check-in/check-out dates
   - Room change functionality
   - Automatic recalculation

2. **Cancellation System**
   - Cancellation status
   - Refund policy engine
   - Automated refund calculation

3. **No-Show Handling**
   - No-show status
   - Automatic room release
   - Advance payment retention

#### Medium Priority:
4. **Group Booking**
   - Link multiple bookings
   - Group payment tracking
   - Bulk operations

5. **Discount System**
   - Discount codes
   - Promotional rates
   - Automatic application

6. **Enhanced Reporting**
   - Occupancy rates
   - Revenue analytics
   - Guest history

#### Low Priority:
7. **Special Requests**
   - Request tracking
   - Fulfillment status
   - Additional charges

8. **Damage Tracking**
   - Incident recording
   - Charge calculation
   - Resolution tracking

---

## Quick Reference Commands

### Check Room Availability
```python
python manage.py shell
from hotel.models import Room, Booking
from datetime import date

# Check specific room
room = Room.objects.get(room_number='102')
conflicts = Booking.objects.filter(
    room=room,
    status__in=['Confirmed', 'Checked-In'],
    check_in_date__lte=date(2026, 2, 5),
    check_out_date__gte=date(2026, 2, 1)
)
print(f"Available: {conflicts.count() == 0}")
```

### Generate Monthly Report
```python
from hotel.models import Payment, Booking
from datetime import datetime

month = 1
year = 2026

payments = Payment.objects.filter(
    date__month=month,
    date__year=year
)

total_income = sum(p.amount for p in payments)
print(f"Income for {month}/{year}: ${total_income}")
```

### Process Early Checkout
```python
from hotel.models import Booking
from datetime import date

booking = Booking.objects.get(id=4)
new_checkout = date(2026, 2, 3)

# Calculate new total
days = (new_checkout - booking.check_in_date).days
new_total = booking.room.price_per_night * days

# Update booking
booking.check_out_date = new_checkout
booking.total_amount = new_total
booking.status = 'Checked-Out'
booking.room.status = 'Available'
booking.room.save()
booking.save()

print(f"Refund due: ${booking.invoice.amount_paid - new_total}")
```

---

## Testing Checklist

### Scenario Testing
- [ ] Test early checkout with refund calculation
- [ ] Test late checkout with additional charges
- [ ] Test booking cancellation with refund policy
- [ ] Test partial payments and balance tracking
- [ ] Test expense approval workflow
- [ ] Test room change with price adjustment
- [ ] Test double booking prevention
- [ ] Test no-show handling
- [ ] Test long-term booking extensions
- [ ] Test invoice generation with all charges

### Edge Cases
- [ ] Same-day check-in and check-out
- [ ] Booking modification after partial payment
- [ ] Multiple room changes
- [ ] Concurrent booking attempts
- [ ] Payment exceeding total amount
- [ ] Negative balance handling
- [ ] Room status consistency
- [ ] Date validation (checkout before check-in)

---

**Document Version:** 1.0  
**Last Updated:** January 30, 2026  
**Maintained By:** KHMS Development Team

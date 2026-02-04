# Kheyre Hotel Management System (KHMS) - Client Presentation Guide

This guide is designed to help you explain the system to your clients or staff. It details the entire workflow from a guest walking in to checking out, and explains the purpose of every data field in the system.

---

## 1. The Guest Journey (Workflow)

This section explains how the system handles a customer ensuring a smooth operation.

### **Phase 1: Guest Arrival & Registration**
**Scenario**: A new guest walks into the hotel reception.
**Action**: The Receptionist navigates to the **Guests** tab and clicks **Add Guest**.

| Field Name | Description | Why is it needed? |
| :--- | :--- | :--- |
| **Full Name** | The complete legal name of the guest. | For invoices and legal records. |
| **Phone Number** | Contact number for the guest. | To contact the guest in emergencies or for booking updates. |
| **ID / Passport** | National ID or Passport Number. | **Security Requirement**: Hotels must identify who is staying. |
| **Address** | Home address of the guest. | Optional, but useful for corporate billing or mailing lists. |

---

### **Phase 2: Booking a Room**
**Scenario**: The guest wants to stay for 3 nights in a "Double" room.
**Action**: Receptionist goes to **Bookings** -> **New Booking**.

1.  **Select Guest**: Choose the guest created in Phase 1.
2.  **Select Room**: The system shows only *Active* rooms.
    *   *Note: If a room is already booked for those dates, the system will error to prevent double-booking.*
3.  **Dates**:
    *   **Check-in Date**: When they arrive (usually today).
    *   **Check-out Date**: When they plan to leave.

**System Logic**:
*   The system automatically calculates: `(Price Per Night) x (Number of Days) = Total Amount`.
*   **Booking Status**: Starts as **"Pending"** or **"Confirmed"**.

---

### **Phase 3: The Check-In**
**Scenario**: The guest is at the desk and ready to go to their room.
**Action**: Receptionist views the Booking Detail and clicks **"Check In Guest"**.

*   **Status Update**: Booking becomes **"Checked-In"**.
*   **Room Update**: Room status changes to **"Occupied"**.
    *   *This prevents anyone else from booking this specific room while the guest is there.*

---

### **Phase 4: Payments & Finance**
**Scenario**: The guest pays an advance of $100 cash.
**Action**: In Booking Detail, scroll to **"Record New Payment"**.

| Field Name | Description | Logic |
| :--- | :--- | :--- |
| **Amount** | How much the guest is paying now. | Deducted from the Total Balance. |
| **Method** | Cash, Mobile Money, or Bank Transfer. | Helps in daily reconciliation (counting cash vs. checking bank). |

*   **Invoice Generation**: The system keeps a live invoice.
    *   **Total Due**: e.g., $300
    *   **Paid**: $100
    *   **Balance**: $200 (System tracks this automatically).

---

### **Phase 5: Check-Out**
**Scenario**: The guest is leaving.
**Action**: Receptionist clicks **"Check Out Guest"**.

**Validation Rule**:
*   The system **checks the balance**.
*   **If Balance > 0**: The system BLOCKS the check-out. It says: *"Outstanding balance remains."*
*   **If Balance == 0**: The Receptionist can proceed.
    *   Booking Status -> **"Checked-Out"**.
    *   Room Status -> **"Available"** (Ready for the next guest).

---

## 2. Field Dictionary (What Every Column Does)

Here is a detailed breakdown of the fields in the system's database and forms.

### **Room Inventory**
| Column | Meaning |
| :--- | :--- |
| **Room Number** | The physical number on the door (e.g., 101, 505). |
| **Room Type** | **Single**: One bed. **Double**: Two beds/Large bed. **Suite**: Luxury. |
| **Price/Night** | The cost for one night stay. Used to calculate total booking cost. |
| **Capacity** | Max people allowed. (For info purposes). |
| **Status** | **Available**: Ready to book. <br>**Occupied**: Guest is inside. <br>**Maintenance**: Broken/Being cleaned (Cannot be booked). |

### **Booking Statuses**
| Status | Meaning |
| :--- | :--- |
| **Pending** | Booking created but not fully confirmed (e.g., waiting for deposit). |
| **Confirmed** | Booking secured. Room is reserved for these dates. |
| **Checked-In** | Guest has arrived and taken the key. Room is now "Occupied". |
| **Checked-Out** | Guest has left. Room is "Available" again. |
| **Cancelled** | Guest didn't come. Room is freed up. |

### **Expenses (Admin Only)**
| Column | Meaning |
| :--- | :--- |
| **Title** | What was bought? (e.g., "Cleaning Supplies"). |
| **Category** | Grouping for reports (e.g., "Maintenance", "Utilities"). |
| **Amount** | Cost of the expense. |
| **Status** | **Pending**: Receptionist added it. <br>**Approved**: Admin verified it (Deducted from profit). <br>**Rejected**: Admin denied it. |

---

## 3. Explaining to Clients: The "Why"
When presenting, use these key points:

1.  **"No More Double Bookings"**: The system physically stops you from booking an occupied room.
2.  **"Financial Control"**: Admins see every penny. Receptionists can collect money, but they can't delete records easily.
3.  **"Professional Invoices"**: Click one button to give the customer a professional bill, not a handwritten note.
4.  **"Anywhere Access"**: Since it's web-based, the Owner can check today's income from their phone (if hosted online).

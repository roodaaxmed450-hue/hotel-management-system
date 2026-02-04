from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Guest, Booking, Invoice, Payment, Expense, AdditionalCharge

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest', 'room', 'check_in_date', 'status', 'get_estimated_total')
    list_filter = ('status', 'check_in_date')
    
    def get_estimated_total(self, obj):
        return f"${obj.get_estimated_total()}"
    get_estimated_total.short_description = 'Estimated Total'

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'status', 'created_by')
    list_filter = ('status', 'date')

class AdditionalChargeAdmin(admin.ModelAdmin):
    list_display = ('booking', 'charge_type', 'description', 'amount', 'date')
    list_filter = ('charge_type', 'date')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Room)
admin.site.register(Guest)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Invoice)
admin.site.register(Payment)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(AdditionalCharge, AdditionalChargeAdmin)

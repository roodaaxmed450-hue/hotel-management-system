from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='hotel/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('rooms/', views.room_list, name='room_list'),
    
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/add/', views.add_guest, name='add_guest'),
    path('guests/<int:guest_id>/edit/', views.edit_guest, name='edit_guest'),
    path('guests/<int:guest_id>/delete/', views.delete_guest, name='delete_guest'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/', views.create_booking, name='create_booking'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('bookings/<int:booking_id>/check-in/', views.check_in, name='check_in'),
    path('bookings/<int:booking_id>/check-out/', views.check_out, name='check_out'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:booking_id>/apply-discount/', views.apply_discount, name='apply_discount'),
    path('bookings/<int:booking_id>/update-dates/', views.update_booking_dates, name='update_booking_dates'),
    path('bookings/<int:booking_id>/invoice/', views.invoice_view, name='invoice_view'),
    path('bookings/<int:booking_id>/charge/add/', views.add_additional_charge, name='add_additional_charge'),
    
    path('payments/<int:payment_id>/delete/', views.delete_payment, name='delete_payment'),
    
    path('reports/', views.flexible_report, name='monthly_report'),
    
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('expenses/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('expenses/<int:expense_id>/approve/', views.approve_expense, name='approve_expense'),
    path('expenses/<int:expense_id>/reject/', views.reject_expense, name='reject_expense'),
    
    path('recycle-bin/', views.recycle_bin, name='recycle_bin'),
    path('recycle-bin/restore/<str:item_type>/<int:item_id>/', views.restore_item, name='restore_item'),
    path('recycle-bin/delete/<str:item_type>/<int:item_id>/', views.permanent_delete_item, name='permanent_delete_item'),
    
    path('search/', views.search, name='search'),
    path('guests/report/', views.guest_report, name='guest_report'),
    path('reports/printable/', views.printable_financial_report, name='printable_financial_report'),
    path('api/search/', views.api_search, name='api_search'),
    # Force Reload Trigger
]

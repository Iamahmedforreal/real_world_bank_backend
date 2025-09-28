from django.contrib import admin
from .models import Customer, Account, Transaction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'kyc_verified', 'created_at')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('kyc_verified', 'created_at')
    ordering = ('-created_at',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'customer', 'account_type', 'balance', 'status', 'created_at')
    search_fields = ('account_number', 'customer__user__username')
    list_filter = ('account_type', 'status', 'created_at')
    ordering = ('-created_at',)
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_account', 'to_account', 'transaction_type', 'status')
    search_fields = ('from_account__account_number', 'to_account__account_number')
    list_filter = ('transaction_type', 'status')
    ordering = ('-id',)
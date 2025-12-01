

# funds/admin.py
from django.contrib import admin
from .models import Wallet, Transaction, FundSettings

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'liquid', 'reserve')
    search_fields = ('user__full_name', 'user__email')  # Search wallets by user

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'performed_by', 'timestamp', 'note')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('wallet__user__full_name', 'wallet__user__email', 'performed_by__full_name', 'note')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)


@admin.register(FundSettings)
class FundSettingsAdmin(admin.ModelAdmin):
    list_display = ('max_deposit_per_transaction', 'daily_deposit_limit_per_user')

    def has_add_permission(self, request):
        # Limit to only one settings instance
        return not FundSettings.objects.exists()




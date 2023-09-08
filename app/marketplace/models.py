from django.db import models
from django.db.models.fields import CharField, PositiveIntegerField, TextField
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save



# Create your models here.
class FeaturedCreators(models.Model):
    sequence_number = PositiveIntegerField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class FeaturedCourses(models.Model):
    sequence_number = PositiveIntegerField()
    course = models.ForeignKey("criticalpath.Course", on_delete=models.CASCADE, null=True, blank=True)

class FeaturedEbooks(models.Model):
    sequence_number = PositiveIntegerField()
    ebook = models.ForeignKey("criticalpath.Ebook", on_delete=models.CASCADE, null=True, blank=True)

class FeaturedWorkshops(models.Model):
    sequence_number = PositiveIntegerField()
    workshop = models.ForeignKey("criticalpath.Workshop", on_delete=models.CASCADE, null=True, blank=True)

class UserProfile(models.Model):
    lightning_address = models.EmailField(null=True, blank=True)
    creator = models.BooleanField(default=False, null=True, blank=False)
    bio = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(default="img1.jpg" ,upload_to='resource/profile_pics/%Y/%m/%D/', null=True, blank=False)
    tiktok_username = models.CharField(max_length=255, null=True, blank=True)
    youtube_username = models.CharField(max_length=255, null=True, blank=True)
    twitter_username = models.CharField(max_length=255, null=True, blank=True)
    twitch_username = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " 's Profile"



# this is to create a wallet and profile each time a new user is created
@receiver(post_save, sender=User)
def wallet_profile_create(sender, instance=None, created=False, **kwargs):
    if created:
        Wallet.objects.create(user=instance,)
        UserProfile.objects.create(user=instance,)



class Charge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=1000)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=1000)
    unit = models.CharField(max_length=50)
    internal_id = models.CharField(max_length=1000)
    external_id = models.CharField(max_length=1000)
    callback_url = models.URLField()
    charge_encoded = models.CharField(max_length=1000)
    uri = models.CharField(max_length=1000)
    fee = PositiveIntegerField(blank=True, null=True)
    created_at = models.CharField(max_length=1000)
    expires_at = models.CharField(max_length=1000)
    last_modified_at = models.DateTimeField(auto_now=True)
    user_credited = models.BooleanField(default=False)

    def __str__(self):
        return self.external_id

class Withdrawal(models.Model):
    amount = PositiveIntegerField()
    unit = CharField(max_length=1000)
    status = CharField(max_length=500, blank=True, null=True)
    external_id = CharField(max_length=1000)
    internal_id = CharField(max_length=1000)
    description = TextField()
    callback_url = models.URLField()
    lnurl_withdrawal_encoded = CharField(max_length=1000)
    uri = CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.CharField(max_length=1000)
    user_credited = models.BooleanField(default=False)


    def __str__(self):
        return self.external_id

class Purchase(models.Model):
    charge = models.ForeignKey(Charge, on_delete=models.CASCADE, null=True, blank=True)
    resource = models.ForeignKey("criticalpath.Resource", on_delete=models.CASCADE, null=True, blank=True)
    journey = models.ForeignKey("criticalpath.Journey", on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey("criticalpath.Course", on_delete=models.CASCADE, null=True, blank=True)
    ebook = models.ForeignKey("criticalpath.Ebook", on_delete=models.CASCADE, null=True, blank=True)
    workshop = models.ForeignKey("criticalpath.Workshop", on_delete=models.CASCADE, null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    paid_at = models.DateField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user) + " purchased " + str(self.resource)

class TransactionType(models.Model):
    # debit & credit
    DEBIT = 0
    CREDIT = 1
    TRANSACTION_TYPES = [
    (DEBIT, 'Debit'),
    (CREDIT, 'Credit'),
    ]
    transaction_type_text = models.IntegerField(choices=TRANSACTION_TYPES)
    def __str__(self):
        return str(self.transaction_type_text)


class TransactionCode(models.Model):
    # we need spread, payout here
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, null=True, blank=True)
    transaction_code_text = models.CharField(max_length=1000)
    def __str__(self):
        return str(self.transaction_code_text)

class Transaction(models.Model):
    description = CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    transaction_code = models.ForeignKey(TransactionCode, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user) +  str(self.transaction_code) + " transaction  " + "for the amount of " + str(self.amount) + " sats"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    def __str__(self):
        return str(self.user) + " has a balance of " + str(self.balance)


#need transaction table for withdrawals + payments of users + sats earned + refund
#need erd diagram
#design flows for withdrawal
#minimum fee of 1 sat

class Currency(models.Model):
    text = CharField(max_length=500)
    iso_code = CharField(max_length=3)

    def __str__(self):
        return self.text
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import random


class Country(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):

    def get_path(instance, filename):
        filename = "{}.{}".format(instance.username, filename.split('.')[1])
        return "users/{}/passport/{}".format(instance.username, filename)

    def get_account_number():
        PREFIX = "67"
        number = random.randrange(10000000, 999999999)
        number = PREFIX + str(number)
        """  if User.objects.filter(account_number  = number).exists() : 
            self.get_account_number()"""
        return number

    ACCOUNT_TYPE = (('Savings', 'SAVINGS'), ('Current', 'CURRENT'))

    
    email_verified = models.BooleanField(default=False, blank=True)
    phone_number = models.CharField(max_length=30, blank=False, null=False)
    phone_number_verified = models.BooleanField(default=False, blank=True)
    occupation = models.CharField(max_length=30)
    date_of_birth = models.DateField(verbose_name="D.O.B", null=True)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    address = models.TextField(null=True)
    account_number = models.CharField(
        default=get_account_number, null=False, max_length=14, unique=True, blank=True)
    account_type = models.CharField(
        default="SAVINGS", max_length=10, choices=ACCOUNT_TYPE)
    passport = models.FileField(
        upload_to=get_path, null=True, verbose_name="photo")


    # admin controls account from here
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True, null=True)

    @property
    def account_number_hidden(self) :
        return  "{}***..*{}{}".format(
        self.account_number[0],
        self.account_number[-2],
        self.account_number[-1]
        )


    @property
    def has_transaction(self) :
        return self.transaction.count() > 0

    @property
    def name(self):
        return "{} {}".format(self.last_name, self.first_name)

    @property
    def dp(self):
        default = ""
        if self.passport:
            return self.passport.url

        else:
            return default

    def __str__(self):
        st = "{} {}".format(self.first_name, self.last_name)
        if not len(st) > 1:
            st = self.username
        return st

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.get_account_number()
        
        super(User, self).save(*args, **kwargs)


class Dashboard(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='dashboard')
    receive_sms = models.BooleanField(default=True)
    receive_email = models.BooleanField(default=True)
    otc = models.PositiveIntegerField(blank=True, null=True)
    otc_expiry = models.DateTimeField(blank=True, null=True)
    applied_for_card = models.BooleanField(default=False)
    applied_for_loan = models.BooleanField(default=False)

    def __str__(self):
        return self.user.__str__()

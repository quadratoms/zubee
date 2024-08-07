from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
from random import randrange, random

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from loanapp.utils import create_virtual_account, idk, transfer_to_account

import jsonfield

class MyUserManager(BaseUserManager):
    def create_user(self, phone, password="1234", **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not phone:
            raise ValueError("Users must have an phone address")
        user = self.model(
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            phone=phone,
            password=password,
            **extra_fields,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class ZubyUser(AbstractBaseUser):
    phone = models.CharField(
        verbose_name="phone number",
        max_length=100,
        unique=True,
    )
    email = models.EmailField(max_length=254)
    activate = models.BooleanField(default=False, null=True)
    # ****noted for attack, user may a have acces to account tr=hrough order means

    is_active = models.BooleanField(default=True)
    is_supervisor = models.BooleanField(default=False, null=True)
    is_admin = models.BooleanField(default=False, null=True)
    is_collector = models.BooleanField(default=False, null=True)
    objects = MyUserManager()
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return str(self.phone)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin or self.is_supervisor or self.is_collector


# def __str__(self):
#     return self.user


class Level(models.Model):
    level = models.IntegerField(default=0, null=True, blank=True)
    quota = models.IntegerField(default=0, null=True, blank=True)


@receiver(post_save, sender=ZubyUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        # all user will have token
    if not instance.is_staff:
        Customer.objects.get_or_create(user=instance)
    else:
        if instance.is_collector:
            Collector.objects.get_or_create(user=instance)
        elif instance.is_supervisor:
            Supervisor.objects.get_or_create(user=instance)
        else:
            pass


class Customer(models.Model):
    level = models.ForeignKey(Level, null=True, blank=True, on_delete=models.CASCADE)
    user = models.OneToOneField(ZubyUser, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    age = models.DateField(null=True, auto_now=False, auto_now_add=False)
    address = models.TextField(null=True, blank=True)
    state = models.IntegerField(null=True, blank=True)
    lga = models.IntegerField(null=True, blank=True)
    job = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(
        upload_to=None,
        null=True,
        blank=True,
        height_field=None,
        width_field=None,
        max_length=None,
    )
    blocked = models.BooleanField(default=False)

    @property
    def fullname(self):
        return "{} {}".format(self.firstname, self.lastname)

    @property
    def loan(self):
        return Loan.objects.filter(customer=self).last()

@receiver(post_save, sender=Customer)
def create_contact(sender, instance:Customer|None=None, created=False, **kwargs):
    if created:
        Contact.objects.create(customer=instance)
        Bankdetail.objects.create(customer=instance)
        levels=Level.objects.all()
        if levels.count()>0:
            instance.level=levels[0]
            instance.save()


class Otp(models.Model):
    user = models.OneToOneField("loanapp.zubyuser", on_delete=models.CASCADE, null=True)
    otp = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    today=models.DateField()
    today_count=models.IntegerField(default=0)


    def set_otp(self, otp_code):
        if self.today==date.today():
            if self.today_count > 4:
                return False
            else:
                self.otp=otp_code
                self.today_count += 1
                self.save()
                return True
        self.otp=otp_code
        self.today=date.today()
        self.today_count=1
        self.save()
        return True

class VirtualAccount(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="virtual_account")
    name = models.CharField(max_length=50, blank=True, null=True)
    acc_no = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    data = models.JSONField(null=True)

    # def create(self, amount):
    #     """
    #     only when user mail is not none
    #     """
    #     email = self.customer.user.email
    #     data = create_virtual_account(email, amount)
    #     # do somethhing with the data


class Card(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cards")
    token = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)
    first_6digits = models.CharField(max_length=50, blank=True, null=True)
    last_4digits = models.CharField(max_length=50, blank=True, null=True)
    issuer = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    expiry = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    data = models.JSONField(null=True)


class Contactlist(models.Model):
    customer = models.OneToOneField(Customer, null=True, on_delete=models.CASCADE)
    contacts = models.JSONField(null=True)

class Image(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE, related_name="customer_name")
    image = models.ImageField(upload_to='customerImage', null=False)


class Bankdetail(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    # the account number and the bvn should be encypt for security sake
    bank_code = models.CharField(blank=True, null=True, max_length=100)
    account_no = models.CharField(blank=True, null=True, max_length=100)
    bvn = models.CharField(blank=True, null=True, max_length=100)
    is_verify = models.CharField(blank=True, null=True, max_length=100)

    def verify(self):
        print(self.customer.user.email)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>")
        data={
            "email": self.customer.user.email,
            "is_permanent": True,
            "narration": self.customer.fullname+ "from zeecash",
            "bvn": self.bvn,
            "name": self.customer.fullname,
            # "tx_ref": self.customer.fullname,
        }
        res= create_virtual_account(data)
        print(res)
        virtual, _=VirtualAccount.objects.get_or_create(customer=self.customer)
        if res['status'] == 'success':
            virtual.acc_no=res['data']['account_number']
            virtual.name=res['data']['bank_name']
            virtual.data=res
            virtual.save()
            return True
        return False




class Guarantor(models.Model):
    # two guarantor per customer
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="guarantors"
    )
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    job = models.CharField(max_length=50, null=True, blank=True)
    relationship = models.CharField(max_length=50, null=True, blank=True)
    id_card = models.ImageField(
        null=True,
        blank=True,
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=None,
    )


class Loanstatus(models.Model):
    status = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.status


class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    collector = models.ForeignKey("Collector", on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=0, null=True, blank=True)
    interest_rate = models.IntegerField(default=30, null=True, blank=True)
    request_date = models.DateField(auto_now=False, auto_now_add=True, null=True, blank=True)
    accept = models.BooleanField(default=False, null=True, blank=True)
    accept_date = models.DateField(null=True, blank=True)
    duration = models.IntegerField(default=14, null=True, blank=True)
    status = models.ForeignKey(Loanstatus, null=True, on_delete=models.PROTECT)
    paid = models.BooleanField(default=False, null=True, blank=True)
    amount_paid = models.IntegerField(default=0, null=True, blank=True)
    last_share = models.IntegerField(default=0, null=True, blank=True)

    @property
    def get_due_payment(self):
        initial = self.amount + (self.amount * self.interest_rate / 100)
        lapse = 0
        if self.accept:
            lapse = (date.today() - (self.accept_date + timedelta(self.duration))).days
        lapse = max(lapse, 0)
        if self.accept and self.accept_date + timedelta(self.duration) > date.today():
            return initial, lapse
        return initial + (self.amount * 0.005 * lapse), lapse

    @property
    def disburst(self) -> bool:
        return self.loanpayment.successful

    @property
    def total_repayment(self):
        return sum(repayment.amount for repayment in self.repayment_set.all())

    def pay(self):
        payment, _ = LoanPayment.objects.get_or_create(loan=self)
        data = {
            "account_bank": Bankdetail.objects.get(customer=self.customer).bank_code,
            "currency": "NGN",
            "amount": self.amount,
            "beneficiary_name": self.customer.fullname,
            "account_number": Bankdetail.objects.get(customer=self.customer).account_no,
            "narration": "Loan disbursement to " + self.customer.fullname,
            "reference": "zeepayout-" + idk(20),
            "callback_url": "whotnews.buzz/paymentdata",
            "debit_currency": "NGN"
        }
        res = transfer_to_account(data)
        payment.successful = True
        payment.account_number = res["data"]["account_number"]
        payment.bank_code = res["data"]["bank_code"]
        payment.full_name = res["data"]["full_name"]
        payment.created_at = res["data"]["created_at"]
        payment.amount = res["data"]["amount"]
        payment.status = res["data"]["status"]
        payment.reference = res["data"]["reference"]
        payment.complete_message = res["data"]["complete_message"]
        payment.bank_name = res["data"]["bank_name"]
        payment.id_from_method = res["data"]["id"]
        payment.save()

    def collate_repayment(self):
        amount = sum(repayment.amount for repayment in self.repayment_set.all())
        self.amount_paid = amount
        self.paid = amount >= self.amount
        self.save()
        return amount

@receiver(post_save, sender=Loan)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if instance.accept and instance.accept_date is None:
        instance.accept_date = date.today() - timedelta(randrange(8))
        instance.save()


class Loanhistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    borrow_date = models.DateField(auto_now=False, auto_now_add=False)
    paid_date = models.DateField(auto_now=False, auto_now_add=False)


class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    ref = models.CharField(blank=True, null=True, max_length=20)
    amount = models.IntegerField(default=0, blank=True)
    paid_at=models.DateTimeField(null=True, blank=True)
    receive_by=models.ForeignKey('Collector', null=True, blank=True, on_delete=models.PROTECT)

    def collate_repayment(self):
        if self.loan:
            self.loan.collate_repayment()


@receiver(post_save, sender=Repayment)
def save_repayment(sender, instance=None, created=False, **kwargs):
    if instance.loan:
        instance.loan.collate_repayment()


class LoanPayment(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.PROTECT)
    ref = models.CharField(blank=True, null=True, max_length=100)
    id_from_method = models.CharField(blank=True, null=True, max_length=100)
    account_number = models.CharField(blank=True, null=True, max_length=100)
    bank_code = models.CharField(blank=True, null=True, max_length=100)
    full_name = models.CharField(blank=True, null=True, max_length=100)
    created_at = models.CharField(blank=True, null=True, max_length=100)
    status = models.CharField(blank=True, null=True, max_length=100)
    reference = models.CharField(blank=True, null=True, max_length=100)
    complete_message = models.CharField(blank=True, null=True, max_length=100)
    bank_name = models.CharField(blank=True, null=True, max_length=100)
    amount = models.CharField(blank=True, null=True, max_length=100)
    successful = models.BooleanField(default=False)


class Supervisor(models.Model):
    user = models.OneToOneField(ZubyUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)


class Collector(models.Model):
    user = models.OneToOneField(ZubyUser, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.PROTECT, null=True, blank=True
    )
    username = models.CharField(max_length=50)
    active = models.BooleanField(
        default=True,
    )
    rep = models.CharField(max_length=50, blank=True, null=True)
    last_cashout=models.DateTimeField(null=True, blank=True)

class Cashout(models.Model):
    user = models.ForeignKey(ZubyUser, on_delete=models.CASCADE)
    start=models.DateTimeField(auto_now_add=True)

    


# class CollectorRecord(models.Model):
#     collector=models.ForeignKey(Collector, on_delete=models.CASCADE)
#     record_for=models.DateField(auto_now=True)
#     total_order=models.PositiveIntegerField(default=0)
#     collected_order=models.PositiveIntegerField(default=0)
#     total_amount=models.PositiveIntegerField(default=0)
#     collected_amount=models.PositiveIntegerField(default=0)

# class Order(models.Model):
#     collector=models.ForeignKey(Collector,on_delete=models.PROTECT, null=True )
#     loan=models.OneToOneField(Loan,on_delete=models.CASCADE)


class Comment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, null=True, related_name="comments"
    )
    collection_type = models.CharField(max_length=20)
    collection_object = models.CharField(max_length=20)
    collection_contact = models.CharField(max_length=20)
    collection_comment = models.TextField()
    collection_status = models.CharField(max_length=20)



class Contact(models.Model):
    customer= models.OneToOneField(
        Customer, on_delete=models.CASCADE, null=True,
    )
    data = jsonfield.JSONField()

class CustomerImage(models.Model):
    customer= models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True,related_name="customer_image"
    )
    image = models.ImageField(
        upload_to="customerImage",
        null=True,
        blank=True,
        height_field=None,
        width_field=None,
        max_length=None,
    )


class PaymentData(models.Model):
    data = jsonfield.JSONField()



# Create your models here.

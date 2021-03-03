from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import (
BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
	
    def create_user(self, phone, password='1234', **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not phone:
            raise ValueError('Users must have an email address')
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



class MyUser(AbstractBaseUser):
    phone=models.IntegerField(verbose_name='phone number',
    unique=True,
    )
    email= models.EmailField(max_length=254)
    activate=models.BooleanField(default= False, null=True)
    # ****noted for attack, user may a have acces to account tr=hrough order means
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']
    
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
        return self.is_admin



@receiver(post_save, sender=MyUser)
def create_auth_token(sender,instance=None,created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
    

class Otp(models.Model):
    user= models.OneToOneField("loanapp.myuser", on_delete=models.CASCADE, null=True)
    otp= models.IntegerField(blank=True,null=True)
    created= models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    # def __str__(self):
    #     return self.user
    

class Level(models.Model):
    level=models.IntegerField(default=0, null=True, blank=True)
    quota=models.IntegerField(default=0, null=True, blank=True)
    

class Costumer(models.Model):
    level= models.ForeignKey(Level,null=True, blank=True, on_delete=models.CASCADE)
    user=models.OneToOneField(MyUser, on_delete=models.CASCADE)
    age=models.DateField(auto_now=False, auto_now_add=False)
    address=models.TextField(null=True, blank=True)
    job=models.CharField(max_length=50, blank=True, null=True)
    image=models.ImageField(upload_to=None,null=True, blank=True,
    height_field=None, width_field=None, max_length=None)
    blocked=models.BooleanField(default=False)

class Contactlist(models.Model):
    costumer= models.OneToOneField(Costumer, null=True, on_delete=models.CASCADE)
    contacts=models.JSONField()





class Bankdetail(models.Model):
    costumer= models.OneToOneField(Costumer, on_delete=models.CASCADE)
    #the account number and the bvn should be encypt for security sake
    account_no= models.CharField(blank=True, null=True, max_length=100)
    bvn= models.CharField(blank=True, null=True, max_length=100)
    debit_card= models.CharField(blank=True, null=True, max_length=100)

    

    # def getname(self):
    #     name= self.user.first_name+' '+self.user.last_name
    #     return name

class Guarantor(models.Model):
    #two guarantor per costumer
    costumer=models.ForeignKey(Costumer, on_delete=models.CASCADE)
    name=models.CharField(max_length=50, blank=True, null=True)
    job= models.CharField(max_length=50, null=True, blank=True)
    id_card= models.ImageField(null=True, blank=True,upload_to=None,
    height_field=None, width_field=None, max_length=None)





class Loan(models.Model):
    costumer=models.OneToOneField(Costumer, on_delete=models.CASCADE)
    amount=models.IntegerField(default=0, null=True, blank=True)
    interest_rate= models.IntegerField(default=30,null=True, blank=True)
    request_date= models.DateField(auto_now=False, auto_now_add=True, null=True, blank=True)
    accept= models.BooleanField(default=False, null=True, blank=True)
    accept_date=models.DateField(null=True, blank=True)
    duration= models.IntegerField(default=14,null=True, blank=True)
    paid= models.BooleanField(default=False, null=True, blank=True)
    
    @property
    def get_due_payment(self):
        initial= self.amount + (self.amount * self.interest_rate/100)
        print('init', initial)
        lapse= (date.today() - (self.accept_date + timedelta(self.duration))).days
        if lapse <= 0:
            lapse=0
        if self.accept_date + timedelta(self.duration) > date.today():
            # print(self.accept_date+timedelta(self.duration))
            # print(date.today())
            return initial, lapse
        
        print(lapse)
        # assumming that one percent incrase every day after lapse day
        return initial + (self.amount*0.005 * lapse), lapse
    
    # def due(self):
    #     if date.today 

class Loanhistory(models.Model):
    costumer=models.ForeignKey(Costumer, on_delete=models.CASCADE)
    amount=models.IntegerField(default=0)
    borrow_date= models.DateField(auto_now=False, auto_now_add=False)
    paid_date=  models.DateField(auto_now=False, auto_now_add=False)



# Create your models here.

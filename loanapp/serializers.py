from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

from rest_framework.authtoken.models import Token


class Levelserializer(serializers.ModelSerializer):
    class Meta:
        model= Level
        fields= '__all__'

class Bankdetailserializer(serializers.ModelSerializer):
    class Meta:
        model= Bankdetail
        fields= '__all__'

class Guarantorserializer(serializers.ModelSerializer):
    class Meta:
        model= Guarantor
        fields= '__all__'

class LOanserializer(serializers.ModelSerializer):
    class Meta:
        model= Loan
        fields= '__all__'



class Costumerserializer(serializers.ModelSerializer):
    level= Levelserializer(read_only=True)
    loan= LOanserializer(read_only=True)
    bankdetail= Bankdetailserializer(read_only=True,)
    guarantor= Guarantorserializer(many=True, read_only=True)
    class Meta:
        model= Costumer
        fields= '__all__'

class Userserializer(serializers.ModelSerializer):
    costumer= Costumerserializer(read_only=True)
    
    class Meta:
        model= MyUser
        fields= ['phone', 'password', 'costumer',]
        extra_kwargs= {"password":{'write_only': True}}

    def save(self):
        user=MyUser(phone=self.validated_data['phone'])
        user.set_password(self.validated_data['password'])
        user.save()
        Token.objects.create(user=user).save()


class Otpserializer(serializers.ModelSerializer):
    class Meta:
        models=Otp
        fields= '__all__'
    
    def save(self):
        otp= Otp.objects.get_or_create(phone=self.validated_data['phone'])
        


#.....
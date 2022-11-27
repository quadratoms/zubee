from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

from rest_framework.authtoken.models import Token


class Levelserializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class Bankdetailserializer(serializers.ModelSerializer):
    class Meta:
        model = Bankdetail
        fields = ["bank_name", "account_no"]

class Commentserializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields=[
            'costumer',
            'collection_type',
            'collection_object',
            'collection_contact',
            'collection_comment',
            'collection_status',
        ]

class Guarantorserializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantor
        fields = ["address", "relationship", "name", "job", "phone"]


class LOanserializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "id",
            "costumer",
            "amount",
            "interest_rate",
            "request_date",
            "accept",
            "accept_date",
            "duration",
            "status",
            "paid",
            "get_due_payment",
            "disburst",
            "total_repayment",
        ]


class Costumerserializer(serializers.ModelSerializer):
    comments=Commentserializer(many=True, read_only=True)
    level = Levelserializer(read_only=True)
    loans = LOanserializer(many=True, read_only=True)
    bankdetail = Bankdetailserializer(
        read_only=True,
    )
    guarantors = Guarantorserializer(many=True)

    class Meta:
        model = Costumer
        fields = [
            "id",
            "firstname",
            "fullname",
            "lastname",
            "age",
            "address",
            "state",
            "lga",
            "job",
            # "image",
            "blocked",
            "loans",
            "bankdetail",
            "level",
            "guarantors",
            "comments"
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "firstname": {"read_only": True},
            "lastname": {"read_only": True},
        }


class Loanserializer(serializers.ModelSerializer):
    costumer = Costumerserializer(read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "costumer",
            "amount",
            "interest_rate",
            "request_date",
            "accept",
            "accept_date",
            "duration",
            "status",
            "paid",
            "get_due_payment",
            "disburst",
            "total_repayment",
        ]


class UserSerializer(serializers.ModelSerializer):
    costumer = Costumerserializer(read_only=True)

    class Meta:
        model = ZubyUser
        fields = [
            "phone",
            "password",
            "costumer",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self):
        user = ZubyUser(phone=self.validated_data["phone"])
        user.set_password(self.validated_data["password"])
        user.save()
        Token.objects.create(user=user).save()


class Otpserializer(serializers.ModelSerializer):
    class Meta:
        models = Otp
        fields = "__all__"

    def save(self):
        otp = Otp.objects.get_or_create(phone=self.validated_data["phone"])


class Collectorserializer(serializers.ModelSerializer):
    class Meta:
        models = Collector
        fields = "__all__"


# .....

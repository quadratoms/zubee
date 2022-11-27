from django.test import TestCase
from paystackapi import transaction
import requests

a= transaction.Transaction(secret_key="sk_test_ac7e6b6b04b712d76676cd40230e4db141f8b9e6")
# print(a.initialize(email="quadratoms30@gmail.com", amount="5000"))
# print(a.verify('dlynx2lfhr'))
# print(a.charge(authorization_code='AUTH_hqk9prabpv', email="quadratoms30@gmail.com", amount="20000"))
# Create your tests here.
data = {"customer": '100000000',
    "preferred_bank": "wema-bank",
    "first_name":"kunle",
    "last_name":'kunule',
    "phone":"09067585648",
    "email":"Qu@t.com",
    }
resp = requests.post(
    "https://api.paystack.co/dedicated_account",data=data,headers={'Content-Type':'application/json','Authorization':"Bearer pk_test_beac4efb5dcee8173e8ff51677bb2d102d15fae7"}
)
print(resp)

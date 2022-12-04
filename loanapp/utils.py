import json
from random import choice
import string
from .constant import  FLUTTERWAVE_SECRET_KEY
from rave_python import rave
import requests
from .constant import FLUTTERWAVE_PUBLIC_KEY


def idk(i):
    l=[]
    for each in range(i):
        l.append(choice(string.digits))
    n=''.join(l)
    return n


def create_virtual_account():
    # v=rave.VirtualAccount(FLUTTERWAVE_PUBLIC_KEY,FLUTTERWAVE_SECRET_KEY, production=False, usingEnv=False)

    r=requests.post('https://api.flutterwave.com/v3/virtual-account-numbers',json=
    {
            "email": "quadratoms30@gmail.com",
            "seckey": FLUTTERWAVE_SECRET_KEY,
            "is_permanent": True,
            "narration": "narrations",
            # "amount":"500",
                "bvn": "59836771570",
            "name":"tosin quadri","tx_ref":"tosin124",


        },
        headers={
        "Authorization":"Bearer "+FLUTTERWAVE_SECRET_KEY
        })
    # res = rave.VirtualAccount.create(v,
    #     accountDetails={
    #         "email": "quadratoms30@gmail.com",
    #         "seckey": FLUTTERWAVE_SECRET_KEY,
    #         "is_permanent": False,
    #         "narration": "narrations",
    #         "amount":"500",
    #         "name":"tosin quadri"
    #     }
    # )
    print(r.json())
    return r
# create_virtual_account()

def verifypayment(ref):
    url="https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref="+ref
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+FLUTTERWAVE_SECRET_KEY
    }

    res = requests.request("get", url, headers=headers)

    print(res.text)
    return res.json()
def chargecard():
    v=rave.Card(FLUTTERWAVE_PUBLIC_KEY,FLUTTERWAVE_SECRET_KEY, production=False, usingEnv=False)
    res = rave.Card.charge(v, 
     cardDetails={
        "token":"flw-t1nf-652a8d930e805421a0f8e99b18c4489e-m03k",
    "country":"NG",
    "amount":1000,
    "email":"customer-email@example.com",
    "firstname":"temi",
    "lastname":"Oyekole",
    "IP":"190.233.222.1",
    "txRef":"MC-7666-YU",
    "currency":"NGN",
    'txRef': '8888488448'
        },chargeWithToken=True
    )
    print(res)
    return res
# chargecard()
# def transfer_to_account(data):
#     v=rave.Transfer(FLUTTERWAVE_PUBLIC_KEY,FLUTTERWAVE_SECRET_KEY, production=False, usingEnv=False)
#     res = rave.Transfer.initiate(v,data
#         # transferDetails={
#         #     "name": "user@example.com",
#         #     "seckey": FLUTTERWAVE_SECRET_KEY,
#         #     "is_permanent": False,
#         #     "narration": "narrations"
#         # }
#     )
    return res

def transfer_to_account(data):
    url = "https://api.flutterwave.com/v3/transfers"

    payload = json.dumps(data)
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+FLUTTERWAVE_SECRET_KEY
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.json()

# transfer_to_account()

def bvnl():
    r=requests.post('https://api.paystack.co/bvn/match',json=
    {
            # "amount":"500",
                "bvn": "59836771570",
            "account_number": "2085971163", 
     "bank_code": "033", 
     "first_name": "tosin", 
     "last_name": "quadri",
     "middle_name": "micheal"


        },
        headers={
        "Authorization":"Bearer sk_live_77c1afdee608d5d367778e3cbbc6d25c1c209104"
        })
    print(r.json())
    return r

def bvn():
    r=requests.get("https://api.flutterwave.com/v3/kyc/bvns/22367715797", headers={
        "Authorization":"Bearer FLWSECK-2a552f68bf49ea88fc33ea8f8920885d-X"
        })

    print(r.json())


# from .collector import data
# from .models import ZubyUser

# for each in data:
#     print(each)
#     z=ZubyUser(phone=each['phone'],is_collector=each['is_collector'],is_active=each['is_active'])
#     z.set_password("123456")
#     z.save()
    
# bvn()
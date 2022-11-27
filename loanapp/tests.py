from django.test import TestCase

import datetime

# {"status": "successful", "transaction_id": "3887103", "tx_ref": "tcd873766377373"}
{
    "error": False,
    "transactionComplete": True,
    "txRef": "tcd873766377373",
    "flwRef": "FLW-MOCK-c92d2374e5bd52d1062a7f2721aff609",
    "amount": 2000,
    "chargedamount": 2000,
    "cardToken": "flw-t1nf-652a8d930e805421a0f8e99b18c4489e-m03k",
    "vbvmessage": "successful",
    "chargemessage": "Please enter the OTP sent to your mobile number 080****** and email te**@rave**.com",
    "chargecode": "00",
    "currency": "NGN",
    "meta": [
        {
            "id": 202974267,
            "metaname": "__CheckoutInitAddress",
            "metavalue": "https://ravemodal-dev.herokuapp.com/v3/hosted/pay",
            "createdAt": "2022-10-23T00:49:54.000Z",
            "updatedAt": "2022-10-23T00:49:54.000Z",
            "deletedAt": None,
            "getpaidTransactionId": 3887103,
        }
    ],
}
print(help(datetime))
a = True or False
print(a)
# Create your tests here.

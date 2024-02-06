from pickle import FALSE
import time
from django.shortcuts import render, redirect
import requests as req
import datetime
from rest_framework import status, generics

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
import phonenumbers
from loanapp.constant import FLUTTERWAVE_PUBLIC_KEY

from loanapp.utils import send_message, verifypayment
from .models import *
from .serializers import (
    Imageserializer,
    UserSerializer,
    Otpserializer,
    Customerserializer,
    Bankdetailserializer,
    Guarantorserializer,
    LOanserializer,
)
from rest_framework.views import APIView
import string
from random import choice
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from django.contrib.auth import authenticate, login, logout


def idk(i):
    """
    Generates a string of random digits.

    Args:
        i (int): The length of the string.

    Returns:
        str: The generated string.
    """
    return "".join([choice(string.digits) for _ in range(i)])


@api_view(["POST"])
def login(request):
    phone = request.data.get('phone')
    password = request.data.get('password')

    if not phone or not password:
        return JsonResponse({'error': 'phone and password are required'}, status=400)

    user = authenticate(username=phone, password=password)
    if user is not None:
        if user.is_active:
            # login(request, user)
            data = {"username": phone, "password": password}
            res = requests.post(settings.API_TOKEN_AUTH, data=data)
            if res.status_code == 200:
                return JsonResponse(res.json())
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=400)
        else:
            return JsonResponse({'message': 'Your account is not activated, please contact the administrator'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid credentials'}, status=400)

@api_view(["GET"])
def pay(request):
    # if request.user.customer.loan.get_due_payment[1] == 0:
    #     print(request.user.customer.loan.get_due_payment[1])
    #     return Response(
    #         {"message": "your loan is not due for payment, contact admin"},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )
    # payment method to be apply later
    request.user.customer.loan.paid = True
    request.user.customer.loan.paid.save()
    # if condition to migrate to loanhistry if paid it true, before deleting
    request.user.customer.loan.delete()
    return Response({"message": "paid"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def apply(request, amount, dur=14, obj=None):
    existing = False
    try:
        if request.user.customer.loan_set.all().count() > 0:
            loan = request.user.customer.loan_set.all().last()
            if not loan.paid:
                existing = True
    except:

        pass

    if existing:
        return Response(
            {"message": "already apply", "status": "failed"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.user.customer.level.quota < amount and obj is None:
        # the user should be block, asking more than your quota is imposible from user interface
        return Response(
            {"message": "min amount exceeded", "status": "failed"},
            status=status.HTTP_403_FORBIDDEN,
        )

    virtual=VirtualAccount.objects.filter(customer=request.user.customer)
    card= Card.objects.filter(customer=request.user.customer)
    contact=Contact.objects.filter(customer=request.user.customer)
    if contact.exists():
        if len(contact[0].data)<30:
            return Response(
                {"message": "Your Loan cant be process, no enough data "},
                status=status.HTTP_403_FORBIDDEN)
    if virtual.exists() or card.exists():
        loan = Loan(customer=request.user.customer, amount=amount, duration=dur, obj=(obj == None))
        loan.save()
        return Response(
            {"message": "Your Loan is processing", "status": "success"},
            status=status.HTTP_201_CREATED,
        )
    return Response(
            {"message": "Your Loan can't be process verify you bvn and bank details", "status": "fail"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["GET"])
def due(request):
    # there is an error if we try to get for not yet accepted laon
    a = request.user.customer.loan.get_due_payment
    print(a)
    return Response({"due": a[0], "lapse": a[1]}, status=status.HTTP_200_OK)


@api_view(["GET"])
def userstatus(request):
    print(request.user.customer)
    token = Token.objects.get(user=request.user)
    print(token)

    serialize = UserSerializer(instance=request.user)

    return Response(serialize.data)


# {
#     "event": "charge.completed",
#     "data": {
#         "id": 782728102,
#         "tx_ref": "3456787654",
#         "flw_ref": "MURANDACLOTHING/PDMF36181670742405988211",
#         "device_fingerprint": "7b5f1997b6e362db78f5f82d7ca536c3",
#         "amount": 60,
#         "currency": "NGN",
#         "charged_amount": 60,
#         "app_fee": 0.84,
#         "merchant_fee": 0,
#         "processor_response": "Approved by Financial Institution",
#         "auth_model": "PIN",
#         "ip": "102.89.33.59",
#         "narration": "CARD Transaction ",
#         "status": "successful",
#         "payment_type": "card",
#         "created_at": "2022-12-11T07:06:45.000Z",
#         "account_id": 1941914,
#         "customer": {
#             "id": 481105569,
#             "name": "Anonymous customer",
#             "phone_number": null,
#             "email": "quadratoms30@gmail.com",
#             "created_at": "2022-12-11T07:06:45.000Z",
#         },
#         "card": {
#             "first_6digits": "539983",
#             "last_4digits": "7238",
#             "issuer": "MASTERCARD GUARANTY TRUST BANK Mastercard Naira Debit Card",
#             "country": "NG",
#             "type": "MASTERCARD",
#             "expiry": "12/24",
#         },
#     },
#     "event.type": "CARD_TRANSACTION",
# }

# {
#     "status": "success",
#     "message": "Transaction fetched successfully",
#     "data": {
#         "id": 782728102,
#         "tx_ref": "3456787654",
#         "flw_ref": "MURANDACLOTHING/PDMF36181670742405988211",
#         "device_fingerprint": "7b5f1997b6e362db78f5f82d7ca536c3",
#         "amount": 60,
#         "currency": "NGN",
#         "charged_amount": 60,
#         "app_fee": 0.84,
#         "merchant_fee": 0,
#         "processor_response": "Approved by Financial Institution",
#         "auth_model": "PIN",
#         "ip": "102.89.33.59",
#         "narration": "CARD Transaction ",
#         "status": "successful",
#         "payment_type": "card",
#         "created_at": "2022-12-11T07:06:45.000Z",
#         "account_id": 1941914,
#         "card": {
#             "first_6digits": "539983",
#             "last_4digits": "7238",
#             "issuer": "GUARANTY TRUST BANK Mastercard Naira Debit Card",
#             "country": "NIGERIA NG",
#             "type": "MASTERCARD",
#             "token": "flw-t1nf-d15400264a2d118dba1e712ffe1ceff5-k3n",
#             "expiry": "12/24",
#         },
#         "meta": {
#             "__CheckoutInitAddress": "https://checkout.flutterwave.com/v3/hosted/pay"
#         },
#         "amount_settled": 59.16,
#         "customer": {
#             "id": 481105569,
#             "name": "Anonymous customer",
#             "phone_number": "N/A",
#             "email": "quadratoms30@gmail.com",
#             "created_at": "2022-12-11T07:06:45.000Z",
#         },
#     },
# }


@api_view(["POST"])
def createnewuser(request):
    # this code is useless for now

    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def get_otp(request):

    otp_code = idk(6)
    serializer = UserSerializer(instance=request.data)
    # if serializer.is_valid():
    # print(serializer.data)
    user, newuser = ZubyUser.objects.get_or_create(
        phone=request.data["phone"],email=request.data.get("email")
    )

    otp, _ = Otp.objects.get_or_create(user=user)
    otp.otp = otp_code
    otp.created = datetime.datetime.today()
    print(otp_code)
    otp.save()
    s = otp.set_otp(otp_code)

    if s:
        phone = phonenumbers.parse("+234" + request.data["phone"])
        print(phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164))
        phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)

        send_message(
            {
                "contacts": [phone],
                "sender_id": "Atomus",
                "message": "Hello Zeecash is here, your otp  is " + otp_code,
                # "send_date": "14-12-2022 00:42",
                "priority_route": False,
                "campaign_name": "Testing",
            }
        )
        return Response({"massage": "ok"}, status=status.HTTP_200_OK)
    return Response(
        {"massage": "try again tommorrow"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def verify_otp(request):
    print(request.data)
    try:
        user = ZubyUser.objects.get(phone=request.data["phone"])
        otp = Otp.objects.get(otp=request.data["otp"], user=user)
    except Exception as inst:
        print(inst)
        return Response(
            {"message": "otp not found"}, status=status.HTTP_400_BAD_REQUEST
        )
    t = datetime.datetime.today()
    expire = datetime.timedelta(minutes=6)
    created = otp.created.replace(tzinfo=None)
    print("now", t.time())
    print("exp", expire)
    print(created)
    if t - created > expire:
        return Response({"message": "otp expired"})
    else:

        user.activate = True
        user.set_password(request.data["password"])
        print(type(user.email))
        if request.data["email"] is not None:
            print(request.data["email"])
            print("???????????????????????????????????")
            if user.email == "":

                user.email = request.data["email"]
                print(user.email)
                print(">>>>>>>>>>>>>>>>>>>>>>>>")
        user.save()
        print(user.email)
        return Response({"message": "account activate"}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT", "POST"])
def customerprofile(request):
    print(request.user)
    print(request._request)
    if request.method == "GET":
        customer = Customer.objects.get(user=request.user)
        serializer = Customerserializer(customer)
        return Response(serializer.data)

    if request.method == "PUT":
        customer = Customer.objects.get(user=request.user)
        serializer = Customerserializer(customer, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"data": serializer.data, "status": "success"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "your personal detail was not updated ", "status": "failed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.method == "POST":
        serializer = Customerserializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "POST"])
def bankdetail(request):

    if request.method == "GET":
        bankdetail, _ = Bankdetail.objects.get_or_create(customer=request.user.customer)
        serializer = Bankdetailserializer(bankdetail)
        return Response(serializer.data)

    if request.method == "PUT":
        bankdetail, _ = Bankdetail.objects.get_or_create(customer=request.user.customer)
        serializer = Bankdetailserializer(bankdetail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "status": "success"},
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.methed == "POST":
        serializer = Bankdetailserializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def verify_bvn(request):
    bankdetail, _ = Bankdetail.objects.get_or_create(customer=request.user.customer)
    bankdetail.bvn = request.data["bvn"]

    valid_bvn = False
    if bankdetail.account_no != "":
        # time.sleep(5)
        valid_bvn = bankdetail.verify()
    if valid_bvn:
        bankdetail.save()
        return Response(
            {"message": "bvn verify and virtual account is created"},
            status=status.HTTP_202_ACCEPTED,
        )
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "POST"])
def customer_guarantor(request):

    if request.method == "GET":
        guarantor = Guarantor.objects.filter(customer=request.user.customer)
        print(guarantor)
        serializer = Guarantorserializer(guarantor, many=True)
        print(serializer.data)
        return Response(serializer.data)

    if request.method == "PUT":
        guarantor = Guarantor.objects.filter(customer=request.user.customer)
        print(guarantor)
        for g in range(2):
            if guarantor.count() < g + 1:
                Guarantor.objects.create(customer=request.user.customer)
        guarantor = Guarantor.objects.filter(customer=request.user.customer)

        print(request.data)
        for item in request.data:
            serializer = Guarantorserializer(
                guarantor[request.data.index(item)], data=item
            )
            # print(serializer)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            print(serializer.data)
        return Response(
            {"data": serializer.data, "status": "success"}, status=status.HTTP_200_OK
        )

    if request.method == "POST":
        serializer = Guarantorserializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def loandetail(request):

    if request.method == "GET":
        guarantor = Loan.objects.get(customer=request.user.customer)
        serializer = LOanserializer(guarantor)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = LOanserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET','POST'])
# def customerprofile(request):
#     if request.method=='GET':
#         customer=Customer.objects.get(user=request.user)
#         serializer=Customerserializer(customer)

#     if request.method=='POST':
#         serializer=UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#     return Response(serializer.data)


# @api_view(['GET', 'POST'])
# def comment(request, id):
#     if  request.method=='GET':
#         newscontent= Newsmodel.objects.get(id=id)
#         newscomment= newscontent.comment_set.all().order_by('-time')
#         serialize= Commentserializer(newscomment, many=True)
#     if request.method=='POST':
#         serialize= Commentserializer(data=request.data)
#         if serialize.is_valid():
#             serialize.save()

#     return Response(serialize.data)


@api_view(["GET"])
def get_repayment_ref(request, id):
    """
    Retrieves the repayment reference for a given loan.

    Args:
        request (HttpRequest): The HTTP request object containing information about the request.
        id (int): The ID of the loan for which the repayment reference is to be retrieved.

    Returns:
        Response: A JSON response containing the repayment reference.

    Example Usage:
        # Assuming there is a loan with id=1
        response = get_repayment_ref(request, 1)
        print(response)
    """
    loan = Loan.objects.get(id=id)
    ref = "ZRM" + idk(17)
    # print(loan.repayment_set.all().last().amount)
    if loan.repayment_set.all().count() == 0:
        repayment = Repayment.objects.create(loan=loan, ref=ref)
        print
        return Response({"message": repayment.ref})
    print("was here")
    if loan.repayment_set.all().last().amount != 0:
        repayment = Repayment.objects.create(loan=loan, ref="ZRM" + idk(17))
        return Response({"message": repayment.ref})
    print(ref)
    ref = Repayment.objects.filter(loan=loan).last().ref
    print(ref)
    return Response({"message": ref, "pulic_key":FLUTTERWAVE_PUBLIC_KEY})


@api_view(["GET"])
def verify_repayment(request, ref):
    # change ref to alpha numeric to prevent reoccurence
    try:
        repayment = Repayment.objects.get(ref=ref)
    except:
        return Response({"message": "ref exit not"})
    if repayment:
        try:
            res = verifypayment(ref)
            # print(res["amount"])
            # i dont think card eed to be save here o
            # Card.objects.get_or_create(customer=request.user.customer, token=res['flwRef'], ref=res['txRef'] )
            repayment.amount = res["data"]["amount"]
            repayment.save()
            print("i wass here")
        except:
            return Response(
                {"message": "flutter error"}, status=status.HTTP_424_FAILED_DEPENDENCY
            )

    return Response(
        {"message": "repayment successful"}, status=status.HTTP_202_ACCEPTED
    )


@api_view(["GET"])
def confirm_repayment_paid(request):
    # user = request.user
    print(222)
    print(request.user.customer)
    customer = request.user.customer
    loans = Loan.objects.filter(customer=customer, paid=False)
    for loan in loans:
        loan.collate_repayment()
    return Response({"message": "ok"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def add_contact(request):
    # user = request.user
    print(request.user)
    request.user.customer.contact.data = request.data
    request.user.customer.contact.save()

    return Response({"message": "ok contact"}, status=status.HTTP_202_ACCEPTED)


class ImageViewSet(generics.CreateAPIView):
    # queryset = CustomerImage.objects.all()
    serializer_class = Imageserializer

    def post(self, request, *args, **kwargs):
        print(request.user)
        file = request.data["image"]
        phone = request.data["phone"]
        print(file)
        print(phone)
        image = CustomerImage.objects.create(
            image=file, customer=ZubyUser.objects.get(phone=phone).customer
        )
        return JsonResponse({"received": "success"})


# @api_view(['POST'])
# def imageupload(request):
#     # user = request.user
#     print(request.user)
#     print(request.FILES)
#     CustomerImage.objects.create(image=request.FILES['image'], customer=request.user.customer)
#     return Response({"received": "success"},status=status.HTTP_202_ACCEPTED)

#     # return JsonResponse({"received": "success"})


@api_view(["POST"])
def payment_data(request):
    # user = request.user
    data = request.data["data"]
    if "save" in data["tx_ref"]:
        res = verifypayment(data["tx_ref"])
        if res["status"] == "success":
            email = res["data"]["customer"]["email"]
            first_6digits = res["data"]["card"]["first_6digits"]
            last_4digits = res["data"]["card"]["last_4digits"]
            issuer = res["data"]["card"]["issuer"]
            cardtype = res["data"]["card"]["type"]
            token = res["data"]["card"]["token"]
            expiry = res["data"]["card"]["expiry"]
            try:
                customer = ZubyUser.objects.get(email=email).customer
                Card.objects.create(
                    customer=customer,
                    first_6digits=first_6digits,
                    last_4digits=last_4digits,
                    issuer=issuer,
                    type=cardtype,
                    token=token,
                    expiry=expiry,
                    data=res["data"],
                )
            except:
                print("===========")
    PaymentData.objects.create(data=request.data)

    return Response({"message": "ok "}, status=status.HTTP_202_ACCEPTED)


# Create your views here.

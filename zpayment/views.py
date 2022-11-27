from django.shortcuts import render
import paystackapi
# from rave_python
from paystackapi.verification import Verification
from rest_framework.response import Response
from rest_framework.decorators import api_view



@api_view(['POST'])
def accountverify(request):
	print(request.data['bank'])
	a= Verification.verify_account(account_number=request.data['accno'],
		bank_code=request.data['bank'], currency="NGN")
	return Response(a)


@api_view(['POST'])
def bvnverify(request):
	print(request.data)
	a= Verification.verify_bvn(bvn=request.data['bvn'])
	return Response(a)

@api_view(['POST'])
def phoneverify(request):
	print(request.data)
	a= Verification.verify_phone(verification_type=request.data['type'],phone=request.data['phone'])
	return Response(a)

@api_view(['POST'])
def cardverify(request):
	print(request.data)
	a= Verification.verify_card_bin(card_bin=request.data['cardno'],)
	return Response(a)


# Create your views here.

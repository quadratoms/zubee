from django.shortcuts import render
import paystackapi
# from rave_python
from paystackapi.verification import Verification
from rest_framework.response import Response



def accountverify(request):
	print(request.data)
	a= Verification.verify_account(account_number=request.data['accno'],
		bankcode=request.data['bank'])
	return Response(a)


def bvnverify(request):
	print(request.data)
	a= Verification.verify_bvn(bvn=request.data['bvn'])
	return Response(a)

def phoneverify(request):
	print(request.data)
	a= Verification.verify_phone(verification_type=request.data['type'],phone=request.data['phone'])
	return Response(a)

def cardverify(request):
	print(request.data)
	a= Verification.verify_card_bin(card_bin=request.data['cardno'],)
	return Response(a)


# Create your views here.

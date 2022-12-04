from pickle import FALSE
from django.shortcuts import render, redirect
import requests as req
import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from loanapp.utils import verifypayment
from .models import *
from .serializers import ( UserSerializer, Otpserializer,Costumerserializer, 
Bankdetailserializer, Guarantorserializer, LOanserializer)
from rest_framework.views import APIView
import string
from random import choice

from django.contrib.auth import authenticate, login, logout



def idk(i):
    l=[]
    for each in range(i):
        l.append(choice(string.digits))
    n=''.join(l)
    return n

@api_view(['POST'])
def login(request):
    print(request.data)
    user, newuser=ZubyUser.objects.get_or_create(phone=request.data['phone'],)
    if user.activate:
        data={
            'username': request.data['phone'],
            'password': request.data['password']
        }
        # user= authenticate(request, username=request.data['phone'], password=request.data['password'])
        # if user is not None:
        #     login(request,user)
        a=req.post('http://192.168.204.1:8000/api-token-auth/', data=data)
        print(a.json())

        return Response(a.json())
    print(6666)
    return Response({'message': 'you do not own an account or forgetten password'},
    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def pay(request):
    if request.user.costumer.loan.get_due_payment[1]==0:
        print(request.user.costumer.loan.get_due_payment[1])
        return Response({'message' : 'your loan is not due for payment, contact admin'},
        status=status.HTTP_400_BAD_REQUEST)
    # payment method to be apply later
    request.user.costumer.loan.paid=True
    request.user.costumer.loan.paid.save()
    # if condition to migrate to loanhistry if paid it true, before deleting
    request.user.costumer.loan.delete()
    return Response({'message': 'paid'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def apply(request, amount, dur=14):
    existing=False
    try:
        if request.user.costumer.loan_set.all().count()>0:
            loan=request.user.costumer.loan_set.all().last()
            if not loan.paid:
                existing=True
    except:
        
        pass

    if existing:
        return Response({'message':'already apply', 'status':'failed'},status=status.HTTP_403_FORBIDDEN)
    
    if request.user.costumer.level.quota < amount:
        # the user should be block, asking more than your quota is imposible from user interface
        return Response({'message':'min amount exceeded', 'status':'failed'},status=status.HTTP_403_FORBIDDEN)
    loan= Loan(costumer=request.user.costumer, amount=amount, duration=dur)
    loan.save()
    return Response({'message':'Your Loan is processing', 'status':'success'},status=status.HTTP_201_CREATED)



@api_view(['GET'])
def due(request):
    # there is an error if we try to get for not yet accepted laon
    a=request.user.costumer.loan.get_due_payment
    print(a)
    return Response({'due': a[0], 'lapse': a[1]}, status=status.HTTP_200_OK)


@api_view(['GET'])
def userstatus(request):
    print(request.user.costumer)
    token=Token.objects.get(user=request.user)
    print(token)

    serialize= UserSerializer(instance=request.user)
    
    return Response(serialize.data)





@api_view(['POST'])
def createnewuser(request):
    # this code is useless for now

    if request.method=='POST':
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def get_otp(request):

    otp_code=idk(6)
    serializer= UserSerializer(instance=request.data)
    # if serializer.is_valid():
    # print(serializer.data)
    user, newuser = ZubyUser.objects.get_or_create(phone=serializer.data['phone'],)
    
    otp, _ = Otp.objects.get_or_create(user=user)
    otp.otp=otp_code
    otp.created=datetime.datetime.today()
    print(otp_code)
    otp.save()
    return Response({'massage':'ok', 'code':otp_code}, status=status.HTTP_200_OK)
    # return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    print(request.data)
    try:
        user=ZubyUser.objects.get(phone=request.data['phone'])
        otp=Otp.objects.get(otp=request.data['otp'], user=user)
    except:
        return Response({'message':'otp not found'}, status=status.HTTP_400_BAD_REQUEST)
    t= datetime.datetime.today()
    expire=datetime.timedelta(minutes=3)
    created=otp.created.replace(tzinfo=None)
    print('now',t.time())
    print('exp', expire)
    print(created)
    if t - created > expire:
        return Response({'message':'otp expired'})
    else:

        user.activate=True
        user.set_password(request.data['password'])
        user.save()
        return Response({'message':'account activate'}, status=status.HTTP_200_OK)
	
    
 
@api_view(['GET','PUT','POST'])
def costumerprofile(request):
    print(request.user)
    print(request._request)
    if request.method=='GET':
        costumer=Costumer.objects.get(user=request.user)
        serializer=Costumerserializer(costumer)
        return Response(serializer.data)
    
    if request.method=='PUT':
        costumer=Costumer.objects.get(user=request.user)
        serializer=Costumerserializer(costumer,data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"data":serializer.data, 'status':"success"})
        return Response({'message':'your personal detail was not updated ', 'status': "failed"})
    
    if request.method=='POST':
        serializer=Costumerserializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)
    
 

 
@api_view(['GET','PUT','POST'])
def bankdetail(request):

    if request.method=='GET':
        bankdetail=Bankdetail.objects.get(costumer=request.user.costumer)
        serializer=Bankdetailserializer(bankdetail)
        return Response(serializer.data)
    
    if request.method=='PUT':
        bankdetail=Bankdetail.objects.get(costumer=request.user.costumer)
        serializer=Bankdetailserializer(bankdetail,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response()
    
    if request.methed=='POST':
        serializer=Bankdetailserializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET','PUT','POST'])
def costumer_guarantor(request):

    if request.method=='GET':
        guarantor=Guarantor.objects.filter(costumer=request.user.costumer)
        print(guarantor)
        serializer=Guarantorserializer(guarantor, many=True)
        print(serializer.data)
        return Response(serializer.data)
    
    if request.method=='PUT':
        guarantor=Guarantor.objects.filter(costumer=request.user.costumer)
        print(guarantor)
        for item in request.data:
            serializer=Guarantorserializer(guarantor[request.data.index(item)],data=item)
            # print(serializer)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            print(serializer.data)
            # return Response(serializer.data)
        return Response()
    
    if request.method=='POST':
        serializer=Guarantorserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET','POST'])
def loandetail(request):

    if request.method=='GET':
        guarantor=Loan.objects.get(costumer=request.user.costumer)
        serializer=LOanserializer(guarantor)
        return Response(serializer.data)
    
    
    
    if request.method=='POST':
        serializer=LOanserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)





# @api_view(['GET','POST'])
# def costumerprofile(request):
#     if request.method=='GET':
#         costumer=Costumer.objects.get(user=request.user)
#         serializer=Costumerserializer(costumer)
    
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

@api_view(['GET'])
def get_repayment_ref(request, id):
    loan = Loan.objects.get(id=id)
    ref="ZRM"+idk(17)
    # print(loan.repayment_set.all().last().amount)
    if loan.repayment_set.all().count()==0:
        repayment= Repayment.objects.create(loan=loan, ref=ref)
        print
        return Response({"message":repayment.ref}) 
    print("was here")
    if  loan.repayment_set.all().last().amount != 0:
        repayment= Repayment.objects.create(loan=loan, ref="ZRM"+idk(17))
        return Response({"message":repayment.ref}) 
    print(ref)
    ref=Repayment.objects.filter(loan=loan).last().ref
    print(ref)
    return Response({"message":ref}) 
    
@api_view(['GET'])
def verify_repayment(request, ref):
    # change ref to alpha numeric to prevent reoccurence
    try:
        repayment= Repayment.objects.get(ref=ref)
    except:
        return Response({'message':'ref exit not'})
    if repayment:
        try:
            res=verifypayment(ref)
            # print(res["amount"])
            # i dont think card eed to be save here o
            # Card.objects.get_or_create(costumer=request.user.costumer, token=res['flwRef'], ref=res['txRef'] )
            repayment.amount=res['data']['amount']
            repayment.save()
            print("i wass here")
        except :
            return Response({"message":"flutter error"}, status=status.HTTP_424_FAILED_DEPENDENCY)
    
    return Response({"message":"repayment successful"}, status=status.HTTP_202_ACCEPTED)




@api_view(['GET'])
def confirm_repayment_paid(request):
    # user = request.user
    print(222)
    print(request.user.costumer)
    costumer=request.user.costumer
    loans= Loan.objects.filter(costumer=costumer, paid=False)
    for loan in loans:
        loan.collate_repayment()
    return Response({'message':"ok"},status=status.HTTP_204_NO_CONTENT)


# Create your views here.

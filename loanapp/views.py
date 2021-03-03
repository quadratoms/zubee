from django.shortcuts import render, redirect
import requests as req
import datetime

from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import ( Otpserializer,Costumerserializer, Userserializer,
Bankdetailserializer, Guarantorserializer, LOanserializer)
from rest_framework.views import APIView
import string
from random import choice




def idk(i):
    l=[]
    for each in range(i):
        l.append(choice(string.digits))
    n=''.join(l)
    return n

@api_view(['POST'])
def login(request):
    user, newuser=MyUser.objects.get_or_create(phone=request.data['phone'],)
    if user.activate:
        data={
            'username': request.data['phone'],
            'password': request.data['password']
        }

        a=req.post('http://127.0.0.1:8000/api-token-auth/', data=data)
        print(a.json())
        return Response(a.json())
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
def apply(request, amount):
    existing=False
    try:
        if request.user.costumer.loan:
            existing=True
    except:
        pass

    if existing:
        return Response({'message':'already apply'},status=status.HTTP_403_FORBIDDEN)
    
    if request.user.costumer.level.quota < amount:
        # the user should be block, asking more than your quota is imposible from user interface
        return Response({'message':'min amount exceeded'},status=status.HTTP_403_FORBIDDEN)
    loan= Loan(costumer=request.user.costumer, amount=amount)
    loan.save()
    return Response(status=status.HTTP_201_CREATED)



@api_view(['GET'])
def due(request):
    # there is an error if we try to get for not yet accepted laon
    a=request.user.costumer.loan.get_due_payment
    print(a)
    return Response({'due': a[0], 'lapse': a[1]}, status=status.HTTP_200_OK)


@api_view(['GET'])
def userstatus(request):
    token=Token.objects.get(user=request.user)
    print(token)

    serialize= Userserializer(instance=request.user)
    
    return Response(serialize.data)





@api_view(['POST'])
def createnewuser(request):
    # this code is useless for now

    if request.method=='POST':
        serializer=Userserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def get_otp(request):

    otp_code=idk(6)
    serializer= Userserializer(instance=request.data)
    # if serializer.is_valid():
    # print(serializer.data)
    user, newuser = MyUser.objects.get_or_create(phone=serializer.data['phone'],)
    user.set_password(request.data['password'])
    user.save()
    otp, _ = Otp.objects.get_or_create(user=user)
    otp.otp=otp_code
    otp.created=datetime.datetime.today()
    print(otp_code)
    otp.save()
    return Response({'massage':'ok'}, status=status.HTTP_200_OK)
    # return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_otp(request):
    print(request.data)
    try:
        user=MyUser.objects.get(phone=request.data['phone'])
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response()
    
    if request.methed=='POST':
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
        serializer=Guarantorserializer(guarantor, many=True)
        return Response(serializer.data)
    
    if request.method=='PUT':
        guarantor=Guarantor.objects.get(costumer=request.user.costumer)
        serializer=Guarantorserializer(guarantor,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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
#         serializer=Userserializer(data=request.data)
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

# Create your views here.

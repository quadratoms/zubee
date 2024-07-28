from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
import numpy as np

from loanapp.models import Collector, Loan, ZubyUser
from loanapp.serializers import LOanserializer, Loanserializer, Commentserializer

# @csrf_exempt
@api_view(["POST"])
def login_staff(request):
    print(request.data)
    print(request.method)
    user = ZubyUser.objects.get(
        phone=request.data["phone"],
    )
    print(user)
    if user.activate:
        # data={
        #     'username': request.data['phone'],
        #     'password': request.data['password']
        # }
        user = authenticate(
            request, username=request.data["phone"], password=request.data["password"]
        )
        if user is not None:
            login(request, user)
            token = Token.objects.get(user=user)
            if user.is_staff:
                role = ""
                if user.is_collector:
                    role = "collector"
                elif user.supervisor:
                    role = "supervisor"
                else:
                    role = "admin"
                return Response({"token": token.key, "role": role})
            else:
                # a none staff is trying to login
                pass

    print(6666)
    return Response({"message": "you do not own an account or forgetten password"})


@api_view(["GET"])
def share_order(request):
    loans = Loan.objects.filter(paid=False)
    collectors = Collector.objects.filter(active=True)

    due1, due2, due3, due4 = [], [], [], []
    s1 = collectors.filter(rep="s1")
    s2 = collectors.filter(rep="s2")
    s3 = collectors.filter(rep="s3")
    s4 = collectors.filter(rep="s4")

    for loan in loans:
        due_days = loan.get_due_payment[1]
        if due_days == 1 and loan.last_share != 1:
            due1.append(loan)
        elif due_days == 8 and loan.last_share != 8:
            due2.append(loan)
        elif due_days == 15 and loan.last_share != 15:
            due3.append(loan)
        else:
            due4.append(loan)

    distribute_loans(due1, s1, 1)
    distribute_loans(due2, s2, 8)
    distribute_loans(due3, s3, 15)
    distribute_loans(due4, s4, 30)  # Assuming 30 days for s4, you can change this if needed

    return Response({"message": "share complete"})

def distribute_loans(due_list, collector_list, last_share_value):
    if collector_list.exists():
        collector_count = collector_list.count()
        for idx, loan in enumerate(due_list):
            loan.collector = collector_list[idx % collector_count]
            loan.last_share = last_share_value
            loan.save()

@api_view(["GET"])
def get_all_order(request):
    print(request.user)
    print(request.user.is_authenticated)
    orders = request.user.collector.loan_set.all()
    serializer = Loanserializer(instance=orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CollectorOrder(generics.ListAPIView):
    def get_queryset(self):

        return self.request.user.collector.loan_set.all()

    # queryset = Billing.objects.all()
    serializer_class = Loanserializer
    # pagination_class = LargeResultsSetPagination


@api_view(["POST"])
def addcomment(request):
    print(request.data)
    serializer = Commentserializer(data=request.data)
    if serializer.is_valid():
        print(serializer.validated_data)
        serializer.save()
        return Response(
            {"message": "comment was added"}, status=status.HTTP_201_CREATED
        )
    return Response({"message": "data not valid"}, status=status.HTTP_400_BAD_REQUEST)


# admin
# =========================================================


@api_view(["GET"])
def payoutloan(request, id):
    loan=Loan.objects.get(id=id)
    loan.pay()
    return Response(
            {"message": "payment process"}, status=status.HTTP_201_CREATED
        )


# Create your views here.

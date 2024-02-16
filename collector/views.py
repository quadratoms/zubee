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
            request, phone=request.data["phone"], password=request.data["password"]
        )
        if user is not None:
            login(request, user)
            print(user.auth_token)
            token = Token.objects.get(user=user)
            if user.is_staff:
                role = ""
                if user.is_collector:
                    role = "collector"
                elif user.is_supervisor:
                    role = "supervisor"
                else:
                    role = "admin"
                return Response({"token": token.key, "role": role})
            else:
                # a none staff is trying to login
                pass

    print(6666)
    return Response({"message": "you do not own an account or forgetten password"})


def list_split(listA, n):
    for x in range(0, len(listA), n):
        every_chunk = listA[x : n + x]

        if len(every_chunk) < n:
            every_chunk = every_chunk + [None for y in range(n - len(every_chunk))]
        yield every_chunk


@api_view(["GET"])
def share_order(request):
    loans = Loan.objects.filter(paid=False)  # .order_by("amount")
    print(loans)
    collectors = Collector.objects.filter(active=True)

    due1 = []
    due2 = []
    due3 = []
    due4 = []
    s1 = collectors.filter(rep="s1")
    s2 = collectors.filter(rep="s2")
    s3 = collectors.filter(rep="s3")
    s4 = collectors.filter(rep="s4")
    print(s1)
    print(due1)
    print(loans)
    # sorting loan
    for loan in loans:
        print(loan.get_due_payment)
        if loan.get_due_payment[1] == 1:
            if loan.last_share != 1:
                due1.append(loan)
        elif loan.get_due_payment[1] == 8:
            if loan.last_share != 8:
                due2.append(loan)
        elif loan.get_due_payment[1] == 15:
            if loan.last_share != 15:
                due3.append(loan)
        else:
            due4.append(loan)
    print("++++++++++++++++++++++++++++++++++++++++++")

    print(due1)
    print(due2)

    for collector in s1:
        for loan in np.array_split(due1, len(s1))[list(s1).index(collector)]:
            loan.collector = collector

            loan.save()

    for collector in s2:
        for loan in np.array_split(due2, len(collector))[s2[collector]]:
            loan.collector = collector
            loan.save()

    for collector in s3:
        for loan in np.array_split(due3, len(collector))[s3[collector]]:
            loan.collector = collector
            loan.save()
    # for collector in s4:
    #     for loan in np.array_split(due4,len(collector))[s4[collector]]:
    #         loan.collector=collector
    #         loan.save()

    return Response({"message": "share complete"})


@api_view(["GET"])
def get_all_order(request):
    print(request.user)
    print(request.user.is_authenticated)
    orders = request.user.collector.loan_set.all()
    serializer = Loanserializer(instance=orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework import permissions


class AdminReadOnlyPermission(permissions.BasePermission):
    # edit_methods = ("PUT", "PATCH")

    def has_permission(self, request, view):
        print(request.user, "ts")

        if request.user.is_authenticated:
            return True
        # if request.user.is_admin:
        #     return True

    # def has_object_permission(self, request, view, obj):
    #     print(request.user, "ts")
    #     if request.user.is_superuser:
    #         return True

    #     if request.method in permissions.SAFE_METHODS:
    #         return True

    #     # if obj.author == request.user:
    #     #     return True

    #     # if request.user.is_staff and request.method not in self.edit_methods:
    #     #     return True

    #     return False


class CollectorOrder(generics.ListAPIView):
    def get_queryset(self):
        return self.request.user.collector.loan_set.all()

    # queryset = Billing.objects.all()
    serializer_class = Loanserializer
    # pagination_class = LargeResultsSetPagination


# for admin
class AllOrder(generics.ListAPIView):
    permission_classes = [AdminReadOnlyPermission]

    def get_queryset(self):
        print(self.request.user.is_authenticated)
        if not self.request.user.is_admin:
            return []
        return Loan.objects.all().order_by("-id")

    serializer_class = Loanserializer


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
    if not request.user.is_admin:
        return Response(
            {"message": "payment process"}, status=status.HTTP_401_UNAUTHORIZED
        )
    loan = Loan.objects.get(id=id)
    loan.pay()
    return Response({"message": "payment process"}, status=status.HTTP_201_CREATED)


# Create your views here.

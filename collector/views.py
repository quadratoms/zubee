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
from loanapp.serializers import Collectorserializer, LOanserializer, Loanserializer, Commentserializer


# @csrf_exempt
@api_view(["POST"])
def login_staff(request):
    try:
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not phone or not password:
            return Response({"message": "Phone and password are required."}, status=400)

        user = ZubyUser.objects.get(phone=phone)
        if not user:
            user=Collector(username=phone).user

        if not user.activate:
            return Response({"message": "User is not activated."}, status=403)

        authenticated_user = authenticate(request, phone=phone, password=password)

        if authenticated_user is not None:
            login(request, authenticated_user)
            token = Token.objects.get(user=authenticated_user)

            if authenticated_user.is_staff:
                role = "collector" if authenticated_user.is_collector else ("supervisor" if authenticated_user.is_supervisor else "admin")
                return Response({"token": token.key, "role": role})
            else:
                # Non-staff user attempting to login
                return Response({"message": "You are not authorized to access this endpoint."}, status=403)
        else:
            return Response({"message": "Invalid phone number or password."}, status=401)
    except ZubyUser.DoesNotExist:
        return Response({"message": "User with provided phone number does not exist."}, status=404)
    
def list_split(listA, n):
    for x in range(0, len(listA), n):
        every_chunk = listA[x : n + x]

        if len(every_chunk) < n:
            every_chunk = every_chunk + [None for y in range(n - len(every_chunk))]
        yield every_chunk


from django.db.models import Count

@api_view(["GET"])
def share_order(request):
    # Retrieve all unpaid loans
    loans = Loan.objects.filter(paid=False)

    # Retrieve active collectors and count how many loans each has
    collectors = Collector.objects.filter(active=True).annotate(num_loans=Count('loan'))

    # Initialize dictionaries to hold loans for each due date category
    due_loans = {1: [], 8: [], 15: [], 'other': []}

    # Distribute loans into due date categories
    for loan in loans:
        due_payment_days = loan.get_due_payment[1]
        if due_payment_days == 1:
            due_loans[1].append(loan)
        elif due_payment_days == 8:
            due_loans[8].append(loan)
        elif due_payment_days == 15:
            due_loans[15].append(loan)
        else:
            due_loans['other'].append(loan)

    # Assign loans to collectors based on due date categories
    for collector in collectors:
        num_loans = collector.num_loans
        collector_loans = []

        # Determine which due date category to assign loans from based on collector's rep
        if collector.rep == 's1':
            collector_loans = due_loans[1]
        elif collector.rep == 's2':
            collector_loans = due_loans[8]
        elif collector.rep == 's3':
            collector_loans = due_loans[15]
        # Add more conditions if needed for other reps
        else:
            collector_loans = due_loans["other"]

        # If there are loans for this collector, assign them
        if collector_loans:
            # Ensure we don't exceed the number of loans this collector can handle
            if num_loans < len(collector_loans):
                collector_loans = collector_loans[:num_loans]
            for loan in collector_loans:
                loan.collector = collector
                loan.save()

    return Response({"message": "Loan assignment complete"})


@api_view(["POST"])
def assign_collector_to_loan(request):
    # Retrieve loan and collector IDs from the request data
    loan_id = request.data.get('loan_id')
    collector_id = request.data.get('collector_id')

    try:
        # Retrieve the loan and collector objects
        loan = Loan.objects.get(id=loan_id)
        collector = Collector.objects.get(id=collector_id)

        # Assign the collector to the loan
        loan.collector = collector
        loan.save()

        return Response({"message": "Collector assigned to loan successfully."})
    except Loan.DoesNotExist:
        return Response({"message": "Loan not found."}, status=404)
    except Collector.DoesNotExist:
        return Response({"message": "Collector not found."}, status=404)
    except Exception as e:
        return Response({"message": "An error occurred while assigning collector to loan.", "error": str(e)}, status=500)


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

        # if request.user.is_authenticated:
        #     return True
        if request.user.is_admin:
            return True

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



from rest_framework import filters
from rest_framework import viewsets


class CollectorViewSet(viewsets.ModelViewSet):
    permission_classes = [AdminReadOnlyPermission]

    queryset = Collector.objects.all()
    serializer_class = Collectorserializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields=["username", "user__phone", "user__email"]
    


@api_view(["GET", "POST"])
def payoutloan(request, id, manual=0):
    if not request.user.is_admin:
        return Response(
            {"message": "payment process"}, status=status.HTTP_401_UNAUTHORIZED
        )
    loan = Loan.objects.get(id=id)
    if manual==1:
        loan.pay()
    else:
        if request.method == "POST":
            loan.pay_manually(**request.data)
            
        
    
    return Response({"message": "payment process"}, status=status.HTTP_201_CREATED)


# Create your views here.

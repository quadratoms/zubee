from django.urls import path
from .views import (confirm_repayment_paid, get_repayment_ref, login, userstatus, bankdetail, costumerprofile,verify_otp,
createnewuser, costumer_guarantor, loandetail, due, apply, pay, get_otp, verify_repayment)
from rest_framework.authtoken.views import obtain_auth_token



urlpatterns = [
    path('login/', login, name='login'),
    path('getotp/', get_otp, name='get_otp'),
    path('verifyotp/', verify_otp, name='verify_otp'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('status/', userstatus),
    path('create/', createnewuser),
    path('profile/', costumerprofile),
    path('bank/', bankdetail),
    path('guarantor/', costumer_guarantor),
    path('loan/', loandetail),
    path('apply/<int:amount>/<int:dur>', apply),
    path('due/', due),
    path('pay/', pay),
    path('getrepaymentref/<int:id>', get_repayment_ref),
    path('verifyrepayment/<str:ref>', verify_repayment),
    path('comfirmpayment/', confirm_repayment_paid),
]

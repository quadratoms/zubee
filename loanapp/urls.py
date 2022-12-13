from django.urls import path
from .views import (ImageViewSet, confirm_repayment_paid, get_repayment_ref, login, payment_data, userstatus, bankdetail, customerprofile, verify_bvn,verify_otp,
createnewuser, customer_guarantor, loandetail, due, apply, pay, get_otp, verify_repayment, add_contact)
from rest_framework.authtoken.views import obtain_auth_token



urlpatterns = [
    path('login/', login, name='login'),
    path('getotp/', get_otp, name='get_otp'),
    path('verifyotp/', verify_otp, name='verify_otp'),
    path('verifybvn/', verify_bvn, name='verify_bvn'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('status/', userstatus),
    path('create/', createnewuser),
    path('profile/', customerprofile),
    path('bank/', bankdetail),
    path('guarantor/', customer_guarantor),
    path('loan/', loandetail),
    path('apply/<int:amount>/<int:dur>', apply),
    path('due/', due),
    path('pay/', pay),
    path('getrepaymentref/<int:id>', get_repayment_ref),
    path('verifyrepayment/<str:ref>', verify_repayment),
    path('comfirmpayment/', confirm_repayment_paid),
    path('addcontact/', add_contact),
    path('imageupload/', ImageViewSet.as_view()),
    path('paymentdata/', payment_data),
]

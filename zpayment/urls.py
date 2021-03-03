from django.urls import path
from .views import *



urlpatterns = [
    path('verifybvn/', bvnverify(), name='login'),
    path('verifycard/', cardverify(), name='login'),
    path('verifiyaccount/', accountverify(), name='verifiyaccount'),
    path('verifyphone/', phoneverify(), name='verifyphone'),
    
]

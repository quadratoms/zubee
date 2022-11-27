from django.urls import path
from .views import *



urlpatterns = [
    path('login/', login_staff, name='stafflogin'),
    path('share/', share_order, name='share'),
    path('orders/', get_all_order, name='orders'),
    path('orderss/', CollectorOrder.as_view(), name='orderss'),
    path('addcomment/', addcomment, name='addcomment'),
    
]

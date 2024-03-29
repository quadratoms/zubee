from django.urls import path, include
from .views import *

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'collectors', CollectorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_staff, name='stafflogin'),
    path('share/', share_order, name='share'),
    path('orders/', get_all_order, name='orders'),
    path('orderss/', CollectorOrder.as_view(), name='orderss'),
    path('allorders/', AllOrder.as_view(), name='allorders'),
    path('addcomment/', addcomment, name='addcomment'),
    path('payout/<int:id>/', payoutloan, name='payout'),
    path('assign-collector/', assign_collector_to_loan, name='assign_collector_to_loan'),

    
]

from django.urls import path
from .views import OrderViewSet, OrderCountView, CompletedOrderCountView
urlpatterns = [
    path('orders/', OrderViewSet.as_view(actions={
         'get': 'list', 'post': 'create'}), name='orders'),
    path('orders/<int:pk>/', OrderViewSet.as_view(
        actions={'patch': 'partial_update', 'delete': 'destroy'}), name='orders-detail'),
    path('order-count/<int:pk>/',
         OrderCountView.as_view(), name='ord-proc_cnt'),
    path('completed-order-count/<int:pk>',
         CompletedOrderCountView.as_view(), name='ord-cpl_cnt')
]

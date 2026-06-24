"""URL mapping for the orders_app."""

from django.urls import path
from orders_app.api.views import (CompletedOrderCountView,
                                  OrderCountView,
                                  OrderViewSet)

urlpatterns = [
    path(
        'orders/',
        OrderViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }),
        name='orders'
    ),
    path(
        'orders/<int:pk>/',
        OrderViewSet.as_view({
            'patch': 'partial_update',
            'delete': 'destroy'
        }),
        name='orders-detail'
    ),
    path(
        'order-count/<int:pk>/',
        OrderCountView.as_view(),
        name='ord-proc_cnt'
    ),
    path(
        'completed-order-count/<int:pk>/',
        CompletedOrderCountView.as_view(),
        name='ord-cpl_cnt'
    )
]

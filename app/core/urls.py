from django.urls import path
from orders.views import HealthCheckView, OrderDetailView, OrderListCreateView

urlpatterns = [
        path("healthz/", HealthCheckView.as_view(), name="healthz"),
        path("api/orders/", OrderListCreateView.as_view(), name="order-list-create"),
        path("api/orders/<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
        ]


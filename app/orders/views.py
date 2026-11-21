from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderItem
from .mongo import webhook_logs
from .services import create_order


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["sku", "quantity", "unit_price_cents"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer_email", "status", "created_at", "items"]
        read_only_fields = ["id", "status", "created_at"]


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class OrderListCreateView(APIView):
    def get(self, request):
        # Query tuning: prefetch_related eliminates N+1 queries
        orders = Order.objects.prefetch_related("items").all()[:20]
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(
            customer_email=serializer.validated_data["customer_email"],
            items_data=serializer.validated_data["items"],
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
        # Join relational state (Postgres) with unstructured audit log (MongoDB)
        audit = webhook_logs.find_one({"order_id": str(order.id)}, {"_id": 0})
        data = OrderSerializer(order).data
        data["webhook_audit"] = audit
        return Response(data)

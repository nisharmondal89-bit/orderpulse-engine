from django.db import transaction
from .models import Order, OrderItem
from .tasks import dispatch_order_webhook


def create_order(customer_email: str, items_data: list[dict]):
    with transaction.atomic():
        order=Order.objects.create(customer_email=customer_email)
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                sku=item["sku"],
                quantity=item["quantity"],
                unit_price_cents=item["unit_price_cents"],
                )
            for item in items_data
            ])

        transaction.on_commit(lambda: dispatch_order_webhook,delay(str(order.id)))
    return order

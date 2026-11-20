from django.db import transaction
from .models import Order
from .tasks import dispatch_order_webhook

def create_order(customer_email: str, amount_cents: int)->Order:

    with transaction.atomic():
        order = Order.objects.create(
                customer_email=customer_email,
                amount_cents=amount_cents,
                status="PENDING"
                )

        transaction.on_commit(lambda: dispatch_order_webhook.delay(str(order.id)))
    return order



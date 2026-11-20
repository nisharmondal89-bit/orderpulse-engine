import time
import requests
from celery import shared_task
from .models import Order
from .mongo import webhook_logs


@shared_task(
        bind=True,
        autoretry_for=(requests.RequestException,),
        retry_backoff=True,
        max_retries=3,
        )

def dispatch_order_webhook(self, order_id: str):
    order=Order.objects.prefetch_related("items").get(id=order_id)
    total_cents=sum(i.quantity * i.unit_price_cents for i in order.items.all())

    start=time.perf_counter()
    rep=requests.post(
            "https://httpbin.org",
            json={"order_id": order_id, "email": order.customer_email, "total_cents": total_cents},
            )

    resp.raise_for_status()
    latency_ms=round((time.perf_counter() -start) * 1000, 2)


    webhook_logs.insert_one({
        "order_id": order_id, 
        "status_code" : resp.status_code,
        "latency_ms": latency_ms,
        "raw_payload": resp.json(),
        })
    order.status=Order.Status.CONFIRMED
    order.save(update_fields=["status"])




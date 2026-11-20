import time
import requests
from celery import shared_task
from .models import order
from .mongo import audit_collection

@shared_task(bind=True, autoretry_for=(requests.RequestException,), retry_backoff=True, max_retries=3)
def dispatch_order_webhook(self, order_id: str):
    order=Order.objects.get(id=order_id)
    start=time.perf_counter()

    resp=requests.post("https://httpbin.org", json={"order_id": order_id, "amount": order.amount_cents},timeout=5)
    resp.raise_for_status()

    audit_collection.insert_one({
        "order_id": order_id,
        "status_code": resp.status_code,
        "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        "raw_response": resp.json()
        })

    order.status="CONFIRMED"
    order.save(update_fields=["status"])



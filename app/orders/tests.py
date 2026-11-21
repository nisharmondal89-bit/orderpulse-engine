from unittest.mock import patch
import pytest
from rest_framework.test import APIClient
from .models import Order
from .mongo import webhook_logs
from .services import create_order

@pytest.mark.django_db(transaction=True)
def test_end_to_end_order_flow(settings):
    settings.CELERY_TASK_ALWAYS_EAGER= True
    webhook_logs.delete_many({})


    with patch("orders.tasks.requests.post") as mock_post:
        mock_post.return_value.status_code=200
        mock_post.return_value.json.return_value={"partner_tx_id": "tx_999"}


        client = APIClient()
        res= client.post(
                "/api/orders/",
                {
                    "customer_email": "buyer@example.com",
                    "items": [{"sku": "CHAIR-01", "quantity": 2, "unit_price_cents": 15000}],
                    },
                format="json",
                )

        assert res.status_code==201
        order_id=res.data["id"]

        detail=client.get(f"/api/orders/{order_id}/").data
        assert detail["status"]==Order.Status.CONFIRMED
        assert detail["webhook_audit"]["raw_payload"] == {"partner_tx_id": "tx_999"}

@pytest.mark.django_db
def test_list_orders_prevents_n_plus_one(django_assert_num_queries):
        with patch("orders.services.dispatch_order_webhook.delay"):
                for i in range(5):
                    create_order(f"user{i}@example.com", [{"sku": "TABLE-01", "quantity": 1, "unit_price_cents": 25000}])
        client= APIClient()

        with django_assert_num_queries(2):
            res = client.get("/api/orders/")
        assert res.status_code==200
        assert len(res.data)==5

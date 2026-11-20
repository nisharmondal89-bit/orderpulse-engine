import uuid
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING= "PENDING", "Pending"
        CONFIRMED= "CONFIRMED", "Confirmed"
        FAILED="FAILED", "Failed"

    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_email=models.EmailField(db_index=True)
    status=models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at= models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering= ["-created_at"]

class OrderItem(models.Model):
    order=models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    sku=models.CharField(max_length=64)
    quantity=models.PositiveIntegarField()
    unit_price_cents=models.PositiveIntegerField()



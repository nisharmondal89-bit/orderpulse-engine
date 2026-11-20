from django.conf import settings
from pymongo import MongoClient


_client= MongoClient(settings.MONGO_URI)
_db=_client["orderpulse_audit"]
webhook_logs=_db["webhook_logs"]
webhook_logs.create_index("order_id")


import uuid
from django.db import models

# Create your models here.
class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    product_title = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.UUIDField(default=uuid.uuid4, editable=False, db_column='product_id')
    user = models.UUIDField(default=uuid.uuid4, editable=False, db_column='user_id')
    order = models.UUIDField(null=True, db_column='order_id')
    variant = models.UUIDField(default=uuid.uuid4, editable=False, db_column='variant_id')


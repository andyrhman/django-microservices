import uuid
from django.db import models

# Create your models here.
class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    transaction_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    user = models.UUIDField(default=uuid.uuid4, editable=False, db_column='user_id')
    
    @property
    def total(self):
        return sum(item.quantity * item.price for item in self.order_items_order.all())

    @property
    def total_orders(self):
        return self.order_items_order.count()

class OrderItemStatus(models.TextChoices):
    SEDANG_DIKEMAS = 'Sedang Dikemas', 'Sedang Dikemas'
    DIKIRIM = 'Dikirim', 'Dikirim'
    SELESAI = 'Selesai', 'Selesai'

class OrderItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    product_title = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.SEDANG_DIKEMAS)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, related_name='order_items_order')
    product = models.UUIDField(default=uuid.uuid4, editable=False, db_column='product_id')
    variant = models.UUIDField(default=uuid.uuid4, editable=False, db_column='variant_id')
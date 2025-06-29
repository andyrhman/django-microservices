import uuid
from django.db import models

# Create your models here.
class Review(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    star = models.IntegerField()
    comment = models.TextField(max_length=1000, null=True)
    image = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.UUIDField(null=True, db_column='user_id')
    product = models.UUIDField(null=True, db_column='product_id')
    order = models.UUIDField(null=True, db_column='order_id') 
    variants = models.UUIDField(null=True, db_column='variant_id')
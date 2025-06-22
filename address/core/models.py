import uuid
from django.db import models

# Create your models here.
class Address(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    zip = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    user = models.UUIDField(default=uuid.uuid4, editable=False, db_column='user_id')
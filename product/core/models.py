import uuid
from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)   
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    image = models.CharField(max_length=255)
    price = models.FloatField()
    category = models.UUIDField(default=uuid.uuid4, editable=False, db_column='category_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class ProductVariation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE, related_name='products_variation')

class ProductImages(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE, related_name='products_images')
    
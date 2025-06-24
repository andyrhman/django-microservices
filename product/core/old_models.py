from django.db import models

class OldCategory(models.Model):
    id   = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'core_category'
        app_label = 'core'

class OldProduct(models.Model):
    id          = models.UUIDField(primary_key=True)
    title       = models.CharField(max_length=255)
    slug        = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    image       = models.CharField(max_length=255)
    price       = models.FloatField()
    category_id = models.UUIDField(db_column='category_id')

    class Meta:
        managed = False
        db_table = 'core_product'
        app_label = 'core'

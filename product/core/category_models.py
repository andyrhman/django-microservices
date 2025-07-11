from django.db import models
import uuid

class Category(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        managed   = False
        db_table  = 'core_category'  # e.g. 'categories_category'
        app_label = 'category'

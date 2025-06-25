from rest_framework import serializers

from core.services import ProductService
from core.models import Category
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
import requests
from rest_framework import serializers
from django.utils.text import slugify
import re

from core.models import Product, ProductImages, ProductVariation
from core.services import CategoryService

class ProductAdminSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model  = Product
        fields = ['id','title','slug','description','image','price','category','average_rating']

    def get_category(self, obj):
        cats_map = self.context.get('categories_map', {})
        return cats_map.get(str(obj.category))
        
class ProductCreateSerializer(serializers.ModelSerializer):
    # still accept UUID on write
    category = serializers.UUIDField(write_only=True)
    images   = serializers.ListField(child=serializers.CharField(), write_only=True)
    variants = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model  = Product
        fields = ['title', 'description', 'image', 'price',
                  'category', 'images', 'variants']

    def validate(self, data):
        cat_id  = data['category']
        request = self.context['request']
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else None

        try:
            cat = CategoryService.get_category_admin(cat_id, cookies=cookies)
        except requests.HTTPError:
            raise serializers.ValidationError({'category': 'Invalid category ID'})
        # store the validated dict on the serializer for `create`/`update`
        self._validated_category = cat
        return data

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        variants = validated_data.pop('variants', [])

        title     = validated_data.get('title')
        base_slug = slugify(title)
        slug      = base_slug
        existing  = Product.objects.filter(slug__startswith=base_slug) \
                                   .values_list('slug', flat=True)
        if slug in existing:
            nums = [
                int(m.group(1))
                for s in existing
                if (m := re.match(rf'^{re.escape(base_slug)}-(\d+)$', s))
            ]
            slug = f"{base_slug}-{(max(nums) if nums else 1) + 1}"

        # 4) now create exactly one category kwarg
        product = Product.objects.create(
            slug     = slug,
            category=validated_data.pop('category'),
            **validated_data
        )

        # 5) images & variants
        for img in images:
            ProductImages.objects.create(product=product, name=img)
        for var in variants:
            ProductVariation.objects.create(product=product, name=var)

        return product

    def update(self, instance, validated_data):
        if 'category' in validated_data:
            new_cat_id = validated_data.pop('category')
            request    = self.context['request']
            token      = request.COOKIES.get('user_session')
            cookies    = {'user_session': token} if token else None

            try:
                cat = CategoryService.get_category_admin(new_cat_id, cookies=cookies)
            except requests.HTTPError:
                raise serializers.ValidationError({'category': 'Invalid or unauthorized category'})
            instance.category = cat['id']

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance

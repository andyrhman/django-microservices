import requests
from rest_framework import serializers
from django.utils.text import slugify
import re

from core.models import Product, ProductImages, ProductVariation
from core.services import CategoryService

class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = "__all__"
        
class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = "__all__"
        
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    products_images = ProductImagesSerializer(many=True, read_only=True)
    products_variation = ProductVariationSerializer(many=True, read_only=True)
    # review_products     = ReviewSerializer(many=True, read_only=True)
    # averageRating       = serializers.SerializerMethodField()
    # reviewCount         = serializers.SerializerMethodField()
    class Meta:
        model  = Product
        fields = [
            'id','title','slug','description','image','price',
            'category','products_images','products_variation',
            'created_at', 'updated_at'
        ]
    # class Meta:
    #     model  = Product
    #     fields = [
    #         'id','title','slug','description','image','price',
    #         'category','products_images','products_variation',
    #         'created_at', 'updated_at',
    #         'review_products','averageRating','reviewCount',
    #     ]

    def get_category(self, obj):
        cats_map = self.context.get('categories_map', {})
        return cats_map.get(str(obj.category))
    # def get_averageRating(self, obj):
    #     qs = obj.review_products.all()
    #     if not qs.exists():
    #         return 0
    #     return round(sum(r.star for r in qs) / qs.count(), 2)

    # def get_reviewCount(self, obj):
    #     return obj.review_products.count()
        
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

class ProductVariationCreateSerializer(serializers.ModelSerializer):
    name = serializers.ListField(
        child=serializers.CharField()
    )
    
    product = serializers.UUIDField()

    class Meta:
        model = ProductVariation
        fields = "__all__"
        
    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exists")
        return value
        
    def create(self, validated_data):
        name = validated_data.pop('name', [])
        product_id = validated_data.pop('product', [])
        product = Product.objects.get(id=product_id)
        
        variants = []
        for n in name:
            variant = ProductVariation.objects.create(
                name=n,
                product=product
            )
            
            variants.append(variant)
            
        return variants
            
class ProductImagesCreateSerializer(serializers.ModelSerializer):
    name = serializers.ListField(
        child=serializers.CharField()
    )
    
    product = serializers.UUIDField()
    class Meta:
        model = ProductImages
        fields = "__all__"
    
    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exists")
        return value
     
    def create(self, validated_data):
        name = validated_data.pop('name', [])
        
        product_id = validated_data.pop('product', [])
        product = Product.objects.get(id=product_id)
        
        images = []
        for n in name:
            image = ProductImages.objects.create(
                name=n,
                product=product
            )
            images.append(image)

        return images
import requests
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.services import UserService
from core.services import ProductService
from core.models import Cart

class BulkUserListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        ids = list({ str(addr.user) for addr in data })

        request = self.child.context.get('request')
        scope   = "admin" if request.path.startswith("/api/admin/") else "user"
        token   = request.COOKIES.get('user_session')

        resp = UserService.post(
            f"{scope}/users/bulk",
            json={"ids": ids},
            cookies={"user_session": token},
            timeout=5
        )
        users_map = resp.ok and resp.json() or {}

        for child in self.child.__class__._declared_fields.values():
            pass

        self.child.context['users_map'] = users_map

        return super().to_representation(data)
        
class CartSerializer(serializers.ModelSerializer):
    product            = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField(method_name='get_variant')

    class Meta:
        model  = Cart
        fields = "__all__"

    def get_product(self, obj):
        pm = self.context.get('product_map', {})
        prod = pm.get(str(obj.product))
        if not prod:
            try:
                prod = ProductService.get_product_by_id(obj.product)
            except Exception:
                return None
        return {
            'id':          prod['id'],
            'title':       prod['title'],
            'description': prod.get('description'),
            'slug':        prod.get('slug'),
            'image':       prod.get('image'),
            'price':       prod.get('price'),
        }

    def get_variant(self, obj):
        # same pattern for variants
        pm = self.context.get('product_map', {})
        prod = pm.get(str(obj.product))
        if not prod:
            try:
                prod = ProductService.get_product_by_id(obj.product)
            except Exception:
                return None
        var_id = str(obj.variant)
        return next(
            (v for v in prod.get('products_variation', []) if v['id'] == var_id),
            None
        )
        
class CartAdminSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = "__all__"
        list_serializer_class = BulkUserListSerializer

    def get_user(self, address):
        request   = self.context['request']
        token     = request.COOKIES.get('user_session')
        scope     = "admin" if request.path.startswith("/api/admin/") else "user"
        user_id   = str(address.user)

        users_map = self.context.get("users_map")
        if users_map is not None:
            return users_map.get(user_id)

        resp = UserService.get(
            f"{scope}",
            cookies={"user_session": token},
            timeout=5
        )
        if not resp.ok:
            return None
        return resp.json()
        
class CartCreateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(write_only=True)
    variant = serializers.UUIDField(write_only=True)
    quantity   = serializers.IntegerField()

    class Meta:
        model  = Cart
        fields = ['product', 'variant', 'quantity']

    def validate(self, data):
        try:
            prod = ProductService.get_product_by_id(data['product'])
        except requests.HTTPError:
            raise ValidationError({"product": "Product not found."})

        variants = prod.get('products_variation', [])
        match = next((v for v in variants if v['id'] == str(data['variant'])), None)
        if not match:
            raise ValidationError({"variant": "Variant not found for this product."})

        data['product_data'] = prod
        data['variant_data'] = match
        return data

    def create(self, validated_data):
        user = self.context['request'].user_ms
        prod = validated_data.pop('product_data')
        var  = validated_data.pop('variant_data')
        qty  = validated_data.pop('quantity')

        defaults = {
            "quantity":      qty,
            "price":         prod['price'],
            "product_title": prod['title'],
        }
        # ! [BUG] cart is still incrementing quantity even if completed is true
        # ! it should not increment the quantity if the cart is already completed
        cart_item, created = Cart.objects.get_or_create(
            product = prod['id'],
            variant = var['id'],
            user    = user,
            defaults=defaults
        )
        if not created:
            cart_item.quantity += qty
            cart_item.save()
        return cart_item

class CartQuantityUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = ['quantity']
        
    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        
        return instance

class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cart
        fields = ['completed', 'order']

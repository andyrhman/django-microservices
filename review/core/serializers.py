import cloudinary.uploader
from rest_framework import exceptions, serializers
from decouple import config
from core.models import Review
from core.services import OrderService, ProductService, UserService

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

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = "__all__"
        list_serializer_class = BulkUserListSerializer
        
    def get_user(self, data):
        request   = self.context['request']
        token     = request.COOKIES.get('user_session')
        scope     = "admin" if request.path.startswith("/api/admin/") else "user"
        user_id   = str(data.user)

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

cloudinary.config(
    cloud_name = config('CLOUDINARY_CLOUD_NAME'),
    api_key    = config('CLOUDINARY_API_KEY'),
    api_secret = config('CLOUDINARY_API_SECRET')
)

class CreateReviewSerializer(serializers.ModelSerializer):
    order_id    = serializers.UUIDField(write_only=True)
    product_id  = serializers.UUIDField(write_only=True)
    variant_id  = serializers.UUIDField(write_only=True)
    image       = serializers.FileField(write_only=True, required=False)

    class Meta:
        model  = Review
        fields = ['star', 'comment', 'image', 'product_id', 'variant_id', 'order_id']

    def validate(self, data):
        request = self.context['request']
        user_id = request.user_ms
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else {}
        
        image_file = request.FILES.get('image')
        if image_file:
            try:
                result = cloudinary.uploader.upload(
                    image_file,
                    folder='djangoshop/reviews'
                )
                data['image'] = result['secure_url']
            except Exception as e:
                raise serializers.ValidationError({'image': f'Upload failed: {e}'})

        orders = OrderService.get_user_orders(cookies=cookies)
        oid    = str(data['order_id'])
        order  = next((o for o in orders if o['id'] == oid), None)
        if order is None:
            raise exceptions.NotFound('Order not found')
        
        product = ProductService.get_product_by_id(str(data['product_id']))

        vid = str(data['variant_id'])
        variant = next(
            (v for v in product.get('products_variation', []) if v['id'] == vid),
            None
        )
        if variant is None:
            raise exceptions.NotFound("Product variant not found in that product")

        if order.get('user') != user_id or not order.get('completed', True):
            raise exceptions.PermissionDenied("You're not allowed to review that order.")

        if not (1 <= data['star'] <= 5):
            raise serializers.ValidationError("Star must be between 1 and 5.")

        if Review.objects.filter(
            user=user_id,
            order=order['id'],
            product=product['id'],
            variants=variant['id']
        ).exists():
            raise serializers.ValidationError("Already reviewed.")

        data['order_id']    = order['id']
        data['product_id']  = product['id']
        data['variant_id'] = variant['id']
        return data

    def create(self, validated_data):
        user_id = self.context['request'].user_ms
        return Review.objects.create(
            user       = user_id,
            order      = validated_data.pop('order_id'),
            variants   = validated_data.pop('variant_id'),
            product    = validated_data.pop('product_id'),
            **validated_data
        )

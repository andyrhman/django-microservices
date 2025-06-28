from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from core.models import Order, OrderItem, OrderItemStatus
from core.services import CartService, ProductService
from core.signals import order_completed

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ['id','product_title','price','quantity','status','product','variant']

    def get_product(self, obj):
        pid  = str(obj.product)
        prod = ProductService.get_product_by_id(pid)
        return {
            'id':    prod['id'],
            'title': prod['title'],
            'image': prod['image'],
            'price': prod['price']
        }

    def get_variant(self, obj):
        pid  = str(obj.product)
        prod = ProductService.get_product_by_id(pid)
        vid  = str(obj.variant)
        return next(
            (v for v in prod.get('products_variation', []) if v['id'] == vid),
            None
        )

class OrderSerializer(serializers.ModelSerializer):
    order_items_order = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = "__all__"

class ConfirmOrderSerializer(serializers.ModelSerializer):
    source = serializers.CharField(write_only=True)
    class Meta:
        model = Order
        fields = ['source']
        
    def validate(self, data):
        request = self.context['request']
        user_id = request.user_ms
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else {}

        try:
            order = Order.objects.get(transaction_id=data['source'])
        except Order.DoesNotExist:
            raise NotFound("Order not found")
        if order.completed:
            raise ValidationError("Your order already completed")
        
        resp = CartService.get('carts/bulk/completed', cookies=cookies)
        resp.raise_for_status()
        carts = resp.json().get('data', [])

        user_carts = [c for c in carts
                      if c.get('order') == str(order.id)
                      and c.get('user')  == user_id]
        if not user_carts:
            raise PermissionDenied("You are not allowed to do that")

        data['order'] = order
        data['carts'] = user_carts
        return data

    def create(self, validated_data):
        request = self.context['request']
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else {}

        order = validated_data['order']
        carts  = validated_data['carts']

        for c in carts:
            resp = CartService.put(
                f"carts/{c['id']}/complete",
                cookies=cookies,
                json={'completed': True}
            )
            resp.raise_for_status()

        items = order.order_items_order.all()
        for item in items:
            item.status = OrderItemStatus.SEDANG_DIKEMAS
            item.save()

        order.completed = True
        order.save()

        order_completed.send(sender=self.__class__, order=order)
        return order
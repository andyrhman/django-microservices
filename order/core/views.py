from rest_framework import generics, status
from rest_framework.status import HTTP_201_CREATED
import stripe
from decouple import config
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import JWTAuthentication
from core.models import Order, OrderItem, OrderItemStatus
from core.services import AddressService, CartService, UserService
from core.serializers import ChangeOrderStatusSerializer, ConfirmOrderSerializer, OrderItemSerializer, OrderSerializer

# Create your views here.
class OrderListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        
        queryset = super().get_queryset().prefetch_related('order_items_order')
        
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(order_items_order__product_title__icontains=search) | 
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
            
        return queryset
    
    def get(self, _):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class CreateOrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user_ms
        token = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else {}

        user_resp = UserService.get('user', cookies=cookies)
        user_resp.raise_for_status()
        user_data = user_resp.json()
        
        resp = AddressService.get('address', cookies=cookies)
        if resp.status_code == 404:
            return Response(
                {"message": "Please create your shipping address first"},
                status=status.HTTP_400_BAD_REQUEST
            )
        resp.raise_for_status()

        cart_ids = [c['cart_id'] for c in request.data.get('carts', [])]
        
        resp = CartService.get(
            'carts/bulk',
            cookies=cookies
        )
        resp.raise_for_status()
        carts = resp.json().get('data', [])
        
        if len(carts) != len(cart_ids):
            raise NotFound("One or more carts were not found.")
        if any(c.get('completed') for c in carts):
            raise ValidationError("One or more carts have already been checked out.")
        
        order = Order.objects.create(
            name  = user_data['fullName'],
            email = user_data['email'],
            user  = user,
        )

        line_items = []
        for c in carts:
            prod_id = c['product']['id']
            var_id  = c['variant']['id']

            OrderItem.objects.create(
                order         = order,
                product_title = c['product_title'],
                price         = c['price'],
                quantity      = c['quantity'],
                product       = prod_id,
                variant       = var_id,
                status        = OrderItemStatus.SEDANG_DIKEMAS,
            )
            
            resp = CartService.put(
                f"carts/{c['id']}/complete",
                cookies=cookies,
                json={
                    "completed": True,
                    "order": str(order.id)
                }
            )
            
            resp.raise_for_status()
            line_items.append({
                'price_data': {
                    'currency': 'idr',
                    'unit_amount': int(c['price']),
                    'product_data': {
                        'name': f"{c['product_title']} - Variant {c['variant']['name']}",
                        'description': c['product']['description'],
                        'images': [c['product']['image']],
                    },
                },
                'quantity': c['quantity']
            })

        stripe.api_key = config('STRIPE_SECRET_KEY')
        ORIGIN = config('ORIGIN')
        session = stripe.checkout.Session.create(
            success_url=f"{ORIGIN}/success?source={{CHECKOUT_SESSION_ID}}",
            cancel_url =f"{ORIGIN}/error",
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment'
        )

        order.transaction_id = session['id']
        order.save()

        return Response(session, status=HTTP_201_CREATED)
    
class ConfirmOrderGenericAPIView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = ConfirmOrderSerializer

    def post(self, request, *args, **kwargs):
        ser   = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = ser.save()

        out   = OrderSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)
    
class GetUserOrder(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user_ms)
    
class GetOrderItem(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = 'id'
   
class ChangeOrderStatus(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = ChangeOrderStatusSerializer
    lookup_field = 'id'
    
    def put(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response
    
class TotalOrdersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, _):
        order = Order.objects.all()
        
        total = len(order)
        
        return Response({"total": total})   

class TotalOrderItemsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, _):
        order = OrderItem.objects.all()
        
        total = len(order)
        
        return Response({"total": total})   
from django.shortcuts import render
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Cart
from core.serializers import CartAdminSerializer, CartCreateSerializer, CartQuantityUpdateSerializer, CartSerializer
from core.authentication import JWTAuthentication

# Create your views here.
class CartAdminListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartAdminSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()

        search = self.request.query_params.get("search", "").strip()
        if search:
            token   = self.request.COOKIES.get('user_session')
            cookies = {"user_session": token} if token else {}
            scope   = "admin"

            resp = UserService.get(f"{scope}/users/?search={search}", cookies=cookies, timeout=5)
            if resp.ok:
                users_data = resp.json().get('data') or resp.json()
                matched_ids = [u['id'] for u in users_data]
                qs = qs.filter(user__in=matched_ids)

        sort_by_completed = self.request.query_params.get("sortByCompleted", "").strip().lower()
        sort_by_date      = self.request.query_params.get("sortByDate",     "").strip().lower()

        if sort_by_completed:
            qs = qs.order_by("completed" if sort_by_completed == "asc" else "-completed")
        elif sort_by_date:
            qs = qs.order_by("-created_at" if sort_by_date == "newest" else "created_at")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

class CartsAdminRetriveAPIView(
    generics.RetrieveAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartAdminSerializer
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class TotalCartAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user_ms

        cart_items = Cart.objects.filter(user=user, completed=False)

        total_items = 0
        total_price = 0.0

        for item in cart_items:
            total_items += item.quantity
            total_price += item.price * item.quantity

        return Response({
            "totalItems": total_items,
            "totalPrice": total_price
        }) 
        
class CartCRUDAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CartCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return CartQuantityUpdateSerializer
        return CartSerializer
    
    def post(self, request):
        return self.create(request)
    
    def get(self, request):
        user = request.user_ms
        
        get_user = Cart.objects.filter(user=user, completed=False)
        
        serializer = self.get_serializer(get_user, many=True)
        
        return Response(serializer.data)
    
    def put(self, request, id):
        user = request.user_ms
        
        check_cart = Cart.objects.filter(id=id, user=user).first()
        
        if not check_cart:
            return Response({"message": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(check_cart, data=request.data, context={'request': request}, partial=True)
        
        serializer.is_valid(raise_exception=True)
        
        updated_data = serializer.save()
        
        response = CartQuantityUpdateSerializer(updated_data)
        
        return Response(response.data)
    
    def delete(self, request, id):
        user = request.user_ms
        
        cart = Cart.objects.filter(id=id, user=user).first()
        
        if not cart:
            return Response({"message": "Not Allowed"}, status=status.HTTP_403_FORBIDDEN)
        
        response = super().destroy(request)
        response.status = status.HTTP_204_NO_CONTENT
        
        return response
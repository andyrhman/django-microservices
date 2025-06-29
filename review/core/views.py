from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.authentication import JWTAuthentication
from core.models import Review
from core.serializers import CreateReviewSerializer, ReviewSerializer
from core.services import ProductService

# Create your views here.
class UserReviewAPIView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        return CreateReviewSerializer if self.request.method == "POST" else ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.method == 'GET':
            product_id = self.kwargs.get('id')
            return Review.objects.filter(product=product_id)
        return Review.objects.filter(user=self.request.user_ms)
    
class AdminReviewAPIView(generics.ListAPIView, generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    queryset               = Review.objects.all()
    serializer_class       = ReviewSerializer
    lookup_field           = 'id'

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(product__title=search) |
                Q(product__description=search)
            )
        return qs
    
    def get(self, request, *args, **kwargs):
        if 'id' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        reviews = list(self.get_queryset())

        product_ids = { str(r.product) for r in reviews }
        product_map = {}
        for pid in product_ids:
            try:
                product_map[pid] = ProductService.get_product_by_id(pid)
            except Exception:
                product_map[pid] = None

        serializer = self.get_serializer(
            reviews,
            many=True,
            context={
                **self.get_serializer_context(),
                "product_map": product_map
            }
        )
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(
            instance,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)
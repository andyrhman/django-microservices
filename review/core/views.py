from django.db.models import Avg, Count
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import JWTAuthentication
from core.models import Review
from core.serializers import CreateReviewSerializer, ReviewSerializer
from core.services import ProductService

# Create your views here.
class UserReviewAPIView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    lookup_field           = 'id'

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
        return Review.objects.filter(user=self.request.user.id)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)

        reviews = serializer.data
        total   = len(reviews)
        average = round(
            sum(r.get('star', 0) for r in reviews) / total,
            2
        ) if total else 0.0

        return Response({
            "reviews":        reviews,
            "review_total":   total,
            "average_rating": average
        }, status=status.HTTP_200_OK)
    
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

class ProductReviewSummaryAPIView(APIView):
    permission_classes = []

    def get(self, request, product_id):
        qs = Review.objects.filter(product=product_id)
        summary = qs.aggregate(
            review_total=Count('id'),
            average_rating=Avg('star')
        )
        return Response({
            "review_total":   summary['review_total'],
            "average_rating": round(summary['average_rating'] or 0.0, 2)
        }, status=status.HTTP_200_OK)
         
class TotalReviewsItemsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, _):
        reviews = Review.objects.all()
        
        total = len(reviews)
        
        return Response({"total": total})   
import math 
from django.core.cache import cache
from django.db.models import Q, Avg, Count, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.html import strip_tags
from rest_framework import generics, mixins, status
from rest_framework import permissions
from rest_framework.fields import FloatField
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import JWTAuthentication
from core.models import Product, ProductImages, ProductVariation
from core.serializers import ProductAdminSerializer, ProductCreateSerializer, ProductImagesCreateSerializer, ProductSerializer, ProductVariationCreateSerializer, ProductVariationSerializer, ProductImagesSerializer
from core.services import CategoryService
from core.utils import TenPerPagePagination

# Create your views here.
class ProductListCreateAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    queryset               = Product.objects.all()
    pagination_class       = TenPerPagePagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductAdminSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        qs      = self.filter_queryset(self.get_queryset())
        ids     = {str(p.category) for p in qs}
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else None
        try:
            cats = CategoryService.list_categories(ids, cookies=cookies)
            self.categories_map = {c['id']: c for c in cats}
        except:
            self.categories_map = {}

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['categories_map'] = getattr(self, 'categories_map', {})
        return ctx

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        product = serializer.save()
        cache.delete_pattern("products:*")
        return product
    
class ProductRUDAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProductCreateSerializer
        return ProductAdminSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        product = serializer.save()
        cache.delete_pattern("products:*")
        return product

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete_pattern("products:*")
        
class ProductVariantCDAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductVariation.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductVariationCreateSerializer
        return ProductSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        saved_variants = serializer.save()
        
        response_variants = ProductVariationSerializer(saved_variants, many=True)
        
        return Response(response_variants.data)
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ProductImagesCDAPIView(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductImagesCreateSerializer
    queryset = ProductImages.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        return super().get_serializer_class()
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_images = serializer.save()
        
        images_serializer = ProductImagesSerializer(saved_images, many=True)
        return Response(images_serializer.data)

class ProductsAPIView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]
    serializer_class   = ProductAdminSerializer
    pagination_class   = TenPerPagePagination

    def get_queryset(self):
        qs = Product.objects.all()

        search = strip_tags(self.request.query_params.get("search", "")).strip()
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        raw_fbc = strip_tags(self.request.query_params.get("filterByCategory", "")).strip()
        if raw_fbc:
            names = [strip_tags(c).strip() for c in raw_fbc.split(",") if c.strip()]

            # fetch all categories from Category-MS
            token   = self.request.COOKIES.get('user_session')
            cookies = {'user_session': token} if token else None
            all_cats = CategoryService.list_all(cookies=cookies)

            # build name→id map
            name_to_id = {c['name']: c['id'] for c in all_cats}
            ids = [name_to_id[n] for n in names if n in name_to_id]

            # apply the UUID‐based filter
            if ids:
                qs = qs.filter(category__in=ids)           

        def to_float(v): 
            try: return float(v)
            except: return None

        min_p = to_float(self.request.query_params.get("minPrice"))
        max_p = to_float(self.request.query_params.get("maxPrice"))

        if min_p is not None:
            qs = qs.filter(price__gte=min_p)
        if max_p is not None:
            qs = qs.filter(price__lte=max_p)

        sbp = self.request.query_params.get("sortByPrice", "").strip().lower()
        sbd = self.request.query_params.get("sortByDate",  "").strip().lower()
        if sbp:
            qs = qs.order_by("price" if sbp == "desc" else "-price")
        elif sbd:
            qs = qs.order_by("-created_at" if sbd == "newest" else "created_at")
        elif (min_p is not None) or (max_p is not None):
            qs = qs.order_by("price")
        else:
            qs = qs.order_by("-updated_at")

        return qs

    def get(self, request, *args, **kwargs):
        # cache key, as you had it
        cache_key = f"products:{request.get_full_path()}"
        if (cached := cache.get(cache_key)) is not None:
            return JsonResponse(cached)

        qs      = self.filter_queryset(self.get_queryset())
        total   = qs.count()
        page    = int(request.query_params.get(self.paginator.page_query_param, 1))
        per_pg  = self.paginator.page_size
        last_pg = math.ceil(total / per_pg) if total else 0
        if total and (page < 1 or page > last_pg):
            return JsonResponse({"message": "Invalid page."}, status=404)

        page_qs = self.paginate_queryset(qs) or []

        ids     = {str(p.category) for p in page_qs}
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else None
        cats    = CategoryService.list_by_ids(ids, cookies=cookies)
        cats_map = {c['id']: {'id': c['id'], 'name': c['name']} for c in cats}

        serializer = self.get_serializer(page_qs, many=True, context={'categories_map': cats_map})
        data       = serializer.data

        payload = {
            "data": data,
            "meta": {
                "total":     total,
                "page":      page if total else 1,
                "last_page": last_pg
            }
        }
        cache.set(cache_key, payload, 30 * 60)
        return JsonResponse(payload)

class ProductAvgRatingAPIView(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]
    queryset = Product.objects.all()
    lookup_field = 'id'
    serializer_class = ProductSerializer
    
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        average = response.data.get('averageRating')
        return Response({"averageRating": average})
    
class ProductVariantsAPIView(generics.ListAPIView):
    serializer_class = ProductVariationSerializer
    queryset = ProductVariation.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
class ProductAPIView(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]   
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        category_id = str(instance.category)

        token = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else None
        cat = CategoryService.list_by_ids([category_id], cookies=cookies)[0]

        cats_map = {cat['id']: {'id': cat['id'], 'name': cat['name']}}
        serializer = self.get_serializer(instance, context={'categories_map': cats_map})

        return Response(serializer.data)
    
class ProductIdAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]   
    pagination_class   = None
    queryset = Product.objects.all()
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
class ProductPriceFilterAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        qs      = self.filter_queryset(self.get_queryset())
        ids     = {str(p.category) for p in qs}
        token   = request.COOKIES.get('user_session')
        cookies = {'user_session': token} if token else None
        try:
            cats = CategoryService.list_categories(ids, cookies=cookies)
            self.categories_map = {c['id']: c for c in cats}
        except:
            self.categories_map = {}

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['categories_map'] = getattr(self, 'categories_map', {})
        return ctx
    
    def get_queryset(self):
        price_param = self.request.data.get("price")
        try:
            price_value = float(price_param)
        except (TypeError, ValueError):
            return Product.objects.none()

        return Product.objects.filter(price__gte=price_value).order_by("price")

    def post(self, request, *args, **kwargs):
        if "price" not in request.data:
            return Response(
                {"detail": "Field 'price' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            price_value = float(request.data["price"])
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid price; must be a number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f"price_filter:{price_value}"
        
        if (cached := cache.get(cache_key)) is not None:
            return JsonResponse(cached, safe=False)

        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        data       = serializer.data

        cache.set(cache_key, data, timeout=30 * 60)

        return JsonResponse(data, safe=False)
    
class ProductCategoryCountAPIView(APIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def get(self, request):
        qs = Product.objects.values('category').annotate(count=Count('id'))
        data = list(qs)
        return JsonResponse(data, safe=False)
    
class TotalProductsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, _):
        product = Product.objects.all()
        
        total = len(product)
        
        return Response({"total": total})
    
class HealthCheckAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {"status": "✅ ok", "message": "🏃‍♀️‍➡️ service is running"},
            status=status.HTTP_200_OK
        )    
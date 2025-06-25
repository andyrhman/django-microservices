import math 
from django.core.cache import cache
from django.db.models import Q, Avg, Count, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.html import strip_tags
from requests import Response
from rest_framework import generics, mixins
from rest_framework.fields import FloatField
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from core.authentication import JWTAuthentication
from core.models import Product
from core.serializers import ProductAdminSerializer, ProductCreateSerializer
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
        
class ProductVariantCDAPIView():
    pass

class ProductImagesCDAPIView():
    pass

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

        # qs = qs.annotate(
        #     average_rating=Coalesce(
        #         Avg("review_products__star"),
        #         Value(0.0),
        #         output_field=FloatField()
        #     )
        # )
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
    
class ProductCategoryCountAPIView(APIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def get(self, request):
        qs = Product.objects.values('category').annotate(count=Count('id'))
        data = list(qs)
        return JsonResponse(data, safe=False)
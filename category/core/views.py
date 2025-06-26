from rest_framework import generics, mixins, status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import ProductService
from core.authentication import JWTAuthentication
from core.serializers import CategorySerializer
from core.models import Category

# Create your views here.
class CategoriesAPIView(APIView):
    def get(self, request):
        token   = request.COOKIES.get('user_session')
        cookies = {"user_session": token} if token else {}

        counts = ProductService.counts_by_category(cookies=cookies)
        count_map = {item['category']: item['count'] for item in counts}

        out = []
        for cat in Category.objects.all():
            out.append({
                "id":            str(cat.id),
                "name":          cat.name,
                "product_total": count_map.get(str(cat.id), 0),
            })
        return Response(out)
    
class CategoryGenericAPIView(
    generics.GenericAPIView, mixins.CreateModelMixin, mixins.UpdateModelMixin, 
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin
):
    authentication_classes= [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'id'
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        if ids:
            id_list = ids.split(',')
            qs = self.get_queryset().filter(id__in=id_list)
            page = self.paginate_queryset(qs)
            ser = self.get_serializer(page or qs, many=True)
            return self.get_paginated_response(ser.data) if page else Response(ser.data)
        
        if 'id' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
        
    def put(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class PublicCategoryListAPIView(generics.ListAPIView):
    queryset           = Category.objects.all()
    serializer_class   = CategorySerializer
    permission_classes = [permissions.AllowAny]   
    pagination_class   = None

    def list(self, request, *args, **kwargs):
        ids = request.query_params.get('ids')
        qs  = self.get_queryset()
        if ids:
            qs = qs.filter(id__in=ids.split(','))
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)
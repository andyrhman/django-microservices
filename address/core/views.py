from rest_framework import exceptions, mixins, status
from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import Address
from core.serializers import AddressSerializer
from core.authentication import JWTAuthentication

# Create your views here.
class AddressAPIView(ListAPIView, RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = AddressSerializer
    lookup_field           = 'id'
    queryset              = Address.objects.all()

    def get(self, request, *args, **kwargs):
        if kwargs.get('id'):
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)
    
class AddressDetailAPIView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Address.objects.get(user=self.request.user_ms)
        except Address.DoesNotExist:
            raise exceptions.NotFound({"message": "Address not found"})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user_ms)

    def post(self, request, *args, **kwargs):
        if Address.objects.filter(user=request.user_ms).exists():
            return Response(
                {"message": "Address already exists"},
                status=status.HTTP_409_CONFLICT
            )
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class HealthCheckAPIView(ListAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {"status": "✅ ok", "message": "🏃‍♀️‍➡️ service is running"},
            status=status.HTTP_200_OK
        )
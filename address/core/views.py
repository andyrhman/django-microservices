from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from core.models import Address
from core.serializers import AddressSerializer
from core.authentication import JWTAuthentication

# Create your views here.
class AddressAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = AddressSerializer

    def get_queryset(self):
        return Address.objects.all()
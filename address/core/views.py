from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Address
from core.serializers import AddressSerializer
from core.authentication import JWTAuthentication

# Create your views here.
class AddressAPIView(APIView):
    def get(self, request):
        qs   = Address.objects.all()
        data = AddressSerializer(qs, many=True, context={'request': request}).data
        return Response(data)
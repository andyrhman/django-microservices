from rest_framework import serializers
from core.services import UserService
from core.models import Address

class BulkUserListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        ids = list({ str(addr.user) for addr in data })

        request = self.child.context.get('request')
        scope   = "admin" if request.path.startswith("/api/admin/") else "user"
        token   = request.COOKIES.get('user_session')

        resp = UserService.post(
            f"{scope}/users/bulk",
            json={"ids": ids},
            cookies={"user_session": token},
            timeout=5
        )
        users_map = resp.ok and resp.json() or {}

        for child in self.child.__class__._declared_fields.values():
            pass

        self.child.context['users_map'] = users_map

        return super().to_representation(data)
    
class AddressSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = "__all__"
        list_serializer_class = BulkUserListSerializer

    def get_user(self, address):
        users_map = self.context.get("users_map", {})
        return users_map.get(str(address.user))
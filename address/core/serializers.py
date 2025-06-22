# core/serializers.py
from rest_framework import serializers
from core.models import Address
from core.services import UserService

class AddressSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model  = Address
        fields = "__all__"

    def get_user(self, address):
        request = self.context['request']
        token   = request.COOKIES.get('user_session')
        scope   = "admin" if request.path.startswith("/api/admin/") else "user"
        # NOTE the trailing slash!
        path    = f"{scope}/{address.user}"

        resp = UserService.get(
            path,
            cookies={'user_session': token},
            timeout=5
        )
        if not resp.ok:
            return None  # or raise an error
        return resp.json()

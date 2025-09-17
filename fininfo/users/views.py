import hashlib
import hmac

from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import TelegramLoginSerializer


User = get_user_model()


class TelegramAuthView(APIView):

    def post(self, request):
        serializer = TelegramLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not self.verify_telegram_auth(data):
            return Response({"error": "Authorization failed"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(telegram_id=data["id"], defaults={
            "username": data.get("username") or f"tg_{data['id']}",
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name") or "",
        })
        refresh = RefreshToken.for_user(user)

        return Response({"message": "success", "data": {
            "id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": data.get("photo_url"),
        }})

    def verify_telegram_auth(self, data):
        received_hash = data.pop("hash")
        auth_data = [f"{k}={v}" for k, v in sorted(data.items())]
        data_check_string = "\n".join(auth_data)
        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
        hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return hmac_hash == received_hash

from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Берём токен сначала из Authorization заголовка (Bearer / TMA),
    если нет — то из куки (access).
    """
    def authenticate(self, request):
        # 1. Сначала пробуем стандартный способ (заголовок)
        header_auth = super().authenticate(request)
        if header_auth is not None:
            return header_auth

        # 2. Если заголовка нет — ищем access в cookies
        access = request.COOKIES.get("access")
        if not access:
            return None

        validated_token = self.get_validated_token(access)
        return self.get_user(validated_token), validated_token

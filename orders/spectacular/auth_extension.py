from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme

from backend.backends import JWTAuthentication


class SimpleJWTTokenUserScheme(SimpleJWTScheme):
    name = "CustomJWTAuth"
    target_class = JWTAuthentication

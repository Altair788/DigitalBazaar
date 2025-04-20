from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# from users.permissions import CanViewAPI

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API DigitalBazaar",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="slobodyanik.ed@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # для продакшн (с ограничением на просмотр API только админам)
    # path("api/schema/", SpectacularAPIView.as_view(permission_classes=[CanViewAPI]), name="schema"),
    # path(
    #     "swagger/", SpectacularSwaggerView.as_view(url_name="schema",
    #     permission_classes=[CanViewAPI]), name="swagger-ui"
    # ),
    # path("redoc/", SpectacularRedocView.as_view(url_name="schema", permission_classes=[CanViewAPI]), name="redoc"),
]

# Добавляем маршруты для работы с медиафайлами только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

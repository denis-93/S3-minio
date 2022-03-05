from django.urls import path
from .views import S3APIView, download
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

app_name ='api'

urlpatterns = [
    path('files', S3APIView.as_view()),
    path('download/<str:file_name>', download, name='download-link'),
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]

from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Polls API",
      default_version='v1',
      description="Методы API приложения для проведения опросов",
   ),
   public=True,
)

urlpatterns = [
    path('',include('polls.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

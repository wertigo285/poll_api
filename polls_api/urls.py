import os

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
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

# Для корректной работы swagger при локальном и docker запуске
if not settings.DEBUG and not os.environ.get('DB_ENGINE'):
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve,
                {'document_root': settings.STATIC_ROOT}),
    ]
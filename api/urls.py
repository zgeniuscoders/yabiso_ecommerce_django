from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")

urlpatterns = [
    path('', include(router.urls)),
]

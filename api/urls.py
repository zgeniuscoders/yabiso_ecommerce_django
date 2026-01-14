from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS, ProductVS

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")
router.register(r'products', ProductVS, basename="products")

urlpatterns = [
    path('', include(router.urls)),
]

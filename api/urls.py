from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS, ProductVS, ProductImageVS

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")
router.register(r'products', ProductVS, basename="products")
router.register('product-images', ProductImageVS, basename="product-images")
urlpatterns = []

urlpatterns = [
    path('', include(router.urls)),
]

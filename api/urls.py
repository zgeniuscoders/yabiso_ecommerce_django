from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS, ProductVS, ProductImageVS, RegisterUserView, OrderViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")
router.register(r'products', ProductVS, basename="products")
router.register('product-images', ProductImageVS, basename="product-images")
router.register('orders', OrderViewSet, basename="orders")

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view()),
]

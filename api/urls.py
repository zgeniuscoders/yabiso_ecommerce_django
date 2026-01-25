from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS, ProductVS, ProductImageVS, RegisterUserView, OrderViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")
router.register(r'products', ProductVS, basename="products")
router.register('product-images', ProductImageVS, basename="product-images")
router.register('orders', OrderViewSet, basename="orders")
router.register('users', UserViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view()),
]

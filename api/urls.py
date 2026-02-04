from django.urls import include, path
from rest_framework import routers

from api.viewset import CategoryVS, ProductVS, RegisterUserView, OrderViewSet, UserViewSet, CartViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryVS, basename="categories")
router.register(r'products', ProductVS, basename="products")
router.register('orders', OrderViewSet, basename="orders")
router.register('users', UserViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view()),
    path('cart/', CartViewSet.as_view()),
]

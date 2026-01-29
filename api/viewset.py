from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Product, ProductImage, Order
from api.serializers import UpsertCategorySerializer, ProductSz, CategoryListSz, ProductImageSz, ProductDetailSz, \
    UserSerializer, AddOrderSerializer, OrderSerializer, OrderListSerializer


@extend_schema_view(
    create=extend_schema(
        request=UpsertCategorySerializer,
        responses=CategoryListSz
    ),
    update=extend_schema(
        request=UpsertCategorySerializer,
        responses=CategoryListSz
    ),
)
class CategoryVS(ModelViewSet):
    queryset = Category.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 20
    pagination_class.page_size_query_param = "perPage"
    pagination_class.max_page_size = 100
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name",)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UpsertCategorySerializer
        return CategoryListSz

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="categories_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="category_details"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        responses=ProductSz(many=True)
    ),
    retrieve=extend_schema(
        responses=ProductDetailSz
    ),
    create=extend_schema(
        request=ProductSz,
        responses=ProductSz
    ),
)
class ProductVS(ModelViewSet):
    serializer_class = ProductSz
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 20
    pagination_class.page_size_query_param = "perPage"
    pagination_class.max_page_size = 100
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name", "price")

    def get_queryset(self):
        qs = Product.objects.all()
        if self.action == 'retrieve':
            qs = (qs.prefetch_related('images')
                  .prefetch_related('category')
                  .prefetch_related('tags'))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSz
        if self.action == 'retrieve':
            return ProductDetailSz
        if self.action == 'create':
            return ProductSz
        return ProductDetailSz

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="products_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="product_details"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema_view(
    request=UserSerializer,
)
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema_view(
    list=extend_schema(
        responses=OrderListSerializer(many=True)
    ),
    retrieve=extend_schema(
        responses=OrderSerializer
    ),
    create=extend_schema(
        request=AddOrderSerializer,
        responses=OrderSerializer
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ("ordered_date", "order_status", "quantity", "total_price")
    ordering_fields = ("ordered_date", "order_status", "quantity", "total_price")

    def get_queryset(self):
        qs = Order.objects.all()
        if self.action == 'retrieve':
            qs = (qs.prefetch_related('items')
                  .prefetch_related('user'))
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderSerializer
        elif self.action == 'create':
            return AddOrderSerializer
        elif self.action == 'list':
            return OrderListSerializer
        return OrderSerializer


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @extend_schema(
        responses=OrderSerializer,
    )
    @action(detail=False, methods=['get'], url_path="orders")
    def order(self, request, *args, **kwargs):
        queryset = Order.objects.filter(user=request.user).order_by('-id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

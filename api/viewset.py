from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Product, ProductImage
from api.serializers import UpsertCategorySerializer, ProductSz, CategoryListSz, ProductImageSz, ProductDetailSz, \
    UserSerializer


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

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UpsertCategorySerializer
        return CategoryListSz


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


@extend_schema_view(
    request=ProductImageSz,
    responses=ProductImageSz,
)
class ProductImageVS(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSz
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticatedOrReadOnly,)


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

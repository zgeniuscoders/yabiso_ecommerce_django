from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet

from api.models import Category, Product, ProductImage
from api.serializers import UpsertCategorySerializer, ProductSz, CategoryListSz, ProductImageSz, ProductDetailSz


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

    def get_queryset(self):
        qs = Product.objects.all()
        if self.action == 'retrieve':
            qs = qs.prefetch_related('images')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSz
        if self.action == 'retrieve':
            return ProductDetailSz
        return ProductDetailSz


@extend_schema_view(
    request=ProductImageSz,
    responses=ProductImageSz,
)
class ProductImageVS(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSz
    parser_classes = (MultiPartParser, FormParser)

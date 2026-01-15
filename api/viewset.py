from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet

from api.models import Category, Product, ProductImage
from api.serializers import UpsertCategorySerializer, ProductSz, CategoryListSz, ProductImageSz


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
    responses=ProductSz,
    request=ProductSz,
)
class ProductVS(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSz
    parser_classes = (MultiPartParser, FormParser)


@extend_schema_view(
    request=ProductImageSz,
    responses=ProductImageSz,
)
class ProductImageVS(ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSz
    parser_classes = (MultiPartParser, FormParser)

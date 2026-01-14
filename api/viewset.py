from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet

from api.models import Category
from api.serializers import CategorySz, UpsertCategorySerializer


@extend_schema_view(
    create=extend_schema(
        request=UpsertCategorySerializer,
        responses=CategorySz
    ),
    update=extend_schema(
        request=UpsertCategorySerializer,
        responses=CategorySz
    ),
)
class CategoryVS(ModelViewSet):
    queryset = Category.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UpsertCategorySerializer
        return CategorySz

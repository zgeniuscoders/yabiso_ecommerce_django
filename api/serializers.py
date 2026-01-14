from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import Category, Product


class UpsertCategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=True,
        allow_empty_file=False,
        use_url=True
    )

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="parent",
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Category
        fields = ["name", "slug", "image", "parent_id"]

    def validate_slug(self, value):
        qs = Category.objects.filter(slug=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Slug déjà utilisé")
        return value

    def validate_image(self, image):
        max_size = 10 * 1024 * 1024  # 2MB
        if image.size > max_size:
            raise serializers.ValidationError("Image trop grande (max 10MB)")
        if not image.content_type.startswith("image/"):
            raise serializers.ValidationError("Fichier non valide, une image est requise")
        return image


class CategoryChildSz(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']


class CategoryListSz(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(required=True)

    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="parent",
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'parent', "parent_id", "children"]
        read_only_fields = ["id", "parent"]

    @extend_schema_field(CategoryChildSz(many=True))
    def get_children(self, obj):
        children = obj.children.all()
        return CategoryChildSz(children, many=True).data


class CategorySz(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']
        read_only_fields = ["id"]


class ProductSz(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    category = CategorySz(read_only=True, many=False)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'image', 'price', 'description', 'category', 'category_id']
        read_only_fields = ["id", "category"]

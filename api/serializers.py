from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.models import Category, Product, ProductImage, Tag, Order, OrderItem


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


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

    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )

    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'image', 'price', 'description', 'category', 'category_id', 'tags', 'images']
        read_only_fields = ["id", "category"]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags")
        images = validated_data.pop("images")

        product = Product.objects.create(**validated_data)

        for productImage in images:
            ProductImage.objects.create(product=product, image=productImage)

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            product.tags.add(tag)
        return product


class ProductImageSz(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        required=False,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product', 'product_id']
        read_only_fields = ["id", 'product']


class ProductDetailSz(serializers.ModelSerializer):
    images = ProductImageSz(many=True, read_only=True)
    category = CategorySz(read_only=True, many=False)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'image',
            'category',
            'price',
            'description',
            'images',
            'tags'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'username', 'password']
        extra_kwargs = {
            'email': {'required': True, 'allow_null': False, 'allow_blank': False},
            'username': {'required': True, 'allow_null': False, 'allow_blank': False},
            'password': {'required': True, 'write_only': True, 'style': {'input_type': 'password'}}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        required=True,
        allow_null=True,
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'order', 'product_id']
        extra_kwargs = {
            'order': {'required': False},
            'product': {'required': False},
            'product_id': {'required': True},
            'quantity': {'required': True},
            'price': {'required': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'quantity', 'items', 'order_status', 'ordered_date']


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'quantity', 'order_status', 'ordered_date']


class AddOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        required=True
    )

    items = serializers.ListField(
        child=OrderItemSerializer(many=False),
        write_only=True,
        required=True
    )

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'quantity', 'items', 'user_id', 'order_status', 'ordered_date']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

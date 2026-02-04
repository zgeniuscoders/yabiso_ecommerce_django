from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to="uploads/categories/", null=False, blank=False)
    parent = models.ForeignKey("self",
                               on_delete=models.CASCADE,
                               related_name="children",
                               null=True,
                               blank=True)

    class Meta:
        db_table = "categories"


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "tags"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='uploads/products/%Y/%m/%d/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name="products",
                                 null=True,
                                 blank=True)
    tags = models.ManyToManyField(Tag, related_name="products", )

    class Meta:
        db_table = "products"


class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='uploads/products/gallery/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CANCELLED = 'CANCELLED', 'Annulée'
        DELIVERED = 'DELIVERED', 'Livrée'
        PROCESSING = 'PROCESSING', 'En traitement'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    quantity = models.PositiveIntegerField(default=1)
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    ordered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    quantity = models.PositiveIntegerField(default=1, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    class Meta:
        db_table = "order_items"


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carts")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "carts"

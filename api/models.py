from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField()
    parent = models.ForeignKey("self",
                               on_delete=models.CASCADE,
                               related_name="children",
                               null=True,
                               blank=True)

    class Meta:
        db_table = "categories"


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey("self",
                                 on_delete=models.CASCADE,
                                 related_name="products",
                                 null=True,
                                 blank=True)

    class Meta:
        db_table = "products"


class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/gallery/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")


class Tag(models.Model):
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product)

    class Meta:
        db_table = "tags"

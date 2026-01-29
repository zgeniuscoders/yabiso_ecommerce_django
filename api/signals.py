from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from api.models import Category, Product


@receiver([post_save, post_delete], sender=Category)
def invalidate_categories_cache(sender, instance, **kwargs):
    cache.delete_many("*categories_list*")
    cache.delete_many("*category_details*")


@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete_many("*products_list*")
    cache.delete_many("*product_details*")

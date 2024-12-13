from loft.models import Category, Product, FavoriteProduct
from django import template

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_colors_product(brand, category):
    products = Product.objects.filter(brand=brand, category=category)
    colors = [i.color_code for i in products]
    return colors


# Функция для сохранения фильтрации
@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value

    return query.urlencode()


@register.simple_tag()
def get_favorites(user):
    favorites = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in favorites]
    return products

@register.simple_tag()
def get_discount_price(price, discount):
    if discount > 0:
        procent = (price * discount) / 100
        price = price - procent

    return f'{price:_}'.replace('_', ' ')


@register.simple_tag()
def get_price(price):
    return f'{price:_}'.replace('_', ' ')
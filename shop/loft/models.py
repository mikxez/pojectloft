from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Категория')
    icon = models.ImageField(upload_to='icons/', null=True, blank=True, verbose_name='Иконка')
    slug = models.SlugField(unique=True, null=True, verbose_name='Поле Slug')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Категория',
                               related_name='subcategories')

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def get_icon(self):
        if self.icon:
            return self.icon.url
        else:
            return '💀'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='В наличии')
    color_name = models.CharField(max_length=100, verbose_name='Название Цвета')
    color_code = models.CharField(max_length=10, verbose_name='Код Цвета')
    discount = models.IntegerField(default=0, null=True, blank=True, verbose_name='Скидка')
    width = models.CharField(max_length=10, verbose_name='Ширина')
    depth = models.CharField(max_length=10, verbose_name='Глубина')
    height = models.CharField(max_length=10, verbose_name='Высота')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория товара', related_name='products')
    brand = models.ForeignKey('BrandProduct', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Бренд товара')
    slug = models.SlugField(unique=True, null=True, verbose_name='Slug товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def get_first_photo(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return '-'
        else:
            return '-'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ImageProduct(models.Model):
    image = models.ImageField(upload_to='product_images/', verbose_name='Картинка товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'


class BrandProduct(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название Бренда (Марка)')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


# Модель для избранных товаров
class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f'Пользователь: {self.user.username} товар {self.product.title}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


#  ======================= Модели для заказа ========================

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=100, verbose_name='Имя покупетля')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия покупетля')
    telegram = models.CharField(max_length=30, verbose_name='Телеграм покупетля', null=True, blank=True)


    def __str__(self):
        return f'Покупатель: {self.user.username}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата закза')
    is_completed = models.BooleanField(default=False, verbose_name='Статус заказа')
    payment = models.BooleanField(default=False, verbose_name='Статус оплаты')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')


    def __str__(self):
        return f'Покупатель: {self.customer.first_name} номер заказа {self.pk}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Здесь будут методы для подсчёта
    @property
    def get_order_total_price(self):
        order_products = self.orderproduct_set.all()  # Через образ модели получим заказанные твоары Заказа
        total_price = sum([product.get_total_price for product in order_products])  # [20 000, 10 000, 20 000]
        return total_price

    @property
    def get_order_total_products(self):
        order_products = self.orderproduct_set.all()
        total_products = sum([product.quantity for product in order_products])  #  [2, 1, 1]
        return total_products


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'Товар {self.product.title} закза №: {self.order.pk}'

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    # Метод получения суммы по количеству
    @property
    def get_total_price(self):
        if self.product.discount:
            sum_proc = (self.product.price * self.product.discount) / 100
            self.product.price -= sum_proc

        total_price = self.product.price * self.quantity
        return total_price

    def total_price(self):
        total_price = self.product.price * self.quantity
        return total_price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель', related_name='shippings')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=150, verbose_name='Адрес доставки (улица, дом, кв)')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона')
    comment = models.TextField(max_length=200, default='Комментарий к заказу', null=True, blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, verbose_name='Регион доставки')
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, verbose_name='Город доставки')

    def __str__(self):
        return f'Заказ №:{self.order.pk} на имя {self.customer.first_name}'

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class Region(models.Model):
    title = models.CharField(max_length=100, verbose_name='Область')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class City(models.Model):
    title = models.CharField(max_length=100, verbose_name='Город')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион', related_name='cities')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField(max_length=50, verbose_name='Номер телефона')
    city = models.CharField(max_length=100, verbose_name='Город', null=True, blank=True)
    street = models.CharField(max_length=100, verbose_name='Улица',  null=True, blank=True)
    home = models.CharField(max_length=100, verbose_name='Дом', null=True, blank=True)
    flat = models.CharField(max_length=100, verbose_name='Квартира', null=True, blank=True)


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

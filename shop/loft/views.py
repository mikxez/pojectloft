from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, CustomerForm, ShippingForm, EditAccountForm, EditProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser
from shop.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
import stripe

# Create your views here.

class ProductListView(ListView):
    model = Product
    template_name = 'loft/index.html'
    extra_context = {
        'title': 'LOFT удобная мебель'
    }
    context_object_name = 'categories'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories



# Вьюшка для страницы детали товара
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=product.category)
        products = [i for i in products if i != product]
        context['products'] = products
        context['title'] = product.title
        return context

# Вьюшка для получения товара по цвету
def product_by_color(request, color_code, category, brand):
    product = Product.objects.get(color_code=color_code,
                                  category__title=category,
                                  brand__title=brand)
    products = Product.objects.filter(category=product.category)
    products = [i for i in products if i != product]
    context = {
        'title': product.title,
        'products': products,
        'product': product
    }
    return render(request, 'loft/product_detail.html', context)




class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'loft/category_page.html'
    paginate_by = 2

    def get_queryset(self):
        cat = self.request.GET.get('cat')
        color = self.request.GET.get('color')
        brand = self.request.GET.get('brand')
        price_from = self.request.GET.get('from')
        price_till = self.request.GET.get('till')

        category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)
        if cat:
            products = products.filter(category__title=cat)
        if color:
            products = products.filter(color_name=color)
        if brand:
            products = products.filter(brand__title=brand)
        if price_from:
            products = [i for i in products if int(i.price) >= int(price_from)]
        if price_till:
            products = [i for i in products if int(i.price) <= int(price_till)]
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = category.title
        context['category'] = category
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)
        context['brands'] = list( set([i.brand for i in products]) )
        context['colors'] = list( set([i.color_name for i in products]) )
        context['subcategories'] = subcategories
        context['prices'] = [i for i in range(500, 100000, 500)]
        context['subcategory'] = self.request.GET.get('cat')
        context['color'] = self.request.GET.get('color')
        context['brand'] = self.request.GET.get('brand')
        context['price_from'] = self.request.GET.get('from')
        context['price_till'] = self.request.GET.get('till')

        return context


# Вьюшка для логина

def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    return redirect('main')
                else:
                    return redirect('login')
            else:
                return redirect('login')
        else:
            form = LoginForm()

    context = {
        'title': 'Авторизация',
        'login_form': form
    }

    return render(request, 'loft/login.html', context)


def logout_user_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main')
    else:
        return redirect('main')


def register_user_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                return redirect('login')
            else:
                return redirect('register')
        else:
            form = RegisterForm()

        context = {
            'title': 'Регистарция',
            'register_form': form
        }

        return render(request, 'loft/register.html', context)


# Вьюшка для добавления товара в Изранное
def add_to_favorite_view(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product in [i.product for i in favorite_products]:
                fav_product = FavoriteProduct.objects.get(product=product, user=user)
                fav_product.delete()
            else:
                FavoriteProduct.objects.create(product=product, user=user)

        next_page = request.META.get('HTTP_REFERER', 'main')  # Получим Адрес Страницы с которой был запрос
        return redirect(next_page)




class FavoriteListView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'loft/favorite.html'
    login_url = 'login'
    extra_context = {
        'title': 'Моё избранное'
    }

    def get_queryset(self):
        favorite = FavoriteProduct.objects.filter(user=self.request.user)
        favorite = [i.product for i in favorite]
        return favorite



class DiscountProduct(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'loft/favorite.html'
    extra_context = {
        'title': 'Товары по акции'
    }

    def get_queryset(self):
        products = Product.objects.all()
        products = [i for i in products if i.discount > 0]
        return products



def add_product_to_cart(request, slug, action):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        user_cart = CartForAuthenticatedUser(request, slug, action)
        next_page = request.META.get('HTTP_REFERER', 'main')  # Получим Адрес страницы с которой делали запрос
        return redirect(next_page)


def my_cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        cart = CartForAuthenticatedUser(request)
        order_info = cart.get_cart_info()  # Получим информацию озаказазынных товарах
        order_products = order_info['order_products']
        products = Product.objects.all()[::-1][:8]

        context = {
            'title': 'Моя корзина',
            'order': order_info['order'],
            'order_products': order_products,
            'products': products
        }

        return render(request, 'loft/my_cart.html', context)



# Вьюшка для удаления товара из корзины
def delete_product_from_cart(request, pk, order):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order_product = OrderProduct.objects.get(pk=pk, order=order)
        order_product.delete()
        return redirect('my_cart')


# Вьюшка для оформления заказа
def checkout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        cart = CartForAuthenticatedUser(request)
        if cart.get_cart_info()['order_products']:
            regions = Region.objects.all()
            dict_city = {i.pk: [[j.title, j.pk] for j in i.cities.all()] for i in regions}

            context = {
                'title': 'Оформление заказа',
                'order': cart.get_cart_info()['order'],
                'order_products': cart.get_cart_info()['order_products'],
                'customer_form': CustomerForm(instance=request.user.customer),
                'shipping_form': ShippingForm(),
                'dict_city': dict_city
            }
            return render(request, 'loft/checkout.html', context)
        else:
            next_page = request.META.get('HTTP_REFERER', 'main')
            return redirect(next_page)



# Вьюшка для оплаты
def create_checkout_session(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        stripe.api_key = STRIPE_SECRET_KEY
        if request.method == 'POST':
            cart = CartForAuthenticatedUser(request)
            order_info = cart.get_cart_info()
            print('sdvsdvsdvdsvsdvdsvsdvsdvsdvsdvsdvsdvsd')

            customer_form = CustomerForm(data=request.POST)
            shipping_form = ShippingForm(data=request.POST)
            ship_address = ShippingAddress.objects.all()
            if customer_form.is_valid() and shipping_form.is_valid():
                customer = Customer.objects.get(user=request.user)
                print(customer.user.username)
                customer.first_name = customer_form.cleaned_data['first_name']
                customer.last_name = customer_form.cleaned_data['last_name']
                customer.telegram = customer_form.cleaned_data['telegram']
                customer.save()
                address = shipping_form.save(commit=False)
                address.customer = customer
                address.order = order_info['order']
                if order_info['order'] not in [i.order for i in ship_address]:
                    address.save()
            else:
                return redirect('checkout')

            total_price = order_info['order_total_price']
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {'name': 'Товары магазна LOFT'},
                        'unit_amount': int(total_price) * 100
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')),
                cancel_url=request.build_absolute_uri(reverse('checkout'))
            )

            return redirect(session.url, 303)


def success_payment(request):
    if not request.user.is_authenticated:
        return redirect('main')
    else:
        cart = CartForAuthenticatedUser(request)
        cart.create_payment()

        context = {
            'title': 'Успешная оплата'
        }

        return render(request, 'loft/success.html', context)


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST':
            account_form = EditAccountForm(request.POST, instance=request.user)
            profile_form = EditProfileForm(request.POST , instance=request.user.profile)
            if account_form.is_valid() and profile_form.is_valid():
                account_form.save()
                profile_form.save()
                return redirect('profile')
        else:
            account_form = EditAccountForm(instance=request.user)
            profile_form = EditProfileForm(instance=request.user.profile)
        try:
            goods = Order.objects.filter(customer=Customer.objects.get(user=request.user), payment=True)
        except:
            goods = None
        context = {
            'title': f'Профиль пользователя: {request.user.username}',
            'account_form': account_form,
            'profile_form': profile_form,
            'items': goods[::-1][:1]
        }

        return render(request, 'loft/profile.html', context)


def order_list(request):
    if not request.user.is_authenticated:
        return redirect('main')
    else:
        try:
            goods = Order.objects.filter(customer=Customer.objects.get(user=request.user), payment=True)
        except:
            goods = None
        if goods:
            context = {
                'items': goods,
                'title': 'Мои заказы'
            }
            return render(request, 'loft/my_orders.html', context)
        else:
            return redirect('main')














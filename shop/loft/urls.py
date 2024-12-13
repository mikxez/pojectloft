from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductListView.as_view(), name='main'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('product_color/<str:color_code>/<str:category>/<str:brand>/', product_by_color, name='product_color'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('login/', user_login_view, name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('registration/', register_user_view, name='register'),
    path('add_favorite/<slug:slug>/', add_to_favorite_view, name='add_favorite'),
    path('my_favorite/', FavoriteListView.as_view(), name='my_favorite'),
    path('sales/', DiscountProduct.as_view(), name='sales'),
    path('add_product/<slug:slug>/<str:action>/', add_product_to_cart, name='add_product'),
    path('my_cart/', my_cart_view, name='my_cart'),
    path('delete/<int:pk>/<int:order>/', delete_product_from_cart, name='delete'),
    path('checkout/', checkout_view, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/', success_payment, name='success'),
    path('profile/', profile_view, name='profile'),
    path('my_orders/', order_list, name='my_orders')
]



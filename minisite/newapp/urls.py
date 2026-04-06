from django.urls import path
from . import views 
urlpatterns = [
    path('',views.home,name='home'),
    path('viewproduct/',views.view_products,name='viewproduct'),
    path('login/',views.login_form,name='login'),
    path('register/',views.register,name='register'),
    path('logout/',views.logout_form,name='logout'),
    path('cart/', views.cart, name='cart'),
    path('add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('search/', views.search, name='search'),
    path('order/', views.place_order, name='place_order'),
    path('orders/', views.orders, name='orders'),
    path('success/', views.success, name='success'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
]
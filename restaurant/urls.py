from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('admin_home',views.admin_home,name='admin_home'),
    path('sales_history',views.sales_history,name='sales_history'),
    path('add_to_cart/<int:item_id>', views.add_to_cart, name='add_to_cart'),
    path('confirm_order',views.confirm_order,name = 'confirm_order'),
    path('place_order',views.place_order,name='place_order'),
    path('change_status',views.change_status,name='change_status'),
    path('manage_menu',views.manage_menu,name='manage_menu'),
    path('update_item',views.update_item,name='update_item'),
    path('add_item',views.add_item,name='add_item'),
    path('remove_item/<int:item_id>',views.remove_item,name='remove_item'),
    path('my_orders',views.user_orders,name='user_orders'),
    path('configure',views.configure,name='configure'),
    path('remove_menu_item/<int:item_id>',views.remove_menu_item,name='remove_menu_item')
 
]

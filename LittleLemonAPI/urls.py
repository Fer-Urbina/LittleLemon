from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token 
from djoser.views import TokenCreateView

urlpatterns = [
    path('category',views.CategoriesView.as_view()),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>',views.SingleMenuItemView.as_view()),
    path('groups/manager/user', views.managers), 
    path('auth/login/', TokenCreateView.as_view()),
    path('update-item-of-the-day/<int:item_id>', views.update_item_of_the_day),
    path('assign-to-delivery-crew/', views.assign_to_delivery_crew),
    path('assign-order-to-delivery/<int:order_id>/', views.assign_order_to_delivery),
    path('get-orders-for-delivery', views.get_orders_for_delivery), 
    path('mark-order-as-delivered/<int:order_id>/', views.mark_order_as_delivered),
    path('get-all-categories', views.get_all_categories), 
    path('get-all-menu-items', views.get_all_menu_items), 
    path('add-to-cart', views.add_to_cart), 
    path('delete-cart-item', views.delete_cart_item),
    path('create-order', views.create_order), 
    path('get-cart-items', views.get_cart_items), 
    path('get-customer-orders', views.get_customer_orders), 
]
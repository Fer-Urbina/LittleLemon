from rest_framework import serializers
from .models import MenuItem, Category, Order, OrderItem, Cart

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'inventory', 'category', 'category_id']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'delivery_crew', 'status']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'quantity', 'user']

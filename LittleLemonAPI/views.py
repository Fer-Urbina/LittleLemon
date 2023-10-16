from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework import generics
from .models import MenuItem, Category, Order, Cart, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, OrderSerializer, CartItemSerializer
from rest_framework import status
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group

@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_id = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering', '')  
        perpage = int(request.query_params.get('perpage', 10)) 
        page = request.query_params.get('page', 1)
        
        if category_id:
            items = items.filter(category__title=category_id)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    elif request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status=status.HTTP_201_CREATED)


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price','inventory',]
    filterset_fields = ['price','inventory',]
    search_fields = ['category']

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({"message":"ok"})
    
    return Response({"message":"error"}), status.HTTP_400_BAD_REQUEST

@api_view(['POST']) # Managers can update the item of the day
@permission_classes([IsAuthenticated, IsAdminUser])
def update_item_of_the_day(request, item_id):
    if request.method == 'POST':
        try:
            menu_item = MenuItem.objects.get(pk=item_id)
        except MenuItem.DoesNotExist:
            return Response({"message": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the 'item_of_the_day' field for the chosen menu item
        menu_item.item_of_the_day = True
        menu_item.save()
        
        return Response({"message": "Item of the day updated successfully."})

@api_view(['POST']) # Managers can assign users to the delivery crew
@permission_classes([IsAdminUser])  
def assign_to_delivery_crew(request):
    username = request.data.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        delivery_crew_group = Group.objects.get(name="Delivery Crew")
        delivery_crew_group.user_set.add(user)
        return Response({"message": "User assigned to Delivery Crew successfully."})
    return Response({"message": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST']) # Managers can assign orders to the delivery crew
@permission_classes([IsAdminUser])
def assign_order_to_delivery(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Retrieve the order details
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data)

    elif request.method == 'POST':
        # Managers can assign the order to a specific delivery person (user)
        username = request.data.get('username')
        if username:
            try:
                delivery_crew = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"message": "Delivery person not found."}, status=status.HTTP_404_NOT_FOUND)

            # Assign the order to the selected delivery person
            order.delivery_crew = delivery_crew
            order.save()
            return Response({"message": "Order assigned to the delivery person successfully."})

        return Response({"message": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET']) # Delivery crew can access orders assigned to them
@permission_classes([IsAuthenticated])
def get_orders_for_delivery(request):
    # Get orders assigned to the authenticated user as the delivery person
    orders = Order.objects.filter(delivery_crew=request.user)
    serialized_orders = OrderSerializer(orders, many=True)
    return Response(serialized_orders.data)

@api_view(['POST']) # Delivery crew can update an order as delivered
@permission_classes([IsAuthenticated])
def mark_order_as_delivered(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"message":"Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if order.delivery_crew != request.user:
        return Response({"message":"You are not authorized to update this order"}, status=status.HTTP_403_FORBIDDEN)
    
    # Update the order status to "Delivered" 
    order.status = "Delivered"
    order.save()

    # Serialize the updated order
    serialized_order = OrderSerializer(order)
    return Response(serialized_order.data)

@api_view(['GET']) # Customers can browse all categories:
def get_all_categories(request):
    categories = Category.objects.all()
    serialized_categories = CategorySerializer(categories, many=True)
    return Response(serialized_categories.data)

@api_view(['GET']) # Customers can browse all the menu items at once
def get_all_menu_items(request):
    menu_items = MenuItem.objects.all()
    serialized_menu_items = MenuItemSerializer(menu_items, many=True)
    return Response(serialized_menu_items.data)

@api_view(['POST']) # Customers can add menu items to the cart
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    menu_item_id = request.data.get('menu_item_id')
    quantity = request.data.get('quantity', 1)

    if not menu_item_id:
        return Response({"message": "menu_item_id is required."}, status=status.HTTP_404_NOT_FOUND)

    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({"message": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    # Try to get the cart item, or create it if it doesn't exist
    cart_item, created = Cart.objects.get_or_create(user=user, menuitem=menu_item)

    if not created:
        # Update the quantity if the item is already in the cart
        cart_item.quantity += quantity
        cart_item.save()

    return Response({"message": "Item added to cart."}, status=status.HTTP_201_CREATED)

@api_view(['DELETE']) 
@permission_classes([IsAuthenticated])
def delete_cart_item(request):
    user = request.user

    Cart.objects.filter(user=user).delete()

    return Response({"message":"Cart items deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    # Get the authenticated user
    user = request.user
    
    # Get current cart items for the user
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items:
        return Response({"message": "No items in the cart"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new order for the user
    order = Order.objects.create(user=user)
    
    # Add cart items to the order
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            menuitem=cart_item.menuitem,
            quantity=cart_item.quantity,
        )
    
    # Clear the user's cart
    cart_items.delete()
    
    return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
    
@api_view(['GET']) # Customers can access previously added items in the cart
@permission_classes([IsAuthenticated])
def get_cart_items(request):
    # Get the authenticated user
    user = request.user
    
    # Get cart items associated with the user
    cart_items = Cart.objects.filter(user=user)
    
    # Serialize and return the cart items
    serializer = CartItemSerializer(cart_items, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) # Customers can browse their own orders
@permission_classes([IsAuthenticated])
def get_customer_orders(request):
    # Get the authenticated user
    user = request.user
    
    # If the user is not in the "Manager" group, restrict the query to their own orders.
    if not user.groups.filter(name='Manager').exists():
        orders = Order.objects.filter(user=user)
    else:
        # Managers can see all orders.
        orders = Order.objects.all()
    
    # Serialize and return the orders
    serializer = OrderSerializer(orders, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

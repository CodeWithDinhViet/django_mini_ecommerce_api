from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
    
        return [IsAdminUser()]
    
    
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        if category:
            queryset = queryset.filter(category_id=category)
            
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
            
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        
        return [IsAdminUser()]
    
    
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='my-cart')
    def my_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)
    
    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            return Response(
                {'quantity': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'product': 'Product not found or inactive'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            new_quantity = cart_item.quantity + quantity
            
            if new_quantity > product.stock:
                return Response(
                    {'quantity': 'Quantity exceeds available stock.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            if quantity > product.stock:
                cart_item.delete()
                return Response(
                    {'quantity': 'Quantity exceeds available stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = int(request.data.get('quantity', cart_item.quantity))
        
        if quantity <= 0:
            return Response(
                {'quantity': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if quantity > cart_item.product.stock:
            return Response(
                {'quantity': 'Quantity exceeds available stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)
        
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
        
        
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.all()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Please use /api/orders/checkout/ to create an order'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
        
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response(
                {'detail': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        shipping_address = request.data.get('shipping_address')
        phone_number = request.data.get('phone_number')
        note = request.data.get('note', '')
        
        if not shipping_address:
            return Response(
                {'shipping_address': 'This field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
        if not phone_number:
            return Response(
                {'phone_number': 'This field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {
                        'detail': f'Not enough stock for product: {item.product.name}. '
                        f'Available stock: {item.product.stock}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone_number=phone_number,
            note=note,
            total_amount=0
        )
        
        total_amount = 0
        
        for item in cart_items:
            product = item.product
            subtotal = product.price * item.quantity
            
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
                subtotal=subtotal
            )
            
            product.stock -= item.quantity
            product.save()
            
            total_amount += subtotal
            
        order.total_amount = total_amount
        order.save()
        
        cart_items.delete()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
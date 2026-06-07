from django.shortcuts import render
from rest_framework import viewsets, generics, status, serializers
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from django.db.models import Sum, Count
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    ReviewSerializer,
    ReportSummarySerializer,
)

from .filters import ProductFilter, OrderFilter, ReviewFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        
        return [IsAdminUser()]
    
    
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
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
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Order.objects.all().order_by('created_at')
        
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
    
    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status != 'pending':
            return Response(
                {'detail': 'Only pending orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
            
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only admin users can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        order = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['pending', 'paid', 'shipping', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return Response(
                {'status': 'Invalid status. Valid statuses are: pending, paid, shipping, completed, cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if order.status in ['completed', 'cancelled']:
            return Response(
                {'detail': 'Cannot update status of compeleted or cancelled orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Review.objects.all().order_by('-created_at')
        return queryset
    
    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        user = self.request.user
        
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            order__status='completed',
            product=product
        ).exists()
        
        if not has_purchased:
            raise serializers.ValidationError(
                {'detail': 'You can only review products you have purchased and completed'}
            )
        
        already_reviewed = Review.objects.filter(
            user=user,
            product=product
        ).exists()
        
        if already_reviewed:
            raise serializers.ValidationError(
                {'detail': 'You have already reviewed this product'}
            )
            
        serializer.save(user=user)
        

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ReportSummarySerializer
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        total_orders = Order.objects.count()
        
        completed_orders = Order.objects.filter(status='completed')
        
        total_revenue = completed_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        total_products = Product.objects.count()
        
        low_stock_products = Product.objects.filter(stock__lte=5).count()
        
        total_reviews = Review.objects.count()
        
        data = {
            'total_order':total_orders,
            'total_revenue':total_revenue,
            'total_products':total_products,
            'low_stock_products':low_stock_products,
            'total_reviews':total_reviews,
        }
        
        serializer = ReportSummarySerializer(data)
        return Response(data)

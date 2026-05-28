from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review
)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
    
class CategorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'creted_at']
        
        
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'stock',
            'is_active',
            'average_rating',
            'review_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'category_name',
            'review_count',
            'created_at',
            'updated_at',
        ]
        
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        
        if not reviews.exists():
            return 0
        
        total_rating = sum(review.rating for review in reviews)
        return round(total_rating/reviews.count(), 1)
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'quantity',
            'subtotal',
        ]
        read_only_fields = [
            'id',
            'product_name',
            'product_price',
            'subtotal',
        ]
        
    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity
    
    def validate_quantity(self, value):
        if value <=0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        return value
    
    
class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'items',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        
    def get_total_amount(self, obj):
        total = 0
        
        for item in obj.items.all():
            total += item.product.price * item.quantity
            
        return total
    
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'price',
            'quantity',
            'subtotal',
        ]
        read_only_fields = [
            'id',
            'product',
            'product_name',
            'price',
            'quantity',
            'subtotal',
        ]
        
        
class OrderSrializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'shipping_address',
            'phone_number',
            'npte',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'total_amount',
            'items',
            'created_at',
            'updated_at',
        ]
        
        
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'product_name',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'product_name',
            'created_at',
        ]
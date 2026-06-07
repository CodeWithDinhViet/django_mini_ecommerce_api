import django_filters

from .models import Product, Order, Review


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Product
        fields = [
            'category',
            'is_active',
            'min_price',
            'max_price',
        ]
        
        
class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = [
            'status',
        ]
        
        
class ReviewFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = [
            'product',
        ]
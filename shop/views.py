from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.models import User
from .models import Category, Product
from .serializers import (
    RegisterSerializer,
    CategorySerializer,
    ProductSerializer,
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
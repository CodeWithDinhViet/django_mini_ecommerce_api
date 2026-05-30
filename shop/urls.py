from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
)

router = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')

router.register('products', ProductViewSet, basename='product')

router.register('cart', CartViewSet, basename='cart')

router.register('cart/items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    
    path('', include(router.urls)),
]
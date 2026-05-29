from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    
    path('', include(router.urls)),
]
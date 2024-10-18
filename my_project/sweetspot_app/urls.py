from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CakeViewSet, CakeCustomizationViewSet, CartViewSet, OrderViewSet


router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'cakes', CakeViewSet)
router.register(r'cake-customizations', CakeCustomizationViewSet)
router.register(r'carts', CartViewSet)
router.register(r'orders', OrderViewSet,basename='order')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/customers/login/', CustomerViewSet.as_view({'post': 'login'}), name='customer-login'),
    path('api/carts/add-to-cart/', CartViewSet.as_view({'post': 'add_to_cart'}), name='add-to-cart'),
    path('api/orders/<int:pk>/update-order/', OrderViewSet.as_view({'post': 'update_order'}), name='update-order'),
]

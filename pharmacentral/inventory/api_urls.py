from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'drugs', api_views.DrugViewSet)
router.register(r'customers', api_views.CustomerViewSet)
router.register(r'sales', api_views.SaleViewSet)
router.register(r'debtors', api_views.DebtorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

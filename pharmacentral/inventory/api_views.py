from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Drug, Customer, Sale, Debtor
from .serializers import DrugSerializer, CustomerSerializer, SaleSerializer, DebtorSerializer


class DrugViewSet(viewsets.ModelViewSet):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'quantity', 'expiry_date']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        from django.db.models import F
        drugs = Drug.objects.filter(quantity__lte=F('minimum_quantity'))
        serializer = self.get_serializer(drugs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        from datetime import date
        drugs = Drug.objects.filter(expiry_date__lt=date.today())
        serializer = self.get_serializer(drugs, many=True)
        return Response(serializer.data)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'phone']


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related('items__drug').all()
    serializer_class = SaleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer_name']
    ordering_fields = ['sale_date', 'total_amount']


class DebtorViewSet(viewsets.ModelViewSet):
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['customer_name']

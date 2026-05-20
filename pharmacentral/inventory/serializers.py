from rest_framework import serializers
from .models import Drug, Customer, Sale, SaleItem, Debtor


class DrugSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model = Drug
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class SaleItemSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(source='drug.name', read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = SaleItem
        fields = ['id', 'drug', 'drug_name', 'quantity', 'unit_price', 'subtotal']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'


class DebtorSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Debtor
        fields = '__all__'

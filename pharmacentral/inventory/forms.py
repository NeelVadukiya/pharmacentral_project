from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Drug, Customer, Sale, SaleItem, Debtor, Purchase, DrugCategory


class DrugCategoryForm(forms.ModelForm):
    class Meta:
        model = DrugCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Antibiotic'}),
        }


class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ['code', 'name', 'description', 'category', 'quantity',
                  'minimum_quantity', 'unit_price', 'expiry_date', 'supplier']
        widgets = {
            'code':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AMX-500'}),
            'name':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amoxicillin 500mg'}),
            'description':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Antibiotic capsule'}),
            'category':         forms.Select(attrs={'class': 'form-control'}),
            'quantity':         forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unit_price':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'expiry_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sun Pharma'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'address', 'notes']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient full name'}),
            'phone':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'notes':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Allergies, conditions...'}),
        }


class DebtorForm(forms.ModelForm):
    class Meta:
        model = Debtor
        fields = ['customer_name', 'amount_owed', 'due_date', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name'}),
            'amount_owed':   forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'due_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason / description'}),
        }


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['drug', 'quantity_received', 'unit_cost', 'supplier',
                  'purchase_date', 'invoice_number', 'notes']
        widgets = {
            'drug':              forms.Select(attrs={'class': 'form-control'}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_cost':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'supplier':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'purchase_date':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'invoice_number':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice / bill number'}),
            'notes':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'}),
        }


class SalesReportForm(forms.Form):
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From Date'
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To Date'
    )

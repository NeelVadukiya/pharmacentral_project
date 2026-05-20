from django.contrib import admin
from .models import Drug, DrugCategory, Customer, Sale, SaleItem, Debtor, Purchase, AuditLog


@admin.register(DrugCategory)
class DrugCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name']
    search_fields = ['name']


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'category', 'quantity', 'minimum_quantity', 'unit_price', 'expiry_date', 'supplier']
    list_filter   = ['category']
    search_fields = ['code', 'name', 'description']
    ordering      = ['name']


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display  = ['id', 'customer_name', 'total_amount', 'sale_date', 'created_by']
    list_filter   = ['sale_date']
    search_fields = ['customer_name']
    inlines       = [SaleItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone', 'address']
    search_fields = ['name', 'phone']


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display  = ['customer_name', 'amount_owed', 'due_date', 'is_paid']
    list_filter   = ['is_paid']
    search_fields = ['customer_name']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display  = ['id', 'drug', 'quantity_received', 'unit_cost', 'supplier', 'purchase_date', 'received_by']
    search_fields = ['drug__name', 'supplier', 'invoice_number']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ['timestamp', 'user', 'action', 'model_name', 'object_repr']
    list_filter   = ['action', 'model_name']
    readonly_fields = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'object_repr', 'details']

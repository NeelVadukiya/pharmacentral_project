from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class DrugCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Drug Categories'

    def __str__(self):
        return self.name


class Drug(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(DrugCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='drugs')
    quantity = models.PositiveIntegerField(default=0)
    minimum_quantity = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    supplier = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def days_until_expiry(self):
        return (self.expiry_date - date.today()).days

    @property
    def status(self):
        days = self.days_until_expiry
        if days < 0:
            return 'expired'
        elif days <= 30:
            return 'expiring'
        elif self.quantity <= self.minimum_quantity:
            return 'low'
        return 'ok'

    @property
    def status_label(self):
        return {'expired': 'Expired', 'expiring': 'Expiring Soon', 'low': 'Low Stock', 'ok': 'OK'}.get(self.status, 'OK')

    @property
    def category_name(self):
        return self.category.name if self.category else 'Uncategorised'


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Sale(models.Model):
    customer_name = models.CharField(max_length=200, default='Walk-in')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_date = models.DateField(default=date.today)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f"Sale #{self.id} - {self.customer_name} ({self.sale_date})"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.drug.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class Debtor(models.Model):
    customer_name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='debts')
    amount_owed = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_paid', 'due_date']

    def __str__(self):
        return f"{self.customer_name} - Rs.{self.amount_owed}"

    @property
    def is_overdue(self):
        if self.is_paid or not self.due_date:
            return False
        return self.due_date < date.today()


class Purchase(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT, related_name='purchases')
    quantity_received = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200, blank=True)
    purchase_date = models.DateField(default=date.today)
    invoice_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"Purchase #{self.id} - {self.drug.name} x{self.quantity_received}"

    @property
    def total_cost(self):
        return self.quantity_received * self.unit_cost


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"

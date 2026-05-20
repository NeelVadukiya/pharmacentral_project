from django.urls import path
from . import views

urlpatterns = [
    # ── Auth (custom — no 405 errors) ──────────────────────────────────────
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard ───────────────────────────────────────────────────────────
    path('', views.dashboard, name='dashboard'),

    # ── Inventory ───────────────────────────────────────────────────────────
    path('inventory/',                  views.inventory_list, name='inventory_list'),
    path('inventory/add/',              views.drug_add,       name='drug_add'),
    path('inventory/<int:pk>/edit/',    views.drug_edit,      name='drug_edit'),
    path('inventory/<int:pk>/delete/',  views.drug_delete,    name='drug_delete'),

    # ── Categories ──────────────────────────────────────────────────────────
    path('categories/',                 views.category_list,   name='category_list'),
    path('categories/add/',             views.category_add,    name='category_add'),
    path('categories/<int:pk>/edit/',   views.category_edit,   name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # ── Sales ───────────────────────────────────────────────────────────────
    path('sales/',                       views.sales_list,       name='sales_list'),
    path('sales/create/',                views.sale_create,      name='sale_create'),
    path('sales/<int:pk>/delete/',       views.sale_delete,      name='sale_delete'),
    path('sales/<int:pk>/invoice/',      views.sale_invoice_pdf, name='sale_invoice_pdf'),
    path('sales/report/',                views.sales_report,     name='sales_report'),
    path('sales/report/export/',         views.sales_report_csv, name='sales_report_csv'),

    # ── Customers ───────────────────────────────────────────────────────────
    path('customers/',                  views.customer_list,   name='customer_list'),
    path('customers/add/',              views.customer_add,    name='customer_add'),
    path('customers/<int:pk>/edit/',    views.customer_edit,   name='customer_edit'),
    path('customers/<int:pk>/delete/',  views.customer_delete, name='customer_delete'),

    # ── Debtors ─────────────────────────────────────────────────────────────
    path('debtors/',                        views.debtor_list,      name='debtor_list'),
    path('debtors/add/',                    views.debtor_add,       name='debtor_add'),
    path('debtors/<int:pk>/edit/',          views.debtor_edit,      name='debtor_edit'),
    path('debtors/<int:pk>/mark-paid/',     views.debtor_mark_paid, name='debtor_mark_paid'),
    path('debtors/<int:pk>/delete/',        views.debtor_delete,    name='debtor_delete'),

    # ── Purchases ───────────────────────────────────────────────────────────
    path('purchases/',                  views.purchase_list,   name='purchase_list'),
    path('purchases/add/',              views.purchase_add,    name='purchase_add'),
    path('purchases/<int:pk>/delete/',  views.purchase_delete, name='purchase_delete'),

    # ── Alerts ──────────────────────────────────────────────────────────────
    path('alerts/', views.alerts_view, name='alerts'),

    # ── Audit Log ───────────────────────────────────────────────────────────
    path('audit/', views.audit_log_view, name='audit_log'),

    # ── Staff Management (Admin only) ───────────────────────────────────────
    path('staff/',                     views.staff_list,   name='staff_list'),
    path('staff/add/',                 views.staff_add,    name='staff_add'),
    path('staff/<int:pk>/edit/',       views.staff_edit,   name='staff_edit'),
    path('staff/<int:pk>/delete/',     views.staff_delete, name='staff_delete'),

    # ── Password Change ─────────────────────────────────────────────────────
    path('password/', views.change_password, name='change_password'),

    # ── AJAX ────────────────────────────────────────────────────────────────
    path('api/drug/<int:pk>/price/', views.drug_price_api, name='drug_price_api'),
]

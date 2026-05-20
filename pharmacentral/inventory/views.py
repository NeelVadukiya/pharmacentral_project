import csv
import io
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (CustomerForm, DebtorForm, DrugCategoryForm, DrugForm,
                    PurchaseForm, SalesReportForm)
from .models import (AuditLog, Customer, Debtor, Drug, DrugCategory, Purchase,
                     Sale, SaleItem)


# ── helpers ───────────────────────────────────────────────────────────────────

def log_action(request, action, obj, details=''):
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=obj.__class__.__name__,
        object_id=str(obj.pk),
        object_repr=str(obj),
        details=details,
    )


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def build_alerts():
    today  = date.today()
    thirty = today + timedelta(days=30)
    alerts = []
    for d in Drug.objects.filter(expiry_date__lt=today):
        alerts.append({'type': 'danger', 'msg': f'{d.name} has EXPIRED (expiry: {d.expiry_date}).'})
    for d in Drug.objects.filter(expiry_date__gte=today, expiry_date__lte=thirty):
        days = (d.expiry_date - today).days
        alerts.append({'type': 'warn', 'msg': f'{d.name} expires in {days} day(s) on {d.expiry_date}.'})
    for d in Drug.objects.filter(quantity__lte=F('minimum_quantity'), expiry_date__gte=today):
        alerts.append({'type': 'warn', 'msg': f'{d.name} is low: {d.quantity} units left (min: {d.minimum_quantity}).'})
    for dbt in Debtor.objects.filter(is_paid=False, due_date__lt=today):
        alerts.append({'type': 'danger', 'msg': f'{dbt.customer_name} has overdue debt of Rs.{dbt.amount_owed} (due: {dbt.due_date}).'})
    return alerts


def base_ctx(request):
    return {'alert_count': len(build_alerts()), 'is_admin': is_admin(request.user)}


# ── auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    # If already logged in send to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # go to page user was trying to visit, or dashboard
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)
        else:
            return render(request, 'inventory/login.html', {
                'error': 'Invalid username or password. Please try again.',
                'username': username,
            })
    return render(request, 'inventory/login.html', {})


def logout_view(request):
    # Works for both GET and POST — no 405 error
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ── dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today  = date.today()
    thirty = today + timedelta(days=30)
    ctx = base_ctx(request)
    ctx.update({
        'total_drugs':   Drug.objects.count(),
        'low_stock':     Drug.objects.filter(quantity__lte=F('minimum_quantity')).count(),
        'expired':       Drug.objects.filter(expiry_date__lt=today).count(),
        'expiring_soon': Drug.objects.filter(expiry_date__gte=today, expiry_date__lte=thirty).count(),
        'total_sales':   Sale.objects.count(),
        'total_revenue': Sale.objects.aggregate(t=Sum('total_amount'))['t'] or 0,
        'recent_sales':  Sale.objects.prefetch_related('items__drug')[:8],
        'alerts':        build_alerts(),
        # Show "everything on /" (small previews)
        'inventory_preview': Drug.objects.select_related('category').all()[:12],
        'customers_preview': Customer.objects.all()[:12],
        'debtors_preview': Debtor.objects.filter(is_paid=False).all()[:12],
        'purchases_preview': Purchase.objects.select_related('drug').all()[:10],
    })
    return render(request, 'inventory/dashboard.html', ctx)


# ── categories ────────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    ctx = base_ctx(request)
    ctx.update({'categories': DrugCategory.objects.all(), 'form': DrugCategoryForm()})
    return render(request, 'inventory/categories.html', ctx)


@login_required
def category_add(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = DrugCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            log_action(request, 'CREATE', cat)
            messages.success(request, f'Category "{cat.name}" added.')
        else:
            messages.error(request, 'Category name is required and must be unique.')
    return redirect('category_list')


@login_required
def category_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    cat = get_object_or_404(DrugCategory, pk=pk)
    if request.method == 'POST':
        form = DrugCategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            log_action(request, 'UPDATE', cat)
            messages.success(request, f'Category updated to "{cat.name}".')
            return redirect('category_list')
    else:
        form = DrugCategoryForm(instance=cat)
    ctx = base_ctx(request)
    ctx.update({'form': form, 'cat': cat})
    return render(request, 'inventory/category_edit.html', ctx)


@login_required
def category_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    cat = get_object_or_404(DrugCategory, pk=pk)
    if request.method == 'POST':
        name = cat.name
        log_action(request, 'DELETE', cat)
        cat.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('category_list')
    ctx = base_ctx(request)
    ctx.update({'object': cat, 'object_type': 'Category'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── inventory ─────────────────────────────────────────────────────────────────

@login_required
def inventory_list(request):
    today  = date.today()
    thirty = today + timedelta(days=30)
    drugs  = Drug.objects.select_related('category').all()
    query           = request.GET.get('query', '')
    status_filter   = request.GET.get('status_filter', 'all')
    category_filter = request.GET.get('category_filter', '')

    if query:
        drugs = drugs.filter(Q(name__icontains=query) | Q(code__icontains=query) | Q(description__icontains=query))
    if category_filter:
        drugs = drugs.filter(category__id=category_filter)
    if status_filter == 'expired':
        drugs = drugs.filter(expiry_date__lt=today)
    elif status_filter == 'expiring':
        drugs = drugs.filter(expiry_date__gte=today, expiry_date__lte=thirty)
    elif status_filter == 'low':
        drugs = drugs.filter(quantity__lte=F('minimum_quantity'), expiry_date__gte=today)

    ctx = base_ctx(request)
    ctx.update({'drugs': drugs, 'query': query, 'status_filter': status_filter,
                'category_filter': category_filter, 'categories': DrugCategory.objects.all()})
    return render(request, 'inventory/inventory.html', ctx)


@login_required
def drug_add(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('inventory_list')
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            drug = form.save()
            log_action(request, 'CREATE', drug)
            messages.success(request, 'Drug added successfully.')
            return redirect(next_url or 'inventory_list')
    else:
        form = DrugForm()
    ctx = base_ctx(request)
    ctx.update({'form': form, 'title': 'Add New Drug', 'next_url': next_url})
    return render(request, 'inventory/drug_form.html', ctx)


@login_required
def drug_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('inventory_list')
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            log_action(request, 'UPDATE', drug)
            messages.success(request, 'Drug updated successfully.')
            return redirect('inventory_list')
    else:
        form = DrugForm(instance=drug)
    ctx = base_ctx(request)
    ctx.update({'form': form, 'title': f'Edit: {drug.name}', 'drug': drug})
    return render(request, 'inventory/drug_form.html', ctx)


@login_required
def drug_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('inventory_list')
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        log_action(request, 'DELETE', drug)
        drug.delete()
        messages.success(request, 'Drug deleted.')
        return redirect('inventory_list')
    ctx = base_ctx(request)
    ctx.update({'object': drug, 'object_type': 'Drug'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── sales ─────────────────────────────────────────────────────────────────────

@login_required
def sales_list(request):
    query = request.GET.get('query', '')
    sales = Sale.objects.prefetch_related('items__drug').all()
    if query:
        sales = sales.filter(
            Q(customer_name__icontains=query) | Q(items__drug__name__icontains=query)
        ).distinct()
    ctx = base_ctx(request)
    ctx.update({
        'sales': sales, 'query': query,
        'drugs': Drug.objects.select_related('category').filter(expiry_date__gte=date.today()),
        'customers': Customer.objects.all(),
    })
    return render(request, 'inventory/sales.html', ctx)


@login_required
def sale_create(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', 'Walk-in').strip() or 'Walk-in'
        sale_date     = request.POST.get('sale_date', str(date.today()))
        drug_ids      = request.POST.getlist('drug_id[]')
        quantities    = request.POST.getlist('quantity[]')
        prices        = request.POST.getlist('price[]')

        valid_items = [(did, quantities[i], prices[i])
                       for i, did in enumerate(drug_ids) if did.strip()]
        if not valid_items:
            messages.error(request, 'Add at least one item to the sale.')
            return redirect('sales_list')

        for did, qty_str, _ in valid_items:
            drug = get_object_or_404(Drug, pk=did)
            if drug.quantity < int(qty_str):
                messages.error(request, f'Not enough stock for {drug.name}. Available: {drug.quantity}')
                return redirect('sales_list')

        sale  = Sale.objects.create(customer_name=customer_name, sale_date=sale_date, created_by=request.user)
        total = 0
        for did, qty_str, price_str in valid_items:
            drug  = get_object_or_404(Drug, pk=did)
            qty   = int(qty_str)
            price = float(price_str)
            SaleItem.objects.create(sale=sale, drug=drug, quantity=qty, unit_price=price)
            drug.quantity -= qty
            drug.save()
            total += qty * price

        sale.total_amount = total
        sale.save()
        log_action(request, 'CREATE', sale, f'Total Rs.{total:.2f}')
        messages.success(request, f'Sale #{sale.id} of Rs.{total:.2f} processed successfully.')
    return redirect('sales_list')


@login_required
def sale_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('sales_list')
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        for item in sale.items.all():
            item.drug.quantity += item.quantity
            item.drug.save()
        log_action(request, 'DELETE', sale)
        sale.delete()
        messages.success(request, 'Sale deleted and stock restored.')
        return redirect('sales_list')
    ctx = base_ctx(request)
    ctx.update({'object': sale, 'object_type': 'Sale'})
    return render(request, 'inventory/confirm_delete.html', ctx)


@login_required
def sale_invoice_pdf(request, pk):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    except ImportError:
        messages.error(request, 'reportlab not installed. Run: pip install reportlab')
        return redirect('sales_list')

    sale = get_object_or_404(Sale, pk=pk)
    buf  = io.BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []

    title_style = ParagraphStyle('t', fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)
    sub_style   = ParagraphStyle('s', fontSize=10, alignment=TA_CENTER, spaceAfter=2)
    story.append(Paragraph('PharmaCentral', title_style))
    story.append(Paragraph('Medicine Inventory Management', sub_style))
    story.append(Spacer(1, 0.4*cm))

    meta = [
        ['Invoice No :', f'INV-{sale.id:04d}', 'Date :', str(sale.sale_date)],
        ['Customer :',   sale.customer_name,    'Served by :', str(sale.created_by or 'Staff')],
    ]
    mt = Table(meta, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    mt.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME',  (0,0), (0,-1),  'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1),  'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.5*cm))

    header = [['#', 'Drug Name', 'Qty', 'Unit Price (Rs.)', 'Subtotal (Rs.)']]
    rows   = []
    for i, item in enumerate(sale.items.all(), 1):
        rows.append([str(i), item.drug.name, str(item.quantity),
                     f'{float(item.unit_price):.2f}', f'{float(item.subtotal):.2f}'])
    rows.append(['', '', '', 'TOTAL', f'{float(sale.total_amount):.2f}'])

    tbl = Table(header + rows, colWidths=[1*cm, 9*cm, 2*cm, 3.5*cm, 3.5*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',     (0,0),  (-1,0),  colors.HexColor('#1a6e5c')),
        ('TEXTCOLOR',      (0,0),  (-1,0),  colors.white),
        ('FONTNAME',       (0,0),  (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',       (0,1),  (-1,-1), 'Helvetica'),
        ('FONTSIZE',       (0,0),  (-1,-1), 9),
        ('ALIGN',          (2,0),  (-1,-1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0,1),  (-1,-2), [colors.white, colors.HexColor('#f4f6f8')]),
        ('FONTNAME',       (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND',     (0,-1), (-1,-1), colors.HexColor('#e0f5f2')),
        ('LINEBELOW',      (0,0),  (-1,0),  1, colors.HexColor('#1a6e5c')),
        ('LINEABOVE',      (0,-1), (-1,-1), 1, colors.HexColor('#1a6e5c')),
        ('TOPPADDING',     (0,0),  (-1,-1), 5),
        ('BOTTOMPADDING',  (0,0),  (-1,-1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6*cm))

    footer_style = ParagraphStyle('f', fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
    story.append(Paragraph('Thank you for your purchase. Please keep this receipt for your records.', footer_style))

    doc.build(story)
    buf.seek(0)
    resp = HttpResponse(buf, content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="invoice_{sale.id:04d}.pdf"'
    return resp


@login_required
def sales_report(request):
    form   = SalesReportForm(request.GET or None)
    sales  = None
    total  = 0
    d_from = d_to = None
    if form.is_valid():
        d_from = form.cleaned_data['date_from']
        d_to   = form.cleaned_data['date_to']
        sales  = Sale.objects.filter(sale_date__gte=d_from, sale_date__lte=d_to).prefetch_related('items__drug')
        total  = sales.aggregate(t=Sum('total_amount'))['t'] or 0
    ctx = base_ctx(request)
    ctx.update({'form': form, 'sales': sales, 'total': total, 'date_from': d_from, 'date_to': d_to})
    return render(request, 'inventory/sales_report.html', ctx)


@login_required
def sales_report_csv(request):
    d_from = request.GET.get('date_from')
    d_to   = request.GET.get('date_to')
    if not d_from or not d_to:
        messages.error(request, 'Please select a date range first.')
        return redirect('sales_report')
    sales = Sale.objects.filter(sale_date__gte=d_from, sale_date__lte=d_to).prefetch_related('items__drug')
    resp  = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="sales_{d_from}_to_{d_to}.csv"'
    w = csv.writer(resp)
    w.writerow(['Sale ID', 'Date', 'Customer', 'Items', 'Total (Rs.)'])
    for sale in sales:
        items_str = ' | '.join(f'{i.drug.name} x{i.quantity}' for i in sale.items.all())
        w.writerow([f'#{sale.id}', sale.sale_date, sale.customer_name, items_str, sale.total_amount])
    return resp


# ── customers ─────────────────────────────────────────────────────────────────

@login_required
def customer_list(request):
    query     = request.GET.get('query', '')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    ctx = base_ctx(request)
    ctx.update({'customers': customers, 'form': CustomerForm(), 'query': query})
    return render(request, 'inventory/customers.html', ctx)


@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            c = form.save()
            log_action(request, 'CREATE', c)
            messages.success(request, 'Customer added.')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('customer_list')


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            log_action(request, 'UPDATE', customer)
            messages.success(request, 'Customer updated.')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    ctx = base_ctx(request)
    ctx.update({'form': form, 'customer': customer})
    return render(request, 'inventory/customer_form.html', ctx)


@login_required
def customer_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('customer_list')
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        log_action(request, 'DELETE', customer)
        customer.delete()
        messages.success(request, 'Customer deleted.')
        return redirect('customer_list')
    ctx = base_ctx(request)
    ctx.update({'object': customer, 'object_type': 'Customer'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── debtors ───────────────────────────────────────────────────────────────────

@login_required
def debtor_list(request):
    query   = request.GET.get('query', '')
    debtors = Debtor.objects.all()
    if query:
        debtors = debtors.filter(customer_name__icontains=query)
    outstanding = Debtor.objects.filter(is_paid=False).aggregate(t=Sum('amount_owed'))['t'] or 0
    ctx = base_ctx(request)
    ctx.update({'debtors': debtors, 'form': DebtorForm(), 'query': query, 'total_outstanding': outstanding})
    return render(request, 'inventory/debtors.html', ctx)


@login_required
def debtor_add(request):
    if request.method == 'POST':
        form = DebtorForm(request.POST)
        if form.is_valid():
            d = form.save()
            log_action(request, 'CREATE', d)
            messages.success(request, 'Debtor record added.')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('debtor_list')


@login_required
def debtor_edit(request, pk):
    debtor = get_object_or_404(Debtor, pk=pk)
    if request.method == 'POST':
        form = DebtorForm(request.POST, instance=debtor)
        if form.is_valid():
            form.save()
            log_action(request, 'UPDATE', debtor)
            messages.success(request, 'Debtor updated.')
            return redirect('debtor_list')
    else:
        form = DebtorForm(instance=debtor)
    ctx = base_ctx(request)
    ctx.update({'form': form, 'debtor': debtor})
    return render(request, 'inventory/debtor_form.html', ctx)


@login_required
def debtor_mark_paid(request, pk):
    debtor           = get_object_or_404(Debtor, pk=pk)
    debtor.is_paid   = True
    debtor.paid_date = date.today()
    debtor.save()
    log_action(request, 'UPDATE', debtor, 'Marked as paid')
    messages.success(request, f'{debtor.customer_name} marked as paid.')
    return redirect('debtor_list')


@login_required
def debtor_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('debtor_list')
    debtor = get_object_or_404(Debtor, pk=pk)
    if request.method == 'POST':
        log_action(request, 'DELETE', debtor)
        debtor.delete()
        messages.success(request, 'Debtor record deleted.')
        return redirect('debtor_list')
    ctx = base_ctx(request)
    ctx.update({'object': debtor, 'object_type': 'Debtor Record'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── purchases ─────────────────────────────────────────────────────────────────

@login_required
def purchase_list(request):
    query     = request.GET.get('query', '')
    purchases = Purchase.objects.select_related('drug', 'received_by').all()
    if query:
        purchases = purchases.filter(
            Q(drug__name__icontains=query) | Q(supplier__icontains=query) | Q(invoice_number__icontains=query)
        )
    ctx = base_ctx(request)
    ctx.update({'purchases': purchases, 'form': PurchaseForm(), 'query': query})
    return render(request, 'inventory/purchases.html', ctx)


@login_required
def purchase_add(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase             = form.save(commit=False)
            purchase.received_by = request.user
            purchase.save()
            drug           = purchase.drug
            drug.quantity += purchase.quantity_received
            drug.save()
            log_action(request, 'CREATE', purchase,
                       f'Added {purchase.quantity_received} units to {drug.name}')
            messages.success(request,
                f'{purchase.quantity_received} units of {drug.name} restocked. New stock: {drug.quantity}')
        else:
            messages.error(request, 'Please fix the errors.')
    return redirect('purchase_list')


@login_required
def purchase_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('purchase_list')
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        drug           = purchase.drug
        drug.quantity -= purchase.quantity_received
        if drug.quantity < 0:
            drug.quantity = 0
        drug.save()
        log_action(request, 'DELETE', purchase)
        purchase.delete()
        messages.success(request, 'Purchase deleted and stock reversed.')
        return redirect('purchase_list')
    ctx = base_ctx(request)
    ctx.update({'object': purchase, 'object_type': 'Purchase Record'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── alerts ────────────────────────────────────────────────────────────────────

@login_required
def alerts_view(request):
    alerts = build_alerts()
    ctx    = base_ctx(request)
    ctx['alerts'] = alerts
    return render(request, 'inventory/alerts.html', ctx)


# ── audit log ─────────────────────────────────────────────────────────────────

@login_required
def audit_log_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    logs = AuditLog.objects.select_related('user').all()[:200]
    ctx  = base_ctx(request)
    ctx['logs'] = logs
    return render(request, 'inventory/audit_log.html', ctx)


# ── staff management ──────────────────────────────────────────────────────────

@login_required
def staff_list(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    staff_users = User.objects.all().order_by('username')
    ctx = base_ctx(request)
    ctx['staff_users'] = staff_users
    return render(request, 'inventory/staff_list.html', ctx)


@login_required
def staff_add(request):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        password   = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        role       = request.POST.get('role', 'staff')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('staff_list')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('staff_list')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('staff_list')

        user            = User.objects.create_user(username=username, password=password,
                                                    first_name=first_name, last_name=last_name)
        user.is_staff   = (role == 'admin')
        user.is_superuser = (role == 'admin')
        user.save()
        log_action(request, 'CREATE', user, f'Role: {role}')
        messages.success(request, f'User "{username}" created successfully as {"Admin" if role == "admin" else "Staff"}.')
    return redirect('staff_list')


@login_required
def staff_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    staff_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        first_name       = request.POST.get('first_name', '').strip()
        last_name        = request.POST.get('last_name', '').strip()
        role             = request.POST.get('role', 'staff')
        new_password     = request.POST.get('new_password', '').strip()
        is_active        = request.POST.get('is_active') == 'on'

        staff_user.first_name   = first_name
        staff_user.last_name    = last_name
        staff_user.is_staff     = (role == 'admin')
        staff_user.is_superuser = (role == 'admin')
        staff_user.is_active    = is_active

        if new_password:
            if len(new_password) < 6:
                messages.error(request, 'New password must be at least 6 characters.')
                ctx = base_ctx(request)
                ctx['staff_user'] = staff_user
                return render(request, 'inventory/staff_edit.html', ctx)
            staff_user.set_password(new_password)

        staff_user.save()
        log_action(request, 'UPDATE', staff_user, f'Role changed to {role}')
        messages.success(request, f'User "{staff_user.username}" updated.')
        return redirect('staff_list')

    ctx = base_ctx(request)
    ctx['staff_user'] = staff_user
    return render(request, 'inventory/staff_edit.html', ctx)


@login_required
def staff_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    staff_user = get_object_or_404(User, pk=pk)
    if staff_user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('staff_list')
    if request.method == 'POST':
        username = staff_user.username
        log_action(request, 'DELETE', staff_user)
        staff_user.delete()
        messages.success(request, f'User "{username}" deleted.')
        return redirect('staff_list')
    ctx = base_ctx(request)
    ctx.update({'object': staff_user, 'object_type': 'User Account'})
    return render(request, 'inventory/confirm_delete.html', ctx)


# ── password change ───────────────────────────────────────────────────────────

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    ctx = base_ctx(request)
    ctx['form'] = form
    return render(request, 'inventory/change_password.html', ctx)


# ── ajax ──────────────────────────────────────────────────────────────────────

@login_required
def drug_price_api(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    return JsonResponse({'price': float(drug.unit_price), 'name': drug.name, 'stock': drug.quantity})

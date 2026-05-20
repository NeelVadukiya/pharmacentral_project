from django.db import migrations, models
import django.db.models.deletion
from datetime import date


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [

        # DrugCategory must come first since Drug FK depends on it
        migrations.CreateModel(
            name='DrugCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name'], 'verbose_name_plural': 'Drug Categories'},
        ),

        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),

        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('category', models.ForeignKey(
                    null=True, blank=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='drugs',
                    to='inventory.drugcategory',
                )),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('minimum_quantity', models.PositiveIntegerField(default=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expiry_date', models.DateField()),
                ('supplier', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),

        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(default='Walk-in', max_length=200)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('sale_date', models.DateField(default=date.today)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sales', to='inventory.customer',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sales', to='auth.user',
                )),
            ],
            options={'ordering': ['-sale_date', '-created_at']},
        ),

        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('drug', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='sale_items', to='inventory.drug',
                )),
                ('sale', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='inventory.sale',
                )),
            ],
        ),

        migrations.CreateModel(
            name='Debtor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=200)),
                ('amount_owed', models.DecimalField(decimal_places=2, max_digits=12)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='debts', to='inventory.customer',
                )),
            ],
            options={'ordering': ['is_paid', 'due_date']},
        ),

        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_received', models.PositiveIntegerField()),
                ('unit_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('supplier', models.CharField(blank=True, max_length=200)),
                ('purchase_date', models.DateField(default=date.today)),
                ('invoice_number', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('drug', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='purchases', to='inventory.drug',
                )),
                ('received_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='auth.user',
                )),
            ],
            options={'ordering': ['-purchase_date', '-created_at']},
        ),

        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(
                    choices=[('CREATE', 'Created'), ('UPDATE', 'Updated'), ('DELETE', 'Deleted')],
                    max_length=10,
                )),
                ('model_name', models.CharField(max_length=100)),
                ('object_id', models.CharField(blank=True, max_length=50)),
                ('object_repr', models.CharField(max_length=300)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField(blank=True)),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='auth.user',
                )),
            ],
            options={'ordering': ['-timestamp']},
        ),
    ]

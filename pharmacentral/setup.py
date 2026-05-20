#!/usr/bin/env python3
"""
PharmaCentral – One-click Setup Script
Run once after cloning:

    pip install -r requirements.txt
    python setup.py
"""
import os, sys, subprocess

def run(cmd):
    print(f"  >> {cmd}")
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        print(f"\n  ERROR running: {cmd}")
        sys.exit(1)

print("=" * 52)
print("   PharmaCentral – Setup")
print("=" * 52)

print("\n[1] Installing requirements...")
run("pip install -r requirements.txt")

print("\n[2] Applying database migrations...")
run("python manage.py migrate")

print("\n[3] Loading sample data...")
run("python manage.py loaddata inventory/fixtures/initial_data.json")

print("\n[4] Creating admin superuser...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacentral.settings')
import django
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pharmalocal.com', 'admin123')
    print("  >> Created: username=admin  password=admin123")
else:
    print("  >> Admin already exists.")

print("\n[5] Creating sample salesperson account...")
if not User.objects.filter(username='staff').exists():
    User.objects.create_user('staff', 'staff@pharmalocal.com', 'staff123')
    print("  >> Created: username=staff  password=staff123  (salesperson role)")
else:
    print("  >> Staff user already exists.")

print("\n" + "=" * 52)
print("  Setup complete!")
print()
print("  Start server :  python manage.py runserver")
print("  Open browser :  http://127.0.0.1:8000")
print()
print("  ADMIN login  :  admin / admin123  (full access)")
print("  STAFF login  :  staff / staff123  (salesperson)")
print("  Django admin :  http://127.0.0.1:8000/admin")
print("=" * 52)

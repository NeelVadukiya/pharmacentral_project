#!/usr/bin/env python3
"""
PharmaCentral — UPDATE SCRIPT
===============================
Run this inside your pharmacentral folder:

    python UPDATE_EXISTING_PROJECT.py

This will fix all errors and start fresh.
"""
import os, sys, subprocess, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

def run(cmd):
    print(f"  >> {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=str(HERE))
    if r.returncode != 0:
        print(f"\n  ERROR running: {cmd}")
        sys.exit(1)

print("=" * 55)
print("  PharmaCentral — Fix & Fresh Setup")
print("=" * 55)

# Step 1 — delete old database
db = HERE / 'db.sqlite3'
if db.exists():
    db.unlink()
    print("\n[1] Old database deleted.")
else:
    print("\n[1] No old database found.")

# Step 2 — delete all __pycache__ folders (stale bytecode causes errors)
print("\n[2] Clearing cached bytecode...")
for p in HERE.rglob('__pycache__'):
    shutil.rmtree(p, ignore_errors=True)
print("  >> Done.")

# Step 3 — install requirements
print("\n[3] Installing requirements...")
run("pip install -r requirements.txt")

# Step 4 — migrate (single clean migration)
print("\n[4] Running database migration...")
run("python manage.py migrate")

# Step 5 — load sample data
print("\n[5] Loading sample data...")
run("python manage.py loaddata inventory/fixtures/initial_data.json")

# Step 6 — create users
print("\n[6] Creating users...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacentral.settings')
sys.path.insert(0, str(HERE))
import django
django.setup()
from django.contrib.auth.models import User

# Admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pharma.local', 'admin123')
else:
    u = User.objects.get(username='admin')
    u.is_staff = True; u.is_superuser = True; u.is_active = True
    u.set_password('admin123'); u.save()
print("  >> Admin ready:  admin / admin123")

# Staff
if not User.objects.filter(username='staff').exists():
    User.objects.create_user('staff', 'staff@pharma.local', 'staff123')
else:
    u = User.objects.get(username='staff')
    u.is_staff = False; u.is_superuser = False; u.is_active = True
    u.set_password('staff123'); u.save()
print("  >> Staff ready:  staff / staff123")

print("\n" + "=" * 55)
print("  Setup complete! Run:")
print()
print("      python manage.py runserver")
print()
print("  Open:   http://127.0.0.1:8000")
print("  Admin:  admin / admin123")
print("  Staff:  staff / staff123")
print("=" * 55)

# PharmaCentral – Medicine Inventory Management System

A full-stack pharmacy management web application built with Python/Django.

---

## Features

- **Dashboard** – Summary stats, recent sales, live alerts
- **Drug Inventory** – Add, edit, delete drugs with code, name, category, quantity, expiry, price, supplier
- **Expiry Monitoring** – Automatic alerts for expired and expiring-soon drugs (≤30 days)
- **Low Stock Alerts** – Configurable minimum quantity threshold per drug
- **Sales** – Process multi-item sales, auto-deducts stock, full history
- **Customers** – Patient records with medical notes
- **Debtors** – Track credit/unpaid amounts, mark as paid, overdue alerts
- **REST API** – Full DRF API at `/api/`
- **Admin Panel** – Django admin at `/admin/`
- **Search** – Search drugs by name, code, or description

---

## Tech Stack

- **Backend:** Python 3.x, Django 4.x, Django REST Framework
- **Database:** SQLite (file: `db.sqlite3`)
- **Frontend:** HTML5, CSS3, JavaScript (no frameworks needed)

---

## Setup Instructions

### Step 1 – Prerequisites
Make sure you have Python 3.8+ installed:
```
python --version
```

### Step 2 – Install dependencies
```
pip install -r requirements.txt
```

### Step 3 – Run setup (migrations + sample data + admin user)
```
python setup.py
```

This will:
- Run all database migrations
- Load sample drug/customer/debtor data
- Create admin user: `admin` / `admin123`

### Step 4 – Start the server
```
python manage.py runserver
```

### Step 5 – Open in browser
```
http://127.0.0.1:8000
```
Login with: **admin** / **admin123**

---

## Project Structure

```
pharmacentral/
├── manage.py                    # Django management
├── setup.py                     # One-click setup script
├── requirements.txt
├── db.sqlite3                   # Auto-created SQLite database
│
├── pharmacentral/               # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── inventory/                   # Main app
│   ├── models.py                # Drug, Sale, Customer, Debtor models
│   ├── views.py                 # All page views
│   ├── forms.py                 # Django forms
│   ├── urls.py                  # URL routing
│   ├── api_urls.py              # REST API routes
│   ├── api_views.py             # DRF viewsets
│   ├── serializers.py           # DRF serializers
│   ├── admin.py                 # Django admin config
│   ├── fixtures/
│   │   └── initial_data.json    # Sample seed data
│   └── templates/inventory/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── inventory.html
│       ├── drug_form.html
│       ├── sales.html
│       ├── customers.html
│       ├── customer_form.html
│       ├── debtors.html
│       ├── debtor_form.html
│       ├── alerts.html
│       └── confirm_delete.html
│
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## REST API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/drugs/` | List all drugs |
| `POST /api/drugs/` | Add drug |
| `GET /api/drugs/{id}/` | Drug detail |
| `PUT /api/drugs/{id}/` | Update drug |
| `DELETE /api/drugs/{id}/` | Delete drug |
| `GET /api/drugs/low_stock/` | Low stock drugs |
| `GET /api/drugs/expired/` | Expired drugs |
| `GET /api/sales/` | List all sales |
| `GET /api/customers/` | List customers |
| `GET /api/debtors/` | List debtors |

Search: `GET /api/drugs/?search=amoxicillin`

---

## Default Login

| Field | Value |
|-------|-------|
| Username | admin |
| Password | admin123 |

> Change the password after first login via `/admin/`

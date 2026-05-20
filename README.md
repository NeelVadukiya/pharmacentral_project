# PharmaCentral – Pharmacy Management System

PharmaCentral is a full-stack web-based Pharmacy Management System developed using Python, Django, and SQLite to automate pharmacy operations including inventory management, billing, customer records, debtor tracking, sales monitoring, and real-time medicine alerts.

The system helps pharmacists efficiently manage medicine stock, monitor expiry dates, process sales transactions, and maintain customer/debtor records through a centralized and user-friendly dashboard.

---

# Features

## Dashboard
- Summary statistics and recent sales overview
- Real-time expiry and low-stock alerts
- Inventory monitoring dashboard

## Authentication & Authorization
- Secure login system
- Role-Based Access Control (RBAC)
- Admin & Staff access management

## Medicine Inventory Management
- Add, update, delete medicines
- Manage medicine code, category, quantity, supplier, and pricing
- Search medicines by name, code, or description

## Expiry & Stock Monitoring
- Automatic expired medicine alerts
- Expiring-soon medicine notifications (≤30 days)
- Low stock quantity alerts

## Sales & Billing
- Multi-item sales processing
- Automatic stock deduction after sales
- Invoice and billing management
- Sales history tracking

## Customer & Debtor Management
- Store customer details and medical notes
- Track debtor records and unpaid balances
- Overdue payment monitoring

## REST API Support
- Full Django REST Framework (DRF) API support
- API endpoints for medicines, sales, customers, and debtors

## Admin Panel
- Django admin panel integration
- Easy data management through `/admin/`

---

# Tech Stack

## Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Backend
- Python 3.x
- Django 4.x
- Django REST Framework (DRF)

## Database
- SQLite

## Tools & Platforms
- GitHub
- VS Code

---

# System Architecture

The project follows a 3-Tier Architecture:

1. Presentation Layer (Frontend UI)
2. Business Logic Layer (Django Backend)
3. Data Layer (SQLite Database)

This architecture ensures scalability, maintainability, and secure data handling.

---

# Installation & Setup

## Step 1 – Clone Repository

```bash
git clone https://github.com/NeelVadukiya/pharmacentral_project.git
```

---

## Step 2 – Navigate to Project Folder

```bash
cd pharmacentral
```

---

## Step 3 – Create Virtual Environment

```bash
python -m venv venv
```

---

## Step 4 – Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 5 – Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 6 – Run Database Migrations

```bash
python manage.py migrate
```

---

## Step 7 – Start Development Server

```bash
python manage.py runserver
```

---

## Step 8 – Open in Browser

```text
http://127.0.0.1:8000
```

---

# Default Admin Login

| Field | Value |
|-------|-------|
| Username | admin |
| Password | admin123 |

> Change the password after first login.

---

# Project Structure

```text
pharmacentral/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── pharmacentral/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── inventory/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── admin.py
│   └── templates/
│
├── static/
│   ├── css/
│   └── js/
│
└── screenshots/
```

---

# REST API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/drugs/` | List all medicines |
| `POST /api/drugs/` | Add medicine |
| `GET /api/drugs/{id}/` | Medicine details |
| `PUT /api/drugs/{id}/` | Update medicine |
| `DELETE /api/drugs/{id}/` | Delete medicine |
| `GET /api/drugs/low_stock/` | Low stock medicines |
| `GET /api/drugs/expired/` | Expired medicines |
| `GET /api/sales/` | Sales records |
| `GET /api/customers/` | Customer records |
| `GET /api/debtors/` | Debtor records |

### Search Example

```http
GET /api/drugs/?search=paracetamol
```

---

# Future Enhancements

- Barcode Scanner Integration
- Mobile Application Support
- AI-Based Demand Forecasting
- Multi-Branch Pharmacy Management
- Online Prescription Upload
- Advanced Analytics Dashboard

---

# Learning Outcomes

- Django Full Stack Development
- REST API Development
- Database Design & Management
- Authentication & Authorization
- Inventory & Billing Logic
- Real-Time Alert Systems
- Backend Optimization

---

# Author

## Neel Vadukiya

- LinkedIn: https://www.linkedin.com/in/neel-vadukiya-495099285/
- GitHub: https://github.com/NeelVadukiya

---

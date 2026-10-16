# First Django – E-commerce Product Management

A Django web application for managing products and categories, with product inventory fields and dashboard pages for customers and administrators.

## 🚀 Features

- **Product Management:** Store product names, descriptions, prices, and stock quantities.
- **Category Management:** Organize products into categories.
- **Database Relationships:** Connect products to categories using Django `ForeignKey`.
- **Inventory Tracking:** Maintain stock quantities and product availability.
- **Product Availability:** Enable or disable products using an `is_active` field.
- **Django Admin:** Manage application data through Django's administration interface.
- **Dashboard Pages:** Includes templates for customer and admin dashboards.
- **SQLite Database:** Store application data using Django's default SQLite database.

## 🛠️ Tech Stack

- Python
- Django
- SQLite
- HTML and CSS
- Django Templates

## 📁 Project Structure

```text
FIRST-DJANGO/
├── config/
│   └── ...
├── products/
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── db.sqlite3
├── manage.py
├── .venv/
└── README.md
```


## 🗄️ Database Models

### Category

The `Category` model represents a product category.

| Field | Type | Purpose |
|---|---|---|
| `name` | `CharField` | Stores the category name |

### Product

The `Product` model stores product information.

| Field | Type | Purpose |
|---|---|---|
| `name` | `CharField` | Product name |
| `description` | `TextField` | Product description |
| `category` | `ForeignKey` | Links the product to a category |
| `price` | `DecimalField` | Product price |
| `stock` | `IntegerField` | Available stock quantity |
| `is_active` | `BooleanField` | Indicates whether the product is active |



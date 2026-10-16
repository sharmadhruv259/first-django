
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Products
    path(
        'products/<int:product_id>/',
        views.product_details,
        name='product_detail'
    ),
    path('api/products/', views.products, name='products_api'),

    # Dashboards
    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),
    path(
        'customer-dashboard/',
        views.customer_dashboard,
        name='customer_dashboard'
    ),

    # Product management
    path(
        'admin-dashboard/products/',
        views.admin_product_list,
        name='admin_product_list'
    ),
path(
    'admin-dashboard/categories/',
    views.admin_category_list,
    name='admin_category_list'
),
path(
    'admin-dashboard/users/',
    views.admin_user_list,
    name='admin_user_list'
),
]
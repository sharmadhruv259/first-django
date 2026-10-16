from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Product, category
from .forms import ProductForm


UserModel = get_user_model()


# Check whether the logged-in user is an Admin
def is_admin_user(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name='Admin').exists()
        )
    )


# Home page
def home(request):
    if request.user.is_authenticated:
        if is_admin_user(request.user):
            return redirect('admin_dashboard')
        return redirect('customer_dashboard')

    products = Product.objects.select_related('category').filter(
        is_active=True
    )

    return render(request, 'products/index.html', {
        'products': products
    })


# Customer registration
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            customer_group, _ = Group.objects.get_or_create(
                name='Customer'
            )
            user.groups.add(customer_group)

            login(request, user)
            messages.success(
                request,
                'Account created successfully!'
            )

            return redirect('customer_dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form': form
    })


# Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if is_admin_user(user):
                return redirect('admin_dashboard')

            return redirect('customer_dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form
    })


# Logout - accepts POST requests only
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(
            request,
            'You have logged out successfully.'
        )

    return redirect('home')


# Admin dashboard
@login_required
def admin_dashboard(request):
    if not is_admin_user(request.user):
        messages.error(
            request,
            'You are not allowed to access that page.'
        )
        return redirect('customer_dashboard')

    return render(request, 'admin_dashboard.html')


# Customer dashboard
@login_required
def customer_dashboard(request):
    if is_admin_user(request.user):
        return redirect('admin_dashboard')

    products = Product.objects.select_related('category').filter(
        is_active=True
    )

    return render(request, 'customer_dashboard.html', {
        'products': products
    })


# Admin: View, Add, Edit, Toggle and Delete products
@login_required
def admin_product_list(request):
    if not is_admin_user(request.user):
        messages.error(
            request,
            'You are not allowed to access that page.'
        )
        return redirect('customer_dashboard')

    edit_product = None
    form = ProductForm()

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        product_id = request.POST.get('product_id', '').strip()

        # Toggle product visibility
        if action == 'toggle':
            if not product_id:
                messages.error(request, 'No product was selected.')
            else:
                product = get_object_or_404(
                    Product,
                    id=product_id
                )

                product.is_active = not product.is_active
                product.save(update_fields=['is_active'])

                if product.is_active:
                    messages.success(
                        request,
                        f'"{product.name}" is now visible in the portal.'
                    )
                else:
                    messages.success(
                        request,
                        f'"{product.name}" has been hidden from the portal.'
                    )

            return redirect('admin_product_list')

        # Delete product permanently
        elif action == 'delete':
            if not product_id:
                messages.error(request, 'No product was selected.')
            else:
                product = get_object_or_404(
                    Product,
                    id=product_id
                )
                product.delete()
                messages.success(
                    request,
                    'Product deleted successfully.'
                )

            return redirect('admin_product_list')

        # Add or edit product
        elif action in ('add', 'edit'):
            product = None

            if action == 'edit':
                if not product_id:
                    messages.error(
                        request,
                        'No product was selected for editing.'
                    )
                    return redirect('admin_product_list')

                product = get_object_or_404(
                    Product,
                    id=product_id
                )

            form = ProductForm(
                request.POST,
                instance=product
            )

            if form.is_valid():
                form.save()

                if action == 'add':
                    messages.success(
                        request,
                        'Product added successfully.'
                    )
                else:
                    messages.success(
                        request,
                        'Product updated successfully.'
                    )

                return redirect('admin_product_list')

            edit_product = product

        else:
            messages.error(request, 'Invalid product action.')
            return redirect('admin_product_list')

    # Load product for editing when requested by GET
    elif request.GET.get('edit'):
        edit_product = get_object_or_404(
            Product,
            id=request.GET.get('edit')
        )
        form = ProductForm(instance=edit_product)

    # Admin must see active AND inactive products
    products = Product.objects.select_related(
        'category'
    ).all().order_by('id')

    return render(request, 'admin_products.html', {
        'products': products,
        'form': form,
        'edit_product': edit_product,
    })


# Public product list with search and category filtering
def product_list(request):
    products = Product.objects.select_related('category').filter(
        is_active=True
    )
    categories = category.objects.all()

    search_query = request.GET.get('q', '').strip()

    if search_query:
        products = products.filter(
            name__icontains=search_query
        )

    selected_category = request.GET.get('category', '')

    if selected_category.isdigit():
        products = products.filter(
            category_id=int(selected_category)
        )
    elif selected_category:
        selected_category = ''

    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    })


# Product details: inactive products are not available to customers
def product_details(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('category'),
        id=product_id,
        is_active=True
    )

    return render(request, 'product_details.html', {
        'product': product
    })


# Product API: return active products only
def products(request):
    product_queryset = Product.objects.select_related(
        'category'
    ).filter(is_active=True)

    data = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'stock': product.stock,
            'category': product.category.name,
        }
        for product in product_queryset
    ]

    return JsonResponse(data, safe=False)


# Admin: Manage categories
@login_required
def admin_category_list(request):
    if not is_admin_user(request.user):
        messages.error(
            request,
            'You are not allowed to access that page.'
        )
        return redirect('customer_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category_id', '').strip()

        if action == 'add':
            if not name:
                messages.error(
                    request,
                    'Category name is required.'
                )
            elif category.objects.filter(
                name__iexact=name
            ).exists():
                messages.error(
                    request,
                    'This category already exists.'
                )
            else:
                category.objects.create(name=name)
                messages.success(
                    request,
                    'Category added successfully.'
                )

        elif action == 'edit':
            if not category_id:
                messages.error(
                    request,
                    'No category was selected.'
                )
            elif not name:
                messages.error(
                    request,
                    'Category name is required.'
                )
            else:
                item = get_object_or_404(
                    category,
                    id=category_id
                )

                duplicate_exists = category.objects.filter(
                    name__iexact=name
                ).exclude(id=item.id).exists()

                if duplicate_exists:
                    messages.error(
                        request,
                        'Another category already has this name.'
                    )
                else:
                    item.name = name
                    item.save()
                    messages.success(
                        request,
                        'Category updated successfully.'
                    )

        elif action == 'delete':
            if not category_id:
                messages.error(
                    request,
                    'No category was selected.'
                )
            else:
                item = get_object_or_404(
                    category,
                    id=category_id
                )

                if item.products.exists():
                    messages.error(
                        request,
                        'This category contains products. '
                        'Move or delete those products first.'
                    )
                else:
                    item.delete()
                    messages.success(
                        request,
                        'Category deleted successfully.'
                    )

        else:
            messages.error(
                request,
                'Invalid category action.'
            )

        return redirect('admin_category_list')

    categories = category.objects.all().order_by('name')

    return render(request, 'admin_categories.html', {
        'categories': categories,
    })


# Admin: Manage users
@login_required
def admin_user_list(request):
    if not is_admin_user(request.user):
        messages.error(
            request,
            'You are not allowed to access that page.'
        )
        return redirect('customer_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        user_id = request.POST.get('user_id', '').strip()

        if action == 'add':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password_confirm = request.POST.get(
                'password_confirm', ''
            )

            if not username or not password:
                messages.error(
                    request,
                    'Username and password are required.'
                )
            elif UserModel.objects.filter(
                username__iexact=username
            ).exists():
                messages.error(
                    request,
                    'That username is already taken.'
                )
            elif password != password_confirm:
                messages.error(
                    request,
                    'The passwords do not match.'
                )
            else:
                try:
                    validate_password(password)

                    new_user = UserModel.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                    )

                    customer_group, _ = Group.objects.get_or_create(
                        name='Customer'
                    )
                    new_user.groups.add(customer_group)

                    messages.success(
                        request,
                        'User created successfully.'
                    )

                except ValidationError as error:
                    messages.error(
                        request,
                        ' '.join(error.messages)
                    )

        elif action == 'edit':
            if not user_id:
                messages.error(
                    request,
                    'No user was selected.'
                )
            else:
                user = get_object_or_404(
                    UserModel,
                    id=user_id
                )

                username = request.POST.get(
                    'username', ''
                ).strip()
                email = request.POST.get(
                    'email', ''
                ).strip()
                first_name = request.POST.get(
                    'first_name', ''
                ).strip()
                last_name = request.POST.get(
                    'last_name', ''
                ).strip()

                if not username:
                    messages.error(
                        request,
                        'Username is required.'
                    )
                elif UserModel.objects.filter(
                    username__iexact=username
                ).exclude(id=user.id).exists():
                    messages.error(
                        request,
                        'That username is already taken.'
                    )
                else:
                    user.username = username
                    user.email = email
                    user.first_name = first_name
                    user.last_name = last_name

                    # Prevent an admin from deactivating themselves.
                    if user.id != request.user.id:
                        user.is_active = (
                            request.POST.get('is_active') == 'on'
                        )

                    user.save()
                    messages.success(
                        request,
                        'User updated successfully.'
                    )

        elif action == 'delete':
            if not user_id:
                messages.error(
                    request,
                    'No user was selected.'
                )
            else:
                user = get_object_or_404(
                    UserModel,
                    id=user_id
                )

                if user.id == request.user.id:
                    messages.error(
                        request,
                        'You cannot delete your own account.'
                    )
                elif user.is_superuser:
                    messages.error(
                        request,
                        'Superuser accounts cannot be deleted here.'
                    )
                else:
                    user.delete()
                    messages.success(
                        request,
                        'User deleted successfully.'
                    )

        else:
            messages.error(
                request,
                'Invalid user action.'
            )

        return redirect('admin_user_list')

    users = UserModel.objects.all().order_by('username')

    return render(request, 'admin_users.html', {
        'users': users,
    })
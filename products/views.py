from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, ProjectSetting


def validate_positive_amount(value):
    try:
        v = float(value)
        if v <= 0:
            raise ValueError
        return v
    except (TypeError, ValueError):
        return None


@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    if request.method == 'POST':
        amount = validate_positive_amount(request.POST.get('amount'))
        if amount is None:
            messages.error(request, 'Amount must be a positive number.')
            return redirect('products:add')
        p = Product(
            title   = request.POST.get('title'),
            amount  = amount,
            color   = request.POST.get('color', ''),
            size    = request.POST.get('size', ''),
            details = request.POST.get('details', ''),
        )
        if 'image' in request.FILES:
            p.image = request.FILES['image']
        p.save()
        messages.success(request, 'Product added.')
        return redirect('products:manage')
    return render(request, 'products/add.html')


@login_required
def manage_products(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    products = Product.objects.all()
    return render(request, 'products/manage.html', {'products': products})


@login_required
def edit_product(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        amount = validate_positive_amount(request.POST.get('amount'))
        if amount is None:
            messages.error(request, 'Amount must be a positive number.')
            return redirect('products:edit', pk=pk)
        product.title   = request.POST.get('title', product.title)
        product.amount  = amount
        product.color   = request.POST.get('color', product.color)
        product.size    = request.POST.get('size', product.size)
        product.details = request.POST.get('details', product.details)
        product.is_active = request.POST.get('is_active') == '1'
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated.')
        return redirect('products:manage')
    return render(request, 'products/edit.html', {'product': product})


@login_required
@require_POST
def toggle_product_status(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    return JsonResponse({'status': product.is_active})


@login_required
def project_settings(request):
    if not request.user.is_staff:
        return redirect('dashboard:index')
    settings_list = ProjectSetting.objects.all()
    if request.method == 'POST':
        for s in settings_list:
            s.title  = request.POST.get(f'title_{s.id}', s.title)
            s.amount = request.POST.get(f'amount_{s.id}', s.amount)
            s.mark   = request.POST.get(f'mark_{s.id}', s.mark)
            s.reward = request.POST.get(f'reward_{s.id}', s.reward)
            s.status = request.POST.get(f'status_{s.id}') == 'on'
            s.save()
        messages.success(request, 'Settings saved.')
        return redirect('products:settings')
    return render(request, 'products/settings.html', {'settings_list': settings_list})

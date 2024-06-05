from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UAV, RentalRecord
from .forms import UAVForm, SignUpForm, RentalRecordForm, UAVFilterForm, RentalRecordForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


def home_view(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('uav_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})




def uav_list(request):
    brands = UAV.objects.values_list('brand', flat=True).distinct()
    models = UAV.objects.values_list('model', flat=True).distinct()
    categories = UAV.objects.values_list('category', flat=True).distinct()
    uavs = UAV.objects.all()

    # Filtreleme işlemleri
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    min_weight = request.GET.get('min_weight')
    max_weight = request.GET.get('max_weight')
    category = request.GET.get('category')

    if brand:
        uavs = uavs.filter(brand=brand)
    if model:
        uavs = uavs.filter(model=model)
    if min_weight:
        uavs = uavs.filter(weight__gte=min_weight)
    if max_weight:
        uavs = uavs.filter(weight__lte=max_weight)
    if category:
        uavs = uavs.filter(category=category)

    uav_data = {brand: list(UAV.objects.filter(brand=brand).values_list('model', flat=True)) for brand in brands}
    
    context = {
        'brands': brands,
        'models': models,
        'categories': categories,
        'uavs': uavs,
        'uav_data': uav_data,
    }
    return render(request, 'uav_list.html', context)

def is_admin(user):
    return user.is_staff

@login_required
def uav_create(request):
    if not is_admin(request.user):
        messages.error(request, "Bu işlemi sadece yöneticiler gerçekleştirebilir.")
        return redirect('uav_list')
    if request.method == 'POST':
        form = UAVForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('uav_list')
    else:
        form = UAVForm()
    return render(request, 'uav_form.html', {'form': form})

@login_required
def uav_update(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Bu işlemi sadece yöneticiler gerçekleştirebilir.")
        return redirect('uav_list')
    uav = get_object_or_404(UAV, pk=pk)
    if request.method == 'POST':
        form = UAVForm(request.POST, instance=uav)
        if form.is_valid():
            form.save()
            return redirect('uav_list')
    else:
        form = UAVForm(instance=uav)
    return render(request, 'uav_form.html', {'form': form})

@login_required
def uav_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Bu işlemi sadece yöneticiler gerçekleştirebilir.")
        return redirect('uav_list')
    uav = get_object_or_404(UAV, pk=pk)
    if request.method == 'POST':
        uav.delete()
        return redirect('uav_list')
    return render(request, 'uav_confirm_delete.html', {'uav': uav})

@login_required
def rental_list(request):
    rentals = RentalRecord.objects.filter(member=request.user)
    formatted_rentals = []
    for rental in rentals:
        formatted_rentals.append({
            'uav': rental.uav,
            'rental_date': rental.rental_date.strftime('%Y-%m-%d %H:%M'),
            'return_date': rental.return_date.strftime('%Y-%m-%d %H:%M') if rental.return_date else ''
        })
    return render(request, 'rental_list.html', {'rentals': formatted_rentals})

@login_required
def rental_create(request, uav_id=None):
    if request.method == 'POST':
        form = RentalRecordForm(request.POST)
        if form.is_valid():
            rental_date = form.cleaned_data['rental_date']
            return_date = form.cleaned_data['return_date']
            uav = form.cleaned_data['uav']
            four_hours = timedelta(hours=4)

            # Çakışan kiralamaları kontrolü
            overlapping_rentals = RentalRecord.objects.filter(
                Q(uav=uav) &
                (
                    Q(rental_date__lte=rental_date, return_date__gte=rental_date - four_hours) |
                    Q(rental_date__lte=return_date + four_hours, return_date__gte=return_date)
                )
            )
            if overlapping_rentals.exists():
                messages.error(request, "Seçtiğiniz tarihlerde başka bir kiralama mevcut. Lütfen 4 saatlik bir aralık bırakın. Kiralama listesinden IHA'ların meşguliyetini görüntüleyebilirsiniz.")
            else:
                rental = form.save(commit=False)
                rental.member = request.user
                rental.save()
                return redirect('rental_list')
    else:
        initial_data = {}
        if uav_id:
            uav = get_object_or_404(UAV, id=uav_id)
            initial_data['uav'] = uav
        form = RentalRecordForm(initial=initial_data)
    return render(request, 'rental_form.html', {'form': form})

def rental_create_with_uav(request, uav_id):
    uav = get_object_or_404(UAV, pk=uav_id)
    if request.method == 'POST':
        form = RentalRecordForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.uav = uav
            rental.member = request.user 
            rental.save()
            return redirect('rental_list')
    else:
        form = RentalRecordForm(initial={'uav': uav})
    return render(request, 'rental_form.html', {'form': form, 'uav': uav})



def uav_details(request, uav_id):
    uav = get_object_or_404(UAV, id=uav_id)
    data = {
        'brand': uav.brand,
        'model': uav.model,
        'weight': uav.weight,
        'category': uav.category
    }
    return JsonResponse(data)


def get_models(request):
    brand = request.GET.get('brand')
    models = UAV.objects.filter(brand=brand).values_list('model', flat=True).distinct()
    return JsonResponse({'models': list(models)})

def get_models_by_brand(request):
    brand = request.GET.get('brand')
    models = UAV.objects.filter(brand=brand).values_list('model', flat=True).distinct()
    return JsonResponse(list(models), safe=False)

def rental_form_with_uav(request, uav_id):
    uav = get_object_or_404(UAV, id=uav_id)
    if request.method == 'POST':
        form = RentalRecordForm(request.POST)
        if form.is_valid():
            rental_record = form.save(commit=False)
            rental_record.uav = uav
            rental_record.save()
            return redirect('rental_list')
    else:
        form = RentalRecordForm()
    return render(request, 'rental_form.html', {'form': form, 'uav': uav})

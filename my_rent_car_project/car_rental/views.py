from django.shortcuts import render,get_object_or_404, redirect
from django.http import JsonResponse,HttpResponseForbidden
from django.contrib import messages
from .models import Car,Manufacturer,Loan,CarImage
import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from  datetime import datetime
from django.contrib.auth.decorators import login_required,user_passes_test
from django.utils import timezone
from django.db.models import Count, Q


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@superuser_required
def superuser_dashboard(request):
    return render(request, 'car_rental/superuser_dashboard.html')

@login_required
def main_page(request):
    return render(request, 'car_rental/main_page.html')

@login_required
def get_all_cars(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cars = Car.objects.all().order_by('id')
    return render(request, 'car_rental/cars_list.html', {'cars': cars})

@login_required
def search_car(request):
    model_query = request.GET.get('model', '')
    year_query = request.GET.get('year', '')
    transmission_query = request.GET.get('transmission', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    available_query = request.GET.get('available', '')

    filters = Q()

    if model_query:
        filters &= Q(model__icontains=model_query)

    if year_query:
        filters &= Q(year=year_query)

    if transmission_query:
        filters &= Q(transmission__iexact=transmission_query)

    if min_price:
        filters &= Q(price_per_day_usd__gte=min_price)

    if max_price:
        filters &= Q(price_per_day_usd__lte=max_price)

    if available_query:
        if available_query.lower() in ['true', '1']:
            filters &= Q(available=True)
        elif available_query.lower() in ['false', '0']:
            filters &= Q(available=False)

    cars = Car.objects.filter(filters).select_related('manufacturer', 'image')

    result = []
    for car in cars:
        image_url = ''
        if hasattr(car, 'image') and car.image:
            image_url = car.image.image.url

        result.append({
            "id": car.id,
            "manufacturer": car.manufacturer.name,
            "model": car.model,
            "year": car.year,
            "transmission": car.transmission,
            "price_per_day_usd": str(car.price_per_day_usd),
            "available": car.available,
            "image_url": image_url,
        })

    return JsonResponse(result, safe=False)

@login_required
def car_search_page(request):
    return render(request, 'car_rental/car_search.html')

@superuser_required
def add_car(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            manufacturer_name = data.get('manufacturer_name')
            if not manufacturer_name:
                return JsonResponse({"detail": "Manufacturer name is required."}, status=400)
            manufacturer = Manufacturer.objects.filter(name=manufacturer_name).first()
            if not manufacturer:
                return JsonResponse({"detail": "Manufacturer not found."}, status=404)
            price_str = data.get('price_per_day_usd')
            if not price_str:
                return JsonResponse({"detail": "Price is required."}, status=400)
            price_decimal = Decimal(price_str)
            car = Car.objects.create(
                manufacturer=manufacturer,
                model=data.get('model'),
                year=data.get('year'),
                transmission=data.get('transmission'),
                price_per_day_usd=price_decimal,
                available=True
            )
            return JsonResponse({"message": "Car added successfully."})
        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=500)
    else:
        return JsonResponse({"detail": "Method not allowed."}, status=405)

@superuser_required
def add_car_page(request):
    return render(request, 'car_rental/add_car.html')

@superuser_required
def delete_car_graphic(request):
    message = ''
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        try:
            pk = int(car_id)
            car = Car.objects.get(pk=pk)
            if car.available:
                car.delete()
                message = f'Car with ID {pk} was successfully deleted.'
            else:
                message = 'Cannot delete this car because is rented.'
        except ValueError:
            message = 'Please enter a valid numeric ID.'
        except Car.DoesNotExist:
            message = 'No car found with that ID.'
    return render(request, 'car_rental/delete_car_form.html', {'message': message})

@login_required
def list_manufacturers(request):
    manufacturers = Manufacturer.objects.all().order_by('name')
    return render(request, 'car_rental/manufacturers_list.html', {'manufacturers': manufacturers})

@superuser_required
def delete_manufacturer_form(request):
    message = ''
    if request.method == 'POST':
        name_to_delete = request.POST.get('name')
        if name_to_delete:
            try:
                manufacturer = Manufacturer.objects.get(name=name_to_delete)
                manufacturer.delete()
                message = f"Manufacturer '{name_to_delete}' was successfully deleted."
            except Manufacturer.DoesNotExist:
                message = f"No manufacturer found with name '{name_to_delete}'."
        else:
            message = 'Please enter a name.'
    return render(request, 'car_rental/delete_manufacturer.html', {'message': message})

@superuser_required
def add_manufacturer(request):
    message = ''
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        country = request.POST.get('country', '').strip()
        founded_date = request.POST.get('founded_date', '').strip()
        global_sales_input = request.POST.get('global_sales', '').strip()

        if not name:
            message = "Please enter the name of the manufacturer."
            return render(request, 'car_rental/add_manufacturer.html', {'message': message})

        if Manufacturer.objects.filter(name=name).exists():
            message = "A manufacturer with this name already exists."
            return render(request, 'car_rental/add_manufacturer.html', {'message': message})

        if global_sales_input == '':
            global_sales = 0.0
        else:
            try:
                global_sales = float(global_sales_input)
            except ValueError:
                message = "Please enter a valid number for Global Sales."
                return render(request, 'car_rental/add_manufacturer.html', {'message': message})

        manufacturer = Manufacturer(
            name=name,
            country=country,
            founded_date=founded_date if founded_date else None,
            global_sales=global_sales
        )
        manufacturer.save()

        message = f"Manufacturer '{name}' added successfully!"
    return render(request, 'car_rental/add_manufacturer.html', {'message': message})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if User.objects.filter(username=username).exists():
            message = "Username already exists."
            return render(request, 'car_rental/register.html', {'message': message})

        if User.objects.filter(email=email).exists():
            message = "Email already exists."
            return render(request, 'car_rental/register.html', {'message': message})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        message = "User successfully registered."
        return render(request, 'car_rental/register.html', {'message': message})
    else:
        return render(request, 'car_rental/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Incorrect username or password.')
            return render(request, 'car_rental/login_page.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('superuser_dashboard')
            else:
                return redirect('main_page')
        else:
            messages.error(request, 'Incorrect username or password.DSS')
            return render(request, 'car_rental/login_page.html')

    return render(request, 'car_rental/login_page.html')

@login_required
def user_logout(request):
    logout(request)
    return render(request,'car_rental/logout.html')

@login_required()
def reset_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user_auth = authenticate(username=user.username, password=old_password)
        if user_auth is None:
            messages.error(request, 'Old password is incorrect.')
            return render(request, 'car_rental/reset_password.html')

        if old_password == new_password:
            messages.error(request, 'The new password cannot be the same as the old password.')
            return render(request, 'car_rental/reset_password.html')

        try:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been successfully changed. You have been logged out.')
            logout(request)
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
    return render(request, 'car_rental/reset_password.html')

@login_required
def rent_car(request):
    if request.method != 'POST':
        return render(request, 'car_rental/rent_car.html')
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return render(request, 'car_rental/rent_car.html')

    car_id = data.get('car_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')

    if not all([car_id, start_date_str, end_date_str]):
        return render(request, 'car_rental/rent_car.html', {'error': 'Missing required fields.'})

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return render(request, 'car_rental/rent_car.html', {'error': 'Invalid date format.'})

    if start_date > end_date:
        return render(request, 'car_rental/rent_car.html', {'error': 'Start date must be before end date.'})

    try:
        car = Car.objects.get(id=car_id)
    except Car.DoesNotExist:
        return render(request, 'car_rental/rent_car.html', {'error': 'Car not found.'})

    conflicting_rentals = Loan.objects.filter(
        car=car,
        rent_date__lte=end_date,
        return_date__gte=start_date
    )

    if conflicting_rentals.exists():
        return render(request, 'car_rental/rent_car.html',
                      {'error': 'This car is already rented for the selected period.'})

    if not car.available:
        return render(request, 'car_rental/rent_car.html', {'error': 'Car is not available.'})

    delta = end_date - start_date
    days = delta.days + 1
    total_price = days * car.price_per_day_usd

    car.available = False
    car.save()

    Loan.objects.create(
        car=car,
        user=request.user,
        rent_date=start_date,
        return_date=end_date,
        total_price=total_price
    )
    return render(request, 'car_rental/rent_car.html', {'message': 'You booked successfully!',
                                                                            'total_price': total_price})

@login_required
def return_car(request):
    if request.method == 'GET':
        return render(request, 'car_rental/return_car.html')
    elif request.method == 'POST':
        import json
        data = json.loads(request.body)
        car_id = data.get('car_id')

        username = request.user.username

        loan = Loan.objects.filter(car_id=car_id, returned=False).order_by('-rent_date').first()

        if not loan:
            return JsonResponse({'status': 'error', 'message': 'This car is not currently rented.'})

        if loan.user.username != username:
            return JsonResponse({'status': 'error', 'message': 'You did not rent this car.'})

        try:
            car = Car.objects.get(id=car_id)
            car.available = True
            car.save()
        except Car.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Car not found.'})

        loan.returned = True
        loan.save()

        return JsonResponse({'status': 'success', 'message': 'Car returned successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

@login_required
def my_rentals_view(request):
    rentals = Loan.objects.filter(user=request.user)
    today = timezone.now().date()
    return render(request, 'car_rental/my_rentals.html', {'rentals': rentals, 'today': today})

@superuser_required
def add_car_image(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        image_file = request.FILES.get('image')
        try:
            car = Car.objects.filter(id=car_id).first()
            if not car:
                return JsonResponse({"status": "error", "message": "Car ID does not exist."})

            if hasattr(car, 'image'):
                return JsonResponse({"status": "error", "message": "This car already has an image. Only one image per car is allowed."})

            CarImage.objects.create(car=car, image=image_file)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})

def add_image_page(request):
    return render(request, 'car_rental/add_image.html')

@superuser_required
def delete_images_by_id(request):
    message = ''
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        if car_id:
            try:
                car_id_int = int(car_id)
                car = get_object_or_404(Car, id=car_id_int)
                images_qs = CarImage.objects.filter(car=car)
                if images_qs.exists():
                    images_qs.delete()
                    message = f"All images for car ID {car_id} have been deleted."
                else:
                    message = f"No images found for car ID {car_id}."
            except ValueError:
                message = "Invalid ID."
            except:
                message = f"Car with ID {car_id} does not exist."
        else:
            message = "Please enter a valid ID."
    return render(request, 'car_rental/delete_images.html', {'message': message})


def get_top_rented_cars(limit=10):
    top_cars = Car.objects.annotate(
        rental_count=Count('loans')
    ).order_by('-rental_count')[:limit]
    return top_cars

@login_required
def top_cars_view(request):
    top_cars = get_top_rented_cars()
    return render(request, 'car_rental/top_cars.html', {'top_cars': top_cars})
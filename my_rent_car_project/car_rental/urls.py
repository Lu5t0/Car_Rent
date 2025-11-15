from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('superuser-dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('cars/', views.get_all_cars, name='get_all_cars'),
    path('cars/search/', views.search_car, name='search_car'),
    path('cars/add/', views.add_car, name='add_car'),
    path('car-search/', views.car_detail_page, name='car_detail_page'),
    path('add_car/', views.add_car_page, name='add_car_page'),
    path('car/delete/', views.delete_car_graphic, name='delete_car_graphic'),
    path('manufacturers/', views.list_manufacturers, name='list_manufacturers'),
    path('manufacturer/delete/', views.delete_manufacturer_form, name='delete_manufacturer_from'),
    path('manufacturer/add/', views.add_manufacturer, name='add_manufacturer'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('rent_car/', views.rent_car, name='rent_car'),
    path('return_car/', views.return_car, name='return_car'),
    path('logout/', views.user_logout, name='logout'),
    path('reset-passwords/', views.reset_password, name='reset_password'),
    path('my-rentals/', views.my_rentals_view, name='my_rentals'),
    path('add-image/', views.add_image_page, name='add_image'),
    path('api/add-car-image/', views.add_car_image, name='add_car_image'),
    path('delete-images/', views.delete_images_by_id, name='delete_images'),
    path('top-cars/', views.top_cars_view, name='top_cars'),
]

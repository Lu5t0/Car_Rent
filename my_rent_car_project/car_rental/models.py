from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone

class Manufacturer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100, null=False, blank=False,default='Unknown')
    founded_date = models.DateField(null=False, blank=False)
    global_sales = models.FloatField(null=False, blank=False)

    class Meta:
        db_table ='manufacturer'

    def __str__(self):
        return self.name

class Car(models.Model):
    id = models.AutoField(primary_key=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='cars')
    model = models.CharField(max_length=255)
    year = models.IntegerField(null=False, blank=False)
    transmission = models.CharField(max_length=50, null=True, blank=True)
    price_per_day_usd = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    available = models.BooleanField(default=True)

    class Meta:
        db_table = 'cars'

    def __str__(self):
        return f"{self.model} ({self.year})"

class Loan(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    returned = models.BooleanField(default=False)
    rent_date = models.DateField(default=date.today)
    return_date = models.DateField(default=timezone.now, blank=False, null=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        db_table = 'loans'


    def __str__(self):
        return f"Loan of {self.car} to {self.user} - Returned: {self.returned}"

class CarImage(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(upload_to='cars/')


    def __str__(self):
        return f"Image for Car ID {self.car_id}"
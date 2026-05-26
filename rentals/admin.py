from django.contrib import admin

# Register your models here.
from .models import Car, Booking


admin.site.register(Car)
admin.site.register(Booking)
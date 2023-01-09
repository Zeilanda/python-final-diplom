from django.contrib import admin
from backend.models import Customer, Provider, User


admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Provider)
# Register your models here.

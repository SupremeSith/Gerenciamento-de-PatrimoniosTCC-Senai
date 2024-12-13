from django.contrib import admin

# Register your models here.
from .models import Senai
from .models import Inventario
from .models import Sala


admin.site.register(Senai)
admin.site.register(Inventario)
admin.site.register(Sala)

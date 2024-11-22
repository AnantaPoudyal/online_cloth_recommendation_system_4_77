from django.contrib import admin
from viewer.models import create_user
# Register your models here.
class CreateUseer(admin.ModelAdmin):
    exclude = ('password',) 
    list_display = ('usernames', 'DOB','address')

admin.site.register(create_user, CreateUseer)

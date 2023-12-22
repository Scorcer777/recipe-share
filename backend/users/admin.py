from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('email',)
    list_filter = ('username', 'email')


admin.site.register(CustomUser, CustomUserAdmin)

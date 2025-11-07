from django.contrib import admin
from .models import People

@admin.register(People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ['id_number', 'name', 'email', 'phone', 'get_department']
    search_fields = ['id_number', 'name', 'email', 'phone']
    list_filter = ['department']
    ordering = ('name',)

    def get_department(self, obj):
        return obj.department.name if obj.department else '-'
    get_department.short_description = 'Department'

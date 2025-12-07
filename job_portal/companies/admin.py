from django.contrib import admin
from .models import Company

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'owner', 'location', 'email', 'created_at')
    list_display_links = ('company_name',)
    list_filter = ('created_at', 'location', 'owner')
    search_fields = ('company_name', 'owner__username', 'location')
    fields = ('owner', 'company_name', 'description', 'location', 'website', 'logo', 'email', 'phone_number')

admin.site.register(Company, CompanyAdmin)

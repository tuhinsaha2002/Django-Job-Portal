from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Applicant , Skill

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_active']
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('role',)}),)
    
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the name of the skill in the admin list view
    search_fields = ('name',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Applicant)

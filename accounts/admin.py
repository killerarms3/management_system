from django.contrib import admin
from .models import Organization, Title, Profile, UserProfile
from django.conf import settings

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'contact_person', 'is_active')
    
@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    pass    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user' ,'phone_number', 'address')
from django.contrib import admin
from .models import InsurancePlan, UserPreferences

@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    """Admin configuration for the InsurancePlan model."""
    list_display = ('name', 'provider', 'monthly_premium', 'deductible')
    list_filter = ('provider',)
    search_fields = ('name', 'provider')
    ordering = ('monthly_premium',)

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin configuration for the UserPreferences model."""
    list_display = ('session_id', 'zip_code', 'age', 'created_at')
    list_filter = ('zip_code',)
    search_fields = ('session_id',)
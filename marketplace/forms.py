from django import forms
from .models import UserPreferences

class BasicInformationForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['age', 'zip_code', 'current_insurance', 'coverage_start_date']
        widgets = {
            'coverage_start_date': forms.DateInput(attrs={'type': 'date'}),
            'current_insurance': forms.CheckboxInput(),
        }

class HealthcareNeedsForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = [
            'doctor_visit_frequency',
            'has_medical_conditions',
            'needs_prescription_coverage',
            'planned_procedures',
            'needs_specialist_visits'
        ]
        widgets = {
            'planned_procedures': forms.Textarea(attrs={'rows': 3}),
            'has_medical_conditions': forms.CheckboxInput(),
            'needs_prescription_coverage': forms.CheckboxInput(),
            'needs_specialist_visits': forms.CheckboxInput(),
        }

class CoveragePreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = [
            'max_monthly_premium',
            'preferred_deductible',
            'preferred_max_out_of_pocket',
            'desired_benefits'
        ]
        widgets = {
            'max_monthly_premium': forms.NumberInput(attrs={'min': '0', 'step': '50'}),
            'preferred_deductible': forms.NumberInput(attrs={'min': '0', 'step': '100'}),
            'preferred_max_out_of_pocket': forms.NumberInput(attrs={'min': '0', 'step': '100'}),
            'desired_benefits': forms.JSONInput(),
        }

class ProviderPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = [
            'preferred_providers',
            'preferred_hospitals',
            'preferred_pharmacies'
        ]
        widgets = {
            'preferred_providers': forms.Textarea(attrs={'rows': 3}),
            'preferred_hospitals': forms.Textarea(attrs={'rows': 3}),
            'preferred_pharmacies': forms.Textarea(attrs={'rows': 3}),
        }
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from django.utils import timezone

# Insurance Plan Model
class InsurancePlan(models.Model):
    """
    Represents an individual health insurance plan offered by a provider.
    """
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    monthly_premium = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    deductible = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    out_of_pocket_max = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    network_info = models.TextField(
        help_text="Detailed information about the provider network"
    )
    prescription_coverage = models.TextField(
        help_text="Description of prescription drug coverage and tiers"
    )
    benefits = models.JSONField(
        help_text="JSON object containing covered benefits and their details"
    )
    additional_features = models.TextField(
        blank=True, help_text="Any additional plan features or benefits"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['monthly_premium', 'provider']
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['monthly_premium']),
        ]

    def __str__(self):
        return f"{self.provider} - {self.name}"

    def get_annual_cost_estimate(self, utilization_level='medium'):
        annual_premium = float(self.monthly_premium) * 12
        utilization_multipliers = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }
        multiplier = utilization_multipliers.get(utilization_level, 0.6)
        estimated_out_of_pocket = float(self.deductible) * multiplier
        return annual_premium + estimated_out_of_pocket

    def get_coverage_summary(self):
        return {
            'monthly_cost': self.monthly_premium,
            'yearly_cost': self.monthly_premium * 12,
            'deductible': self.deductible,
            'max_out_of_pocket': self.out_of_pocket_max,
            'key_benefits': list(self.benefits.keys())
        }

class UserPreferences(models.Model):
    """
    Represents the preferences and healthcare needs of a user.
    """
    VISIT_FREQUENCY_CHOICES = [
        ('rarely', 'Rarely (0-1 times per year)'),
        ('occasionally', 'Occasionally (2-3 times per year)'),
        ('regularly', 'Regularly (4-6 times per year)'),
        ('frequently', 'Frequently (7+ times per year)')
    ]

    session_id = models.CharField(max_length=100, unique=True, help_text="Session identifier for anonymous users")
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    zip_code = models.CharField(max_length=5, default='00000', help_text="5-digit ZIP code for location-based results")
    current_insurance = models.BooleanField(default=False, help_text="Whether the user currently has insurance")
    coverage_start_date = models.DateField(help_text="Desired start date for new coverage", default=timezone.now)
    doctor_visit_frequency = models.CharField(
        max_length=20, choices=VISIT_FREQUENCY_CHOICES, default='occasionally',
        help_text="How often the user typically visits doctors"
    )
    has_medical_conditions = models.BooleanField(default=False)
    needs_prescription_coverage = models.BooleanField(default=False)
    planned_procedures = models.TextField(blank=True)
    needs_specialist_visits = models.BooleanField(default=False)
    max_monthly_premium = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    preferred_deductible = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    preferred_max_out_of_pocket = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )
    desired_benefits = models.JSONField(
        default=list, help_text="JSON array of desired benefits and coverage features"
    )
    preferred_providers = models.TextField(blank=True)
    preferred_hospitals = models.TextField(blank=True)
    preferred_pharmacies = models.TextField(blank=True)
    selected_plans = models.ManyToManyField(
        InsurancePlan, blank=True, related_name='interested_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "User Preferences"
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['zip_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Preferences for session {self.session_id}"

    def get_provider_list(self):
        return [p.strip() for p in self.preferred_providers.split('\n') if p.strip()]

    def get_hospital_list(self):
        return [h.strip() for h in self.preferred_hospitals.split('\n') if h.strip()]

    def get_pharmacy_list(self):
        return [p.strip() for p in self.preferred_pharmacies.split('\n') if p.strip()]

    def get_benefits_list(self):
        try:
            return json.loads(self.desired_benefits)
        except json.JSONDecodeError:
            return []
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import InsurancePlan, UserPreferences
from decimal import Decimal
import json

def home(request):
    return render(request, 'marketplace/home.html')

def preferences(request):
    # Initialize session variables if not set
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid.uuid4())
    if 'pref_step' not in request.session:
        request.session['pref_step'] = 1  # Start at step 1

    current_step = request.session['pref_step']

    if request.method == 'POST':
        try:
            data = handle_step_submission(request, current_step, request.session['session_id'])

            if data.get('success'):
                # Move to the next step
                if current_step < 4:
                    request.session['pref_step'] = current_step + 1
                    return redirect(f'marketplace:preferences_step_{request.session["pref_step"]}')
                else:
                    create_or_update_user_preferences(request, request.session['session_id'])
                    return redirect('marketplace:compare')

        except ValidationError as e:
            messages.error(request, str(e))

    context = get_step_context(current_step, request.session)
    return render(request, f'marketplace/preferences/step_{current_step}.html', context)

def preferences_back_button(request):
    if 'pref_step' in request.session and request.session['pref_step'] > 1:
        request.session['pref_step'] -= 1
        return redirect(f'marketplace:preferences_step_{request.session["pref_step"]}')
    return redirect('marketplace:home')

def handle_step_submission(request, step, session_id):
    if step == 1:
        data = {
            'age': request.POST.get('age'),
            'zip_code': request.POST.get('zip_code'),
            'coverage_start_date': request.POST.get('coverage_start_date'),
            'current_insurance': request.POST.get('current_insurance') == 'on'
        }
        if not all([data['age'], data['zip_code'], data['coverage_start_date']]):
            raise ValidationError('All fields are required')
        request.session['basic_info'] = data
        return {'success': True}

    elif step == 2:
        data = {
            'doctor_visit_frequency': request.POST.get('doctor_visit_frequency'),
            'has_medical_conditions': request.POST.get('has_medical_conditions') == 'on',
            'needs_prescription_coverage': request.POST.get('needs_prescription_coverage') == 'on',
            'planned_procedures': request.POST.get('planned_procedures'),
            'needs_specialist_visits': request.POST.get('needs_specialist_visits') == 'on'
        }
        request.session['healthcare_needs'] = data
        return {'success': True}

    elif step == 3:
        data = {
            'max_monthly_premium': request.POST.get('max_monthly_premium'),
            'preferred_deductible': request.POST.get('preferred_deductible'),
            'preferred_max_out_of_pocket': request.POST.get('preferred_max_out_of_pocket'),
            'desired_benefits': request.POST.getlist('desired_benefits')
        }
        if not data['max_monthly_premium']:
            raise ValidationError('Please specify your maximum monthly premium')
        request.session['coverage_prefs'] = data
        return {'success': True}

    elif step == 4:
        data = {
            'preferred_providers': request.POST.getlist('preferred_providers'),
            'preferred_hospitals': request.POST.getlist('preferred_hospitals'),
            'preferred_pharmacies': request.POST.getlist('preferred_pharmacies')
        }
        request.session['provider_prefs'] = data
        return {'success': True}

def get_step_context(step, session):
    context = {'step': step}
    if step == 1:
        context['basic_info'] = session.get('basic_info', {})
    elif step == 2:
        context['healthcare_needs'] = session.get('healthcare_needs', {})
    elif step == 3:
        context['coverage_prefs'] = session.get('coverage_prefs', {})
        context['benefit_options'] = [
            'Dental', 'Vision', 'Mental Health', 'Maternity', 'Prescription Drug',
            'Specialist Visits', 'Emergency Services', 'Hospitalization'
        ]
    elif step == 4:
        context['provider_prefs'] = session.get('provider_prefs', {})
    return context

def create_or_update_user_preferences(request, session_id):
    basic_info = request.session.get('basic_info', {})
    healthcare_needs = request.session.get('healthcare_needs', {})
    coverage_prefs = request.session.get('coverage_prefs', {})
    provider_prefs = request.session.get('provider_prefs', {})

    try:
        user_prefs = UserPreferences.objects.get(session_id=session_id)
        # Update existing preferences
        user_prefs.age = basic_info.get('age')
        user_prefs.zip_code = basic_info.get('zip_code')
        user_prefs.current_insurance = basic_info.get('current_insurance', False)
        user_prefs.coverage_start_date = basic_info.get('coverage_start_date')
        user_prefs.doctor_visit_frequency = healthcare_needs.get('doctor_visit_frequency')
        user_prefs.has_medical_conditions = healthcare_needs.get('has_medical_conditions', False)
        user_prefs.needs_prescription_coverage = healthcare_needs.get('needs_prescription_coverage', False)
        user_prefs.planned_procedures = healthcare_needs.get('planned_procedures', '')
        user_prefs.needs_specialist_visits = healthcare_needs.get('needs_specialist_visits', False)
        user_prefs.max_monthly_premium = coverage_prefs.get('max_monthly_premium')
        user_prefs.preferred_deductible = coverage_prefs.get('preferred_deductible')
        user_prefs.preferred_max_out_of_pocket = coverage_prefs.get('preferred_max_out_of_pocket')
        user_prefs.desired_benefits = json.dumps(coverage_prefs.get('desired_benefits', []))
        user_prefs.preferred_providers = '\n'.join(provider_prefs.get('preferred_providers', []))
        user_prefs.preferred_hospitals = '\n'.join(provider_prefs.get('preferred_hospitals', []))
        user_prefs.preferred_pharmacies = '\n'.join(provider_prefs.get('preferred_pharmacies', []))
        user_prefs.save()
    except UserPreferences.DoesNotExist:
        # Create new preferences
        UserPreferences.objects.create(
            session_id=session_id,
            age=basic_info.get('age'),
            zip_code=basic_info.get('zip_code'),
            current_insurance=basic_info.get('current_insurance', False),
            coverage_start_date=basic_info.get('coverage_start_date'),
            doctor_visit_frequency=healthcare_needs.get('doctor_visit_frequency'),
            has_medical_conditions=healthcare_needs.get('has_medical_conditions', False),
            needs_prescription_coverage=healthcare_needs.get('needs_prescription_coverage', False),
            planned_procedures=healthcare_needs.get('planned_procedures', ''),
            needs_specialist_visits=healthcare_needs.get('needs_specialist_visits', False),
            max_monthly_premium=coverage_prefs.get('max_monthly_premium'),
            preferred_deductible=coverage_prefs.get('preferred_deductible'),
            preferred_max_out_of_pocket=coverage_prefs.get('preferred_max_out_of_pocket'),
            desired_benefits=json.dumps(coverage_prefs.get('desired_benefits', [])),
            preferred_providers='\n'.join(provider_prefs.get('preferred_providers', [])),
            preferred_hospitals='\n'.join(provider_prefs.get('preferred_hospitals', [])),
            preferred_pharmacies='\n'.join(provider_prefs.get('preferred_pharmacies', []))
        )

def compare_plans(request):
    try:
        user_prefs = UserPreferences.objects.get(session_id=request.session['session_id'])
        plans = InsurancePlan.objects.all()
        filtered_plans = filter_plans(plans, user_prefs)
        sorted_plans = sort_plans_by_match(filtered_plans, user_prefs)

        context = {
            'plans': sorted_plans,
            'preferences': user_prefs,
            'total_plans': len(sorted_plans)
        }
    except ObjectDoesNotExist:
        context = {
            'error': 'Please complete your preferences first',
            'plans': [],
            'total_plans': 0
        }
    return render(request, 'marketplace/compare.html', context)

def filter_plans(plans, preferences):
    filtered_plans = plans
    if preferences.max_monthly_premium:
        filtered_plans = filtered_plans.filter(
            monthly_premium__lte=preferences.max_monthly_premium
        )
    if preferences.preferred_deductible:
        max_deductible = Decimal(preferences.preferred_deductible) * Decimal('1.2')
        filtered_plans = filtered_plans.filter(
            deductible__lte=max_deductible
        )
    if preferences.preferred_max_out_of_pocket:
        filtered_plans = filtered_plans.filter(
            out_of_pocket_max__lte=preferences.preferred_max_out_of_pocket
        )
    return filtered_plans

def sort_plans_by_match(plans, preferences):
    scored_plans = []
    desired_benefits = json.loads(preferences.desired_benefits)

    for plan in plans:
        score = calculate_match_score(plan, preferences, desired_benefits)
        scored_plans.append({
            'plan': plan,
            'match_score': score,
            'matched_benefits': get_matched_benefits(plan, desired_benefits)
        })

    return sorted(scored_plans, key=lambda x: x['match_score'], reverse=True)

def calculate_match_score(plan, preferences, desired_benefits):
    score = 0
    if preferences.max_monthly_premium:
        premium_ratio = float(plan.monthly_premium) / float(preferences.max_monthly_premium)
        if premium_ratio <= 1:
            score += 30 * (1 - (premium_ratio * 0.8))

    if preferences.preferred_deductible:
        deductible_ratio = float(plan.deductible) / float(preferences.preferred_deductible)
        if deductible_ratio <= 1.2:
            score += 20 * (1 - (deductible_ratio * 0.7))

    if preferences.preferred_max_out_of_pocket:
        oop_ratio = float(plan.out_of_pocket_max) / float(preferences.preferred_max_out_of_pocket)
        if oop_ratio <= 1.2:
            score += 20 * (1 - (oop_ratio * 0.7))

    plan_benefits = plan.benefits.keys()
    matching_benefits = set(plan_benefits).intersection(desired_benefits)
    if desired_benefits:
        score += 30 * (len(matching_benefits) / len(desired_benefits))

    return min(score, 100)

def get_matched_benefits(plan, desired_benefits):
    plan_benefits = plan.benefits.keys()
    return list(set(plan_benefits).intersection(desired_benefits))

def plan_detail(request, plan_id):
    try:
        plan = InsurancePlan.objects.get(id=plan_id)
        user_prefs = UserPreferences.objects.get(session_id=request.session['session_id'])
        context = {
            'plan': plan,
            'preferences': user_prefs,
            'matched_benefits': get_matched_benefits(
                plan,
                json.loads(user_prefs.desired_benefits)
            )
        }
    except ObjectDoesNotExist:
        context = {
            'error': 'Plan not found or preferences not completed',
            'plan': None
        }
    return render(request, 'marketplace/plan_detail.html', context)
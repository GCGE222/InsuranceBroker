from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('preferences/', views.preferences, name='preferences'),
    path('preferences/step_1/', views.preferences, name='preferences_step_1'),
    path('preferences/step_2/', views.preferences, name='preferences_step_2'),
    path('preferences/step_3/', views.preferences, name='preferences_step_3'),
    path('preferences/step_4/', views.preferences, name='preferences_step_4'),
    path('preferences/back/', views.preferences_back_button, name='preferences_back_button'),
    path('compare/', views.compare_plans, name='compare'),
    path('plan/<int:plan_id>/', views.plan_detail, name='plan_detail'),
]
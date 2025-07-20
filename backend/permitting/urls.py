from django.urls import path
from . import views, api_views

app_name = 'permitting'

urlpatterns = [
    # Main application views
    path('', views.home, name='home'),
    path('property-lookup/', views.property_lookup, name='property_lookup'),
    path('permit-wizard/<int:property_id>/', views.permit_wizard, name='permit_wizard'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('applications/', views.applications_list, name='applications_list'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('advanced-compliance/', views.advanced_compliance_view, name='advanced_compliance'),
    
    # Original API endpoints (working)
    path('api/ask-question/', api_views.ask_planning_question, name='ask_question'),
    path('api/calculate-fees/', api_views.calculate_fees, name='calculate_fees'),
    path('api/check-compliance/', api_views.check_project_compliance, name='check_compliance'),
    path('api/search-properties/', api_views.search_properties, name='search_properties'),
    path('api/permit-requirements/<int:permit_type_id>/', api_views.get_permit_requirements, name='permit_requirements'),
]
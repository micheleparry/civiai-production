from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json

from .models import Property, PermitType, PermitApplication, ZoningRule
from .serializers import PropertySerializer, PermitApplicationSerializer


def home(request):
    """
    Home page - The main CiviAI interface
    """
    context = {
        'city_name': 'Shady Cove',
        'total_properties': Property.objects.count(),
        'active_applications': PermitApplication.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count(),
        'permit_types': PermitType.objects.filter(is_active=True),
    }
    return render(request, 'permitting/home.html', context)


def property_lookup(request):
    """
    Property lookup page - Start of the "TurboTax-style" guided intake
    """
    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        tax_lot = request.POST.get('tax_lot', '').strip()
        
        property_obj = None
        
        # Try to find property by address or tax lot
        if address:
            property_obj = Property.objects.filter(address__icontains=address).first()
        elif tax_lot:
            property_obj = Property.objects.filter(tax_lot_number=tax_lot).first()
        
        if property_obj:
            # Redirect to permit wizard with property ID
            return redirect('permit_wizard', property_id=property_obj.id)
        else:
            messages.error(request, 'Property not found. Please check the address or tax lot number.')
    
    return render(request, 'permitting/property_lookup.html')


def permit_wizard(request, property_id):
    """
    The main permit wizard - "TurboTax-style" guided intake
    """
    property_obj = get_object_or_404(Property, id=property_id)
    permit_types = PermitType.objects.filter(is_active=True)
    
    # Get applicable zoning rules for this property
    zoning_rules = ZoningRule.objects.filter(
        zoning_district=property_obj.zoning,
        is_active=True
    )
    
    context = {
        'property': property_obj,
        'permit_types': permit_types,
        'zoning_rules': zoning_rules,
    }
    
    if request.method == 'POST':
        # Process the permit application
        permit_type_id = request.POST.get('permit_type')
        applicant_name = request.POST.get('applicant_name')
        applicant_email = request.POST.get('applicant_email')
        applicant_phone = request.POST.get('applicant_phone')
        project_description = request.POST.get('project_description')
        project_value = request.POST.get('project_value')
        square_footage = request.POST.get('square_footage')
        
        if permit_type_id and applicant_name and applicant_email:
            permit_type = get_object_or_404(PermitType, id=permit_type_id)
            
            # Create the application
            application = PermitApplication.objects.create(
                property=property_obj,
                permit_type=permit_type,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone=applicant_phone or '',
                project_description=project_description or '',
                project_value=float(project_value) if project_value else None,
                square_footage=float(square_footage) if square_footage else None,
            )
            
            # Calculate fees
            application.calculate_fee()
            application.save()
            
            messages.success(request, f'Application {application.application_id} created successfully!')
            return redirect('application_detail', application_id=application.application_id)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'permitting/permit_wizard.html', context)


def application_detail(request, application_id):
    """
    Display details of a specific permit application
    """
    application = get_object_or_404(PermitApplication, application_id=application_id)
    
    context = {
        'application': application,
        'compliance_checks': application.compliance_checks.all(),
        'documents': application.documents.all(),
    }
    
    return render(request, 'permitting/application_detail.html', context)


def applications_list(request):
    """
    List all permit applications (for staff use)
    """
    applications = PermitApplication.objects.all().order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': PermitApplication.STATUS_CHOICES,
        'current_status': status_filter,
    }
    
    return render(request, 'permitting/applications_list.html', context)


# API Views for AJAX interactions

@api_view(['GET'])
def property_info_api(request, property_id):
    """
    API endpoint to get property information
    Used for real-time property data in the wizard
    """
    try:
        property_obj = Property.objects.get(id=property_id)
        serializer = PropertySerializer(property_obj)
        return Response(serializer.data)
    except Property.DoesNotExist:
        return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def calculate_fee_api(request):
    """
    API endpoint to calculate permit fees in real-time
    """
    permit_type_id = request.data.get('permit_type_id')
    project_value = request.data.get('project_value', 0)
    square_footage = request.data.get('square_footage', 0)
    
    try:
        permit_type = PermitType.objects.get(id=permit_type_id)
        
        base_fee = float(permit_type.base_fee)
        additional_fees = 0
        
        if square_footage and permit_type.per_square_foot_fee:
            additional_fees += float(square_footage) * float(permit_type.per_square_foot_fee)
        
        if project_value and permit_type.per_unit_fee:
            additional_fees += float(permit_type.per_unit_fee)
        
        total_fee = base_fee + additional_fees
        
        return Response({
            'base_fee': base_fee,
            'additional_fees': additional_fees,
            'total_fee': total_fee,
            'permit_type': permit_type.name
        })
    
    except PermitType.DoesNotExist:
        return Response({'error': 'Permit type not found'}, status=status.HTTP_404_NOT_FOUND)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid input values'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def compliance_check_api(request):
    """
    API endpoint for real-time compliance checking
    This is where the AI compliance engine will be integrated
    """
    property_id = request.data.get('property_id')
    permit_type_id = request.data.get('permit_type_id')
    project_data = request.data.get('project_data', {})
    
    try:
        property_obj = Property.objects.get(id=property_id)
        permit_type = PermitType.objects.get(id=permit_type_id)
        
        # Get applicable zoning rules
        zoning_rules = ZoningRule.objects.filter(
            zoning_district=property_obj.zoning,
            is_active=True
        )
        
        compliance_results = []
        
        # Basic compliance checks (this will be enhanced with AI)
        for rule in zoning_rules:
            result = {
                'rule_type': rule.rule_type,
                'rule_description': rule.rule_description,
                'status': 'PASS',  # Default to pass
                'message': 'Compliant',
                'details': ''
            }
            
            # Example: Check setback requirements
            if rule.rule_type == 'setback' and 'setbacks' in project_data:
                rule_params = rule.rule_parameters
                project_setbacks = project_data['setbacks']
                
                for side, required in rule_params.items():
                    if side in project_setbacks:
                        provided = float(project_setbacks[side])
                        if provided < required:
                            result['status'] = 'FAIL'
                            result['message'] = f'{side.title()} setback insufficient'
                            result['details'] = f'Required: {required} ft, Provided: {provided} ft'
                            break
            
            compliance_results.append(result)
        
        # Check for special overlays
        overlay_checks = []
        if property_obj.floodplain_overlay:
            overlay_checks.append({
                'rule_type': 'floodplain',
                'rule_description': 'FEMA Floodplain Requirements',
                'status': 'WARNING',
                'message': 'Property is in FEMA floodplain',
                'details': 'Additional floodplain development permits may be required'
            })
        
        if property_obj.riparian_overlay:
            overlay_checks.append({
                'rule_type': 'riparian',
                'rule_description': 'Riparian Buffer Requirements',
                'status': 'WARNING',
                'message': 'Property has riparian buffer requirements',
                'details': 'Development may be restricted near water features'
            })
        
        return Response({
            'property_address': property_obj.address,
            'zoning': property_obj.get_zoning_display(),
            'compliance_results': compliance_results,
            'overlay_checks': overlay_checks,
            'overall_status': 'PASS' if all(r['status'] == 'PASS' for r in compliance_results) else 'ISSUES_FOUND'
        })
    
    except (Property.DoesNotExist, PermitType.DoesNotExist):
        return Response({'error': 'Property or permit type not found'}, status=status.HTTP_404_NOT_FOUND)


def advanced_compliance_view(request):
    """
    Advanced compliance checking interface
    """
    return render(request, 'permitting/advanced_compliance.html')


def ai_assistant(request):
    """
    AI Assistant interface for staff
    """
    return render(request, 'permitting/ai_assistant.html')


def dashboard(request):
    """
    City Manager's Strategic Planning Dashboard
    """
    return render(request, 'permitting/dashboard.html')


def dashboard_stats_api(request):
    """
    API endpoint for dashboard statistics
    Used by the City Manager's Strategic Planning Dashboard
    """
    from django.db.models import Count, Sum
    from datetime import datetime, timedelta
    
    # Calculate date ranges
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Basic statistics
    stats = {
        'total_properties': Property.objects.count(),
        'total_applications': PermitApplication.objects.count(),
        'active_applications': PermitApplication.objects.filter(
            status__in=['SUBMITTED', 'UNDER_REVIEW']
        ).count(),
        'approved_this_month': PermitApplication.objects.filter(
            status='APPROVED',
            review_completed_at__gte=thirty_days_ago
        ).count(),
    }
    
    # Application breakdown by permit type
    permit_breakdown = list(
        PermitApplication.objects.values('permit_type__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Monthly fee collection (if fee tracking is implemented)
    monthly_fees = PermitApplication.objects.filter(
        fee_paid=True,
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('calculated_fee'))['total'] or 0
    
    # Compliance statistics
    compliance_stats = {
        'auto_approved': PermitApplication.objects.filter(
            compliance_check_passed=True,
            status='APPROVED'
        ).count(),
        'needs_review': PermitApplication.objects.filter(
            compliance_check_passed=False,
            status__in=['SUBMITTED', 'UNDER_REVIEW']
        ).count(),
    }
    
    return Response({
        'basic_stats': stats,
        'permit_breakdown': permit_breakdown,
        'monthly_fees': float(monthly_fees),
        'compliance_stats': compliance_stats,
        'generated_at': datetime.now().isoformat()
    })


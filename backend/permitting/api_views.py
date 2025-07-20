"""
API Views for CiviAI AI Assistant
Provides REST API endpoints for planning questions and compliance checking
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import models
import json

from .models import Property, PermitType, PermitApplication
from .ai_assistant import compliance_engine
from .serializers import PropertySerializer, PermitApplicationSerializer


@api_view(['POST'])
def ask_planning_question(request):
    """
    AI Co-Planner endpoint: Answer planning questions in real-time
    """
    try:
        data = request.data
        question = data.get('question', '')
        
        if not question:
            return Response({
                'error': 'Question is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get context if property is specified
        context = {}
        property_id = data.get('property_id')
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                context['property'] = property_obj
            except Property.DoesNotExist:
                pass
        
        # Get AI answer
        answer = compliance_engine.answer_planning_question(question, context)
        
        return Response({
            'question': question,
            'answer': answer,
            'timestamp': request.META.get('HTTP_DATE', ''),
            'context': {
                'property_address': context.get('property', {}).address if 'property' in context else None
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Error processing question: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def check_project_compliance(request):
    """
    Enhanced compliance checking with detailed AI analysis
    """
    try:
        data = request.data
        property_id = data.get('property_id')
        permit_type_id = data.get('permit_type_id')
        project_details = data.get('project_details', {})
        
        if not all([property_id, permit_type_id]):
            return Response({
                'error': 'Property ID and Permit Type ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get objects
        property_obj = get_object_or_404(Property, id=property_id)
        permit_type = get_object_or_404(PermitType, id=permit_type_id)
        
        # Run compliance check
        compliance_results = compliance_engine.check_project_compliance(
            property_obj, permit_type, project_details
        )
        
        # Calculate summary statistics
        total_checks = len(compliance_results)
        passed_checks = sum(1 for result in compliance_results if result['is_compliant'])
        compliance_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        
        # Determine overall status
        overall_status = "APPROVED" if passed_checks == total_checks else "NEEDS_REVIEW"
        if passed_checks < total_checks * 0.5:
            overall_status = "REJECTED"
        
        return Response({
            'property': PropertySerializer(property_obj).data,
            'permit_type': {
                'id': permit_type.id,
                'name': permit_type.name,
                'code': permit_type.code,
                'base_fee': float(permit_type.base_fee)
            },
            'compliance_results': compliance_results,
            'summary': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': total_checks - passed_checks,
                'compliance_rate': round(compliance_rate, 1),
                'overall_status': overall_status
            },
            'recommendations': _generate_recommendations(compliance_results, permit_type)
        })
        
    except Exception as e:
        return Response({
            'error': f'Error checking compliance: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_permit_requirements(request, permit_type_id):
    """
    Get detailed requirements for a specific permit type
    """
    try:
        permit_type = get_object_or_404(PermitType, id=permit_type_id)
        
        # Get general requirements based on permit type
        requirements = _get_permit_type_requirements(permit_type)
        
        return Response({
            'permit_type': {
                'id': permit_type.id,
                'name': permit_type.name,
                'code': permit_type.code,
                'description': permit_type.description,
                'base_fee': float(permit_type.base_fee),
                'requires_public_notice': permit_type.requires_public_notice,
                'requires_public_hearing': permit_type.requires_public_hearing,
                'can_auto_approve': permit_type.can_auto_approve
            },
            'requirements': requirements,
            'typical_review_time': _get_typical_review_time(permit_type),
            'required_documents': _get_required_documents(permit_type)
        })
        
    except Exception as e:
        return Response({
            'error': f'Error getting permit requirements: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def calculate_fees(request):
    """
    Calculate permit fees based on project details
    """
    try:
        data = request.data
        permit_type_id = data.get('permit_type_id')
        project_details = data.get('project_details', {})
        
        permit_type = get_object_or_404(PermitType, id=permit_type_id)
        
        # Calculate fees
        base_fee = float(permit_type.base_fee)
        additional_fees = _calculate_additional_fees(permit_type, project_details)
        total_fee = base_fee + additional_fees
        
        return Response({
            'permit_type': permit_type.name,
            'base_fee': base_fee,
            'additional_fees': additional_fees,
            'total_fee': total_fee,
            'fee_breakdown': _get_fee_breakdown(permit_type, project_details)
        })
        
    except Exception as e:
        return Response({
            'error': f'Error calculating fees: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_properties(request):
    """
    Search properties by address or tax lot number
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'error': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search by address or tax lot
        properties = Property.objects.filter(
            models.Q(address__icontains=query) | 
            models.Q(tax_lot_number__icontains=query)
        )[:10]  # Limit to 10 results
        
        return Response({
            'query': query,
            'results': PropertySerializer(properties, many=True).data,
            'count': properties.count()
        })
        
    except Exception as e:
        return Response({
            'error': f'Error searching properties: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Helper functions

def _generate_recommendations(compliance_results, permit_type):
    """Generate recommendations based on compliance results"""
    recommendations = []
    
    for result in compliance_results:
        if not result['is_compliant']:
            rule_name = result['rule_name'].lower()
            
            if 'setback' in rule_name:
                recommendations.append({
                    'type': 'SETBACK_VIOLATION',
                    'message': f"Consider redesigning to meet {result['rule_name']} requirement",
                    'suggestion': "You may need to reduce building size or request a variance"
                })
            elif 'height' in rule_name:
                recommendations.append({
                    'type': 'HEIGHT_VIOLATION',
                    'message': f"Reduce building height to comply with {result['rule_name']}",
                    'suggestion': "Consider single-story design or lower roof pitch"
                })
            elif 'coverage' in rule_name:
                recommendations.append({
                    'type': 'COVERAGE_VIOLATION',
                    'message': f"Reduce building footprint to meet {result['rule_name']}",
                    'suggestion': "Consider multi-story design or smaller building footprint"
                })
    
    if not recommendations:
        recommendations.append({
            'type': 'COMPLIANT',
            'message': 'Project meets all zoning requirements',
            'suggestion': 'Ready to proceed with permit application'
        })
    
    return recommendations


def _get_permit_type_requirements(permit_type):
    """Get requirements specific to permit type"""
    requirements = {
        'DECK': [
            'Building plans showing deck dimensions and attachment method',
            'Structural calculations if deck is over 200 sq ft',
            'Railing details if deck is over 30 inches high',
            'Setback compliance verification'
        ],
        'FENCE': [
            'Site plan showing fence location and height',
            'Property line verification',
            'Neighbor notification if fence is on property line',
            'Materials and design specifications'
        ],
        'ADD': [
            'Complete building plans and elevations',
            'Structural calculations',
            'Electrical and plumbing plans if applicable',
            'Energy compliance calculations'
        ],
        'SFR': [
            'Complete architectural plans',
            'Structural engineering plans',
            'Site plan with utilities',
            'Soils report',
            'Energy compliance report'
        ],
        'ADU': [
            'Building plans showing ADU layout',
            'Parking plan',
            'Utility connection plans',
            'Design compatibility analysis'
        ],
        'COM': [
            'Complete commercial building plans',
            'Traffic impact analysis',
            'Parking and loading analysis',
            'Landscape plan',
            'Sign plan if applicable'
        ]
    }
    
    return requirements.get(permit_type.code, ['Contact planning department for specific requirements'])


def _get_typical_review_time(permit_type):
    """Get typical review time for permit type"""
    review_times = {
        'DECK': '1-2 weeks',
        'FENCE': '1 week',
        'ADD': '2-3 weeks',
        'SFR': '3-4 weeks',
        'ADU': '2-3 weeks',
        'COM': '4-6 weeks'
    }
    
    return review_times.get(permit_type.code, '2-3 weeks')


def _get_required_documents(permit_type):
    """Get required documents for permit type"""
    documents = {
        'DECK': ['Site plan', 'Building plans', 'Structural details'],
        'FENCE': ['Site plan', 'Fence specifications'],
        'ADD': ['Building plans', 'Site plan', 'Structural plans'],
        'SFR': ['Architectural plans', 'Structural plans', 'Site plan', 'Utility plans'],
        'ADU': ['Building plans', 'Site plan', 'Parking plan'],
        'COM': ['Architectural plans', 'Site plan', 'Landscape plan', 'Traffic study']
    }
    
    return documents.get(permit_type.code, ['Contact planning department'])


def _calculate_additional_fees(permit_type, project_details):
    """Calculate additional fees based on project details"""
    additional_fees = 0.0
    
    # Square footage based fees for some permit types
    if permit_type.code in ['ADD', 'SFR', 'COM']:
        square_footage = float(project_details.get('square_footage', 0))
        if square_footage > 0:
            # $0.10 per square foot for additions and new construction
            additional_fees += square_footage * 0.10
    
    # Project value based fees
    project_value = float(project_details.get('project_value', 0))
    if project_value > 10000:
        # 0.5% of project value over $10,000
        additional_fees += (project_value - 10000) * 0.005
    
    return round(additional_fees, 2)


def _get_fee_breakdown(permit_type, project_details):
    """Get detailed fee breakdown"""
    breakdown = []
    
    breakdown.append({
        'item': f'{permit_type.name} Base Fee',
        'amount': float(permit_type.base_fee)
    })
    
    # Add square footage fees if applicable
    if permit_type.code in ['ADD', 'SFR', 'COM']:
        square_footage = float(project_details.get('square_footage', 0))
        if square_footage > 0:
            sqft_fee = square_footage * 0.10
            breakdown.append({
                'item': f'Square Footage Fee ({square_footage} sq ft @ $0.10/sq ft)',
                'amount': sqft_fee
            })
    
    # Add project value fees if applicable
    project_value = float(project_details.get('project_value', 0))
    if project_value > 10000:
        value_fee = (project_value - 10000) * 0.005
        breakdown.append({
            'item': f'Project Value Fee (0.5% of value over $10,000)',
            'amount': value_fee
        })
    
    return breakdown


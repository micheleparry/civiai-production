"""
Enhanced API Views for CiviAI with Claude Integration
Advanced AI capabilities for municipal planning
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import asyncio
from .models import Property, PermitType, PermitApplication, ZoningRule
from .ai_assistant import PlanningKnowledgeBase, ComplianceEngine
from .claude_service import claude_service
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def ask_planning_question_enhanced(request):
    """
    Enhanced Q&A with Claude integration for complex questions
    """
    try:
        data = request.data
        question = data.get('question', '')
        context = data.get('context', {})
        
        if not question:
            return Response({'error': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine if this is a complex question that needs Claude
        complex_keywords = [
            'variance', 'conditional use', 'environmental impact', 'statewide goals',
            'comprehensive plan', 'legal interpretation', 'precedent', 'appeal',
            'hearing', 'testimony', 'findings', 'conditions of approval'
        ]
        
        is_complex = any(keyword in question.lower() for keyword in complex_keywords)
        
        if is_complex:
            # Use Claude for complex questions
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    claude_service.ask_complex_question(question, context)
                )
                loop.close()
                
                if result['success']:
                    return Response({
                        'answer': result['answer'],
                        'source': 'Claude AI',
                        'model': result['model'],
                        'context_used': result.get('context_used', False),
                        'complexity': 'high'
                    })
                else:
                    # Fallback to local AI if Claude fails
                    assistant = PlanningAssistant()
                    answer = assistant.get_answer(question)
                    return Response({
                        'answer': answer,
                        'source': 'Local AI (Claude fallback)',
                        'complexity': 'high',
                        'note': 'Advanced AI temporarily unavailable, using local knowledge base'
                    })
            except Exception as e:
                logger.error(f"Claude API error: {str(e)}")
                # Fallback to local AI
                assistant = PlanningAssistant()
                answer = assistant.get_answer(question)
                return Response({
                    'answer': answer,
                    'source': 'Local AI (Claude fallback)',
                    'complexity': 'high',
                    'note': 'Advanced AI temporarily unavailable, using local knowledge base'
                })
        else:
            # Use local AI for simple questions (faster)
            assistant = PlanningAssistant()
            answer = assistant.get_answer(question)
            return Response({
                'answer': answer,
                'source': 'Local AI',
                'complexity': 'standard'
            })
            
    except Exception as e:
        logger.error(f"Error in ask_planning_question_enhanced: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_document(request):
    """
    Document analysis using Claude AI
    """
    try:
        data = request.data
        document_text = data.get('document_text', '')
        analysis_type = data.get('analysis_type', 'general')
        
        if not document_text:
            return Response({'error': 'Document text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use Claude for document analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            claude_service.analyze_document(document_text, analysis_type)
        )
        loop.close()
        
        if result['success']:
            return Response({
                'analysis': result['analysis'],
                'analysis_type': result['analysis_type'],
                'model': result['model'],
                'success': True
            })
        else:
            return Response({
                'error': result['error'],
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in analyze_document: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_staff_report(request):
    """
    Generate comprehensive staff report using Claude AI
    """
    try:
        data = request.data
        application_id = data.get('application_id')
        
        if not application_id:
            return Response({'error': 'Application ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use Claude to generate staff report
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            claude_service.generate_staff_report(application_id)
        )
        loop.close()
        
        if result['success']:
            return Response({
                'staff_report': result['staff_report'],
                'application_id': result['application_id'],
                'model': result['model'],
                'success': True
            })
        else:
            return Response({
                'error': result['error'],
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_staff_report: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def check_statewide_goals(request):
    """
    Check compliance with Oregon Statewide Planning Goals using Claude AI
    """
    try:
        data = request.data
        project_description = data.get('project_description', '')
        property_context = data.get('property_context', {})
        
        if not project_description:
            return Response({'error': 'Project description is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use Claude for statewide goals compliance check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            claude_service.check_statewide_goals_compliance(project_description, property_context)
        )
        loop.close()
        
        if result['success']:
            return Response({
                'compliance_analysis': result['compliance_analysis'],
                'goals_checked': result['goals_checked'],
                'model': result['model'],
                'success': True
            })
        else:
            return Response({
                'error': result['error'],
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in check_statewide_goals: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def advanced_compliance_check(request):
    """
    Perform advanced compliance checking with multiple levels
    """
    try:
        from .advanced_compliance import advanced_compliance_engine
        
        data = request.data
        property_id = data.get('property_id')
        permit_type_id = data.get('permit_type_id')
        project_details = data.get('project_details', {})
        compliance_level = data.get('compliance_level', 'COMPREHENSIVE')
        
        if not property_id or not permit_type_id:
            return Response({
                'error': 'property_id and permit_type_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Run advanced compliance check
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                advanced_compliance_engine.comprehensive_compliance_check(
                    property_id, permit_type_id, project_details, compliance_level
                )
            )
            loop.close()
            
            if result['success']:
                return Response({
                    'success': True,
                    'compliance_results': result['compliance_results']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in advanced compliance check: {str(e)}")
            return Response({
                'success': False,
                'error': f'Compliance check failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in advanced compliance endpoint: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_planning_document(request):
    """
    Analyze uploaded planning documents with Claude and MCP integration
    """
    try:
        from .document_analyzer import document_analyzer
        
        if 'document' not in request.FILES:
            return Response({
                'error': 'Document file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        document_file = request.FILES['document']
        analysis_type = request.POST.get('analysis_type', 'comprehensive')
        property_context = json.loads(request.POST.get('property_context', '{}'))
        
        # Run document analysis
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                document_analyzer.analyze_planning_document(
                    document_file, analysis_type, property_context
                )
            )
            loop.close()
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            return Response({
                'success': False,
                'error': f'Document analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in document analysis endpoint: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_site_plan(request):
    """
    Specialized analysis for site plans and architectural drawings
    """
    try:
        from .document_analyzer import document_analyzer
        
        if 'plan_file' not in request.FILES:
            return Response({
                'error': 'Plan file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan_file = request.FILES['plan_file']
        property_context = json.loads(request.POST.get('property_context', '{}'))
        
        # Run site plan analysis
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                document_analyzer.analyze_site_plan(plan_file, property_context)
            )
            loop.close()
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error in site plan analysis: {str(e)}")
            return Response({
                'success': False,
                'error': f'Site plan analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in site plan analysis endpoint: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def mcp_health_check(request):
    """
    Check MCP server health and connectivity
    """
    try:
        from .mcp_integration import mcp_service
        
        health_result = mcp_service.check_server_health()
        
        return Response({
            'success': True,
            'mcp_status': health_result
        })
        
    except Exception as e:
        logger.error(f"Error checking MCP health: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


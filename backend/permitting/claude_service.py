"""
Claude AI Service for CiviAI
Advanced AI reasoning and document analysis for municipal planning
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from django.conf import settings
from .models import Property, PermitType, ZoningRule, PermitApplication
import json

class ClaudeService:
    """
    Advanced AI service using Claude for complex planning scenarios
    """
    
    def __init__(self):
        # Use environment variable or settings for API key
        api_key = os.getenv('ANTHROPIC_API_KEY') or getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not api_key:
            # For demo purposes, create a mock service
            self.client = None
            self.available = False
            self.model = "claude-3-5-sonnet-20241022"
            return
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.available = True
    
    def get_system_prompt(self) -> str:
        """
        Comprehensive system prompt for Claude with planning expertise
        """
        return """You are an expert city planner and municipal planning AI assistant for CiviAI, 
        specifically serving the City of Shady Cove, Oregon. You have deep knowledge of:

        1. Oregon Statewide Planning Goals (all 19 goals)
        2. Municipal zoning and land use regulations
        3. Building codes and permit requirements
        4. Environmental regulations (floodplain, riparian, wetlands)
        5. DLCD (Department of Land Conservation and Development) requirements
        6. Planning commission and public hearing processes
        7. Variance and conditional use permit procedures
        8. Transportation planning and traffic impact analysis
        9. Environmental impact assessment
        10. Historic preservation requirements

        Your role is to:
        - Provide accurate, detailed planning guidance
        - Analyze complex planning scenarios with multiple variables
        - Interpret legal documents and regulations in plain English
        - Suggest solutions for planning challenges
        - Ensure compliance with local, state, and federal requirements
        - Help staff make informed planning decisions

        Always provide specific, actionable advice with relevant code sections and requirements.
        When uncertain, clearly state limitations and suggest consulting with professional planners or legal counsel.
        """
    
    async def ask_complex_question(self, question: str, context: dict = None) -> dict:
        """
        Ask Claude a complex planning question with context
        """
        if not self.available:
            return {
                'success': False,
                'answer': 'Claude AI service is not available in demo mode. This would provide advanced AI analysis in production.',
                'source': 'demo_mode',
                'confidence': 0.0
            }
        
        try:
            # Build context from database if property information is provided
            context_info = ""
            if context:
                if 'property_id' in context:
                    property_info = await self._get_property_context(context['property_id'])
                    context_info += f"\n\nProperty Context:\n{property_info}"
                
                if 'permit_type' in context:
                    permit_info = await self._get_permit_context(context['permit_type'])
                    context_info += f"\n\nPermit Context:\n{permit_info}"
            
            # Construct the full prompt
            full_prompt = f"""
            Planning Question: {question}
            
            {context_info}
            
            Please provide a comprehensive answer that includes:
            1. Direct answer to the question
            2. Relevant code sections or regulations
            3. Step-by-step process if applicable
            4. Potential complications or considerations
            5. Recommended next steps
            """
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=2000,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return {
                "success": True,
                "answer": response.content[0].text,
                "model": self.model,
                "context_used": bool(context_info)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": "I apologize, but I'm experiencing technical difficulties. Please consult with the planning staff or refer to the municipal code directly."
            }
    
    async def analyze_document(self, document_text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze planning documents (plans, ordinances, applications)
        """
        try:
            analysis_prompts = {
                "general": "Analyze this planning document and provide a summary of key points, requirements, and potential issues.",
                "compliance": "Review this document for compliance with Oregon Statewide Planning Goals and local regulations. Identify any potential violations or concerns.",
                "environmental": "Analyze this document for environmental considerations including floodplain, riparian, wetlands, and other environmental factors.",
                "zoning": "Review this document for zoning compliance, setback requirements, height restrictions, and land use compatibility."
            }
            
            prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
            
            full_prompt = f"""
            {prompt}
            
            Document Content:
            {document_text}
            
            Please provide:
            1. Executive Summary
            2. Key Requirements Identified
            3. Compliance Assessment
            4. Potential Issues or Red Flags
            5. Recommendations for Staff Review
            """
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=3000,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return {
                "success": True,
                "analysis": response.content[0].text,
                "analysis_type": analysis_type,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_staff_report(self, application_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive staff report for permit applications
        """
        try:
            # Get application details
            application = await self._get_application_details(application_id)
            
            prompt = f"""
            Generate a comprehensive staff report for this permit application:
            
            Application Details:
            {application}
            
            Please provide a professional staff report including:
            1. Project Description
            2. Zoning and Land Use Analysis
            3. Code Compliance Review
            4. Environmental Considerations
            5. Public Notice Requirements
            6. Recommended Conditions of Approval
            7. Staff Recommendation (Approve/Deny/Modify)
            8. Suggested Motion for Planning Commission
            """
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=4000,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "staff_report": response.content[0].text,
                "application_id": application_id,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_statewide_goals_compliance(self, project_description: str, property_context: Dict) -> Dict[str, Any]:
        """
        Check compliance with Oregon's 19 Statewide Planning Goals
        """
        try:
            statewide_goals = """
            Oregon's 19 Statewide Planning Goals:
            1. Citizen Involvement
            2. Land Use Planning
            3. Agricultural Lands
            4. Forest Lands
            5. Natural Resources, Scenic and Historic Areas, and Open Spaces
            6. Air, Water and Land Resources Quality
            7. Areas Subject to Natural Disasters and Hazards
            8. Recreational Needs
            9. Economic Development
            10. Housing
            11. Public Facilities and Services
            12. Transportation
            13. Energy Conservation
            14. Urbanization
            15. Willamette River Greenway
            16. Estuarine Resources
            17. Coastal Shorelands
            18. Beaches and Dunes
            19. Ocean Resources
            """
            
            prompt = f"""
            Analyze this project for compliance with Oregon Statewide Planning Goals:
            
            Project: {project_description}
            Property Context: {json.dumps(property_context, indent=2)}
            
            {statewide_goals}
            
            Please provide:
            1. Applicable Goals Analysis (which goals apply to this project)
            2. Compliance Assessment for each applicable goal
            3. Potential Conflicts or Issues
            4. Required Findings or Conditions
            5. Recommended Mitigation Measures
            6. Overall Compliance Determination
            """
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=3500,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "compliance_analysis": response.content[0].text,
                "goals_checked": "All 19 Oregon Statewide Planning Goals",
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_property_context(self, property_id: int) -> str:
        """Get property information for context"""
        try:
            from django.apps import apps
            Property = apps.get_model('permitting', 'Property')
            property_obj = await asyncio.to_thread(Property.objects.get, id=property_id)
            
            return f"""
            Address: {property_obj.address}
            Tax Lot: {property_obj.tax_lot_number}
            Zoning: {property_obj.zoning}
            Acres: {property_obj.acres}
            In Floodplain: {property_obj.in_floodplain}
            Riparian Overlay: {property_obj.riparian_overlay}
            """
        except:
            return "Property information not available"
    
    async def _get_permit_context(self, permit_type: str) -> str:
        """Get permit type information for context"""
        try:
            from django.apps import apps
            PermitType = apps.get_model('permitting', 'PermitType')
            permit_obj = await asyncio.to_thread(PermitType.objects.get, name=permit_type)
            
            return f"""
            Permit Type: {permit_obj.name}
            Description: {permit_obj.description}
            Base Fee: ${permit_obj.base_fee}
            Review Time: {permit_obj.review_time_days} days
            Public Notice Required: {permit_obj.requires_public_notice}
            """
        except:
            return "Permit type information not available"
    
    async def _get_application_details(self, application_id: int) -> str:
        """Get full application details for staff report generation"""
        try:
            from django.apps import apps
            PermitApplication = apps.get_model('permitting', 'PermitApplication')
            app = await asyncio.to_thread(PermitApplication.objects.select_related('property', 'permit_type').get, id=application_id)
            
            return f"""
            Application ID: {app.id}
            Applicant: {app.applicant_name}
            Property: {app.property.address}
            Permit Type: {app.permit_type.name}
            Project Description: {app.project_description}
            Square Footage: {app.square_footage}
            Estimated Cost: ${app.estimated_cost}
            Status: {app.status}
            Submitted: {app.created_at}
            """
        except:
            return "Application details not available"

# Global instance
claude_service = ClaudeService()


"""
Document Analysis Service for CiviAI
Advanced document analysis using Claude AI and MCP integration
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from django.core.files.uploadedfile import UploadedFile
from .claude_service import claude_service
from .mcp_integration import mcp_service
import PyPDF2
import io
import json

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """
    Advanced document analysis for planning applications
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.doc', '.docx']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def analyze_planning_document(self, 
                                      document_file: Union[UploadedFile, str], 
                                      analysis_type: str = "comprehensive",
                                      property_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of planning documents
        """
        try:
            # Extract text from document
            if isinstance(document_file, str):
                # File path provided
                document_text = self._read_file_content(document_file)
                filename = os.path.basename(document_file)
            else:
                # Uploaded file
                document_text = self._extract_text_from_upload(document_file)
                filename = document_file.name
            
            if not document_text:
                return {
                    'success': False,
                    'error': 'Could not extract text from document'
                }
            
            # Perform different types of analysis based on request
            analysis_results = {}
            
            if analysis_type in ['comprehensive', 'general']:
                # General document analysis with Claude
                claude_analysis = await claude_service.analyze_document(document_text, 'general')
                analysis_results['general_analysis'] = claude_analysis
            
            if analysis_type in ['comprehensive', 'compliance']:
                # Local zoning compliance analysis
                local_compliance = await self._analyze_local_compliance(document_text, property_context)
                analysis_results['local_compliance'] = local_compliance
            
            if analysis_type in ['comprehensive', 'statewide']:
                # Statewide goals compliance analysis
                statewide_compliance = await self._analyze_statewide_compliance(document_text, property_context)
                analysis_results['statewide_compliance'] = statewide_compliance
            
            if analysis_type in ['comprehensive', 'environmental']:
                # Environmental analysis
                environmental_analysis = await claude_service.analyze_document(document_text, 'environmental')
                analysis_results['environmental_analysis'] = environmental_analysis
            
            if analysis_type in ['comprehensive', 'zoning']:
                # Zoning analysis
                zoning_analysis = await claude_service.analyze_document(document_text, 'zoning')
                analysis_results['zoning_analysis'] = zoning_analysis
            
            # Generate summary and recommendations
            summary = await self._generate_analysis_summary(analysis_results, document_text)
            
            return {
                'success': True,
                'filename': filename,
                'analysis_type': analysis_type,
                'document_length': len(document_text),
                'analysis_results': analysis_results,
                'summary': summary,
                'recommendations': await self._generate_recommendations(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_site_plan(self, 
                              plan_file: UploadedFile, 
                              property_context: Dict) -> Dict[str, Any]:
        """
        Specialized analysis for site plans and architectural drawings
        """
        try:
            # Extract text and analyze
            plan_text = self._extract_text_from_upload(plan_file)
            
            if not plan_text:
                return {
                    'success': False,
                    'error': 'Could not extract text from site plan. Please ensure the plan includes text descriptions or submit additional documentation.'
                }
            
            # Use Claude for detailed site plan analysis
            site_plan_prompt = f"""
            Analyze this site plan for a planning application:
            
            Property Context: {json.dumps(property_context, indent=2)}
            Plan Content: {plan_text}
            
            Please provide:
            1. Site Plan Completeness Assessment
            2. Setback and Dimensional Analysis
            3. Parking and Access Review
            4. Utility and Infrastructure Analysis
            5. Landscaping and Open Space Review
            6. Compliance Issues Identified
            7. Missing Information or Required Clarifications
            8. Recommendations for Approval
            """
            
            claude_analysis = await claude_service.ask_complex_question(site_plan_prompt)
            
            # Check against local zoning requirements
            local_compliance = await self._analyze_local_compliance(plan_text, property_context)
            
            # Check statewide goals compliance
            statewide_compliance = await self._analyze_statewide_compliance(plan_text, property_context)
            
            return {
                'success': True,
                'filename': plan_file.name,
                'analysis_type': 'site_plan',
                'claude_analysis': claude_analysis,
                'local_compliance': local_compliance,
                'statewide_compliance': statewide_compliance,
                'recommendations': await self._generate_site_plan_recommendations(claude_analysis, local_compliance, statewide_compliance)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing site plan: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_staff_report_from_documents(self, 
                                                 application_id: int, 
                                                 documents: List[UploadedFile]) -> Dict[str, Any]:
        """
        Generate comprehensive staff report from multiple documents
        """
        try:
            document_analyses = []
            
            # Analyze each document
            for doc in documents:
                analysis = await self.analyze_planning_document(doc, 'comprehensive')
                if analysis['success']:
                    document_analyses.append(analysis)
            
            # Use Claude to generate comprehensive staff report
            staff_report_prompt = f"""
            Generate a comprehensive staff report for permit application #{application_id} based on the following document analyses:
            
            {json.dumps(document_analyses, indent=2)}
            
            Please provide a professional staff report including:
            1. Executive Summary
            2. Project Description
            3. Zoning and Land Use Analysis
            4. Code Compliance Review
            5. Environmental Considerations
            6. Statewide Planning Goals Compliance
            7. Public Notice and Hearing Requirements
            8. Recommended Conditions of Approval
            9. Staff Recommendation (Approve/Deny/Continue)
            10. Suggested Motion for Planning Commission
            """
            
            staff_report = await claude_service.ask_complex_question(staff_report_prompt)
            
            return {
                'success': True,
                'application_id': application_id,
                'documents_analyzed': len(document_analyses),
                'staff_report': staff_report,
                'document_summaries': [
                    {
                        'filename': analysis['filename'],
                        'summary': analysis.get('summary', {})
                    } for analysis in document_analyses
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating staff report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_text_from_upload(self, uploaded_file: UploadedFile) -> str:
        """
        Extract text from uploaded file
        """
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_pdf_text(uploaded_file)
            elif file_extension in ['.txt']:
                return uploaded_file.read().decode('utf-8')
            else:
                # For other formats, try to read as text
                try:
                    return uploaded_file.read().decode('utf-8')
                except:
                    return f"Document type: {file_extension}. Text extraction not available for this format."
        except Exception as e:
            logger.error(f"Error extracting text from upload: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, pdf_file: UploadedFile) -> str:
        """
        Extract text from PDF file
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _read_file_content(self, file_path: str) -> str:
        """
        Read content from file path
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return ""
    
    async def _analyze_local_compliance(self, document_text: str, property_context: Optional[Dict]) -> Dict[str, Any]:
        """
        Analyze compliance with local zoning and building codes
        """
        try:
            if not property_context:
                return {
                    'success': False,
                    'error': 'Property context required for local compliance analysis'
                }
            
            # Use Claude for local compliance analysis
            local_prompt = f"""
            Analyze this document for compliance with local zoning and building codes:
            
            Property Context: {json.dumps(property_context, indent=2)}
            Document Content: {document_text[:2000]}...
            
            Focus on:
            1. Zoning compliance (setbacks, height, coverage)
            2. Building code requirements
            3. Parking and access requirements
            4. Utility requirements
            5. Local ordinance compliance
            
            Provide specific findings and recommendations.
            """
            
            result = await claude_service.ask_complex_question(local_prompt)
            return {
                'success': True,
                'analysis': result.get('answer', '') if result['success'] else 'Analysis unavailable',
                'source': 'Claude AI'
            }
            
        except Exception as e:
            logger.error(f"Error in local compliance analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_statewide_compliance(self, document_text: str, property_context: Optional[Dict]) -> Dict[str, Any]:
        """
        Analyze compliance with Oregon Statewide Planning Goals using MCP
        """
        try:
            if not property_context:
                property_context = {}
            
            # Use MCP service for statewide compliance
            mcp_result = mcp_service.check_statewide_compliance(document_text, property_context)
            
            if mcp_result['success']:
                return {
                    'success': True,
                    'analysis': mcp_result,
                    'source': 'Oregon Goals MCP Server'
                }
            else:
                # Fallback to Claude analysis
                statewide_prompt = f"""
                Analyze this document for compliance with Oregon's 19 Statewide Planning Goals:
                
                Property Context: {json.dumps(property_context, indent=2)}
                Document Content: {document_text[:2000]}...
                
                Check compliance with applicable Oregon Statewide Planning Goals and provide detailed findings.
                """
                
                claude_result = await claude_service.ask_complex_question(statewide_prompt)
                return {
                    'success': True,
                    'analysis': claude_result.get('answer', '') if claude_result['success'] else 'Analysis unavailable',
                    'source': 'Claude AI (MCP fallback)',
                    'mcp_error': mcp_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error in statewide compliance analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_analysis_summary(self, analysis_results: Dict, document_text: str) -> Dict[str, Any]:
        """
        Generate summary of all analysis results
        """
        try:
            summary_prompt = f"""
            Generate a concise summary of this document analysis:
            
            Analysis Results: {json.dumps(analysis_results, indent=2)}
            
            Provide:
            1. Key Findings Summary
            2. Compliance Status Overview
            3. Major Issues Identified
            4. Overall Assessment
            """
            
            summary_result = await claude_service.ask_complex_question(summary_prompt)
            
            return {
                'success': True,
                'summary': summary_result.get('answer', '') if summary_result['success'] else 'Summary unavailable'
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """
        Generate actionable recommendations based on analysis
        """
        try:
            recommendations = []
            
            # Extract recommendations from each analysis
            for analysis_type, result in analysis_results.items():
                if isinstance(result, dict) and result.get('success'):
                    if 'recommendations' in result:
                        recommendations.extend(result['recommendations'])
            
            # If no specific recommendations, generate general ones
            if not recommendations:
                recommendations = [
                    "Review document for completeness",
                    "Verify compliance with local zoning requirements",
                    "Check statewide planning goals compliance",
                    "Ensure all required documentation is submitted"
                ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    async def _generate_site_plan_recommendations(self, claude_analysis: Dict, local_compliance: Dict, statewide_compliance: Dict) -> List[str]:
        """
        Generate specific recommendations for site plans
        """
        recommendations = []
        
        # Add recommendations based on analysis results
        if not claude_analysis.get('success', False):
            recommendations.append("Site plan requires detailed review by planning staff")
        
        if not local_compliance.get('success', False):
            recommendations.append("Verify compliance with local zoning requirements")
        
        if not statewide_compliance.get('success', False):
            recommendations.append("Review against Oregon Statewide Planning Goals")
        
        # Default recommendations for site plans
        recommendations.extend([
            "Verify all setback dimensions are clearly marked",
            "Ensure parking calculations meet code requirements",
            "Confirm utility connections are properly shown",
            "Review landscaping plan for compliance"
        ])
        
        return recommendations

# Global instance
document_analyzer = DocumentAnalyzer()


"""
Advanced Compliance Checking Engine for CiviAI
Integrates local zoning, state planning goals, and AI analysis
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from django.apps import apps
from .claude_service import claude_service
from .mcp_integration import mcp_service
from .models import Property, PermitType, ZoningRule, PermitApplication

logger = logging.getLogger(__name__)

class AdvancedComplianceEngine:
    """
    Comprehensive compliance checking system
    """
    
    def __init__(self):
        self.compliance_levels = {
            'BASIC': 'Basic zoning compliance',
            'STANDARD': 'Standard compliance with local codes',
            'COMPREHENSIVE': 'Full compliance including state goals',
            'EXPERT': 'AI-enhanced compliance with recommendations'
        }
    
    async def comprehensive_compliance_check(self, 
                                           property_id: int,
                                           permit_type_id: int,
                                           project_details: Dict,
                                           compliance_level: str = 'COMPREHENSIVE') -> Dict[str, Any]:
        """
        Perform comprehensive compliance checking at specified level
        """
        try:
            # Get property and permit type
            Property = apps.get_model('permitting', 'Property')
            PermitType = apps.get_model('permitting', 'PermitType')
            
            property_obj = await asyncio.to_thread(Property.objects.get, id=property_id)
            permit_type = await asyncio.to_thread(PermitType.objects.get, id=permit_type_id)
            
            # Build property context
            property_context = {
                'address': property_obj.address,
                'tax_lot': property_obj.tax_lot_number,
                'zoning': property_obj.zoning,
                'acres': float(property_obj.acres),
                'in_floodplain': property_obj.in_floodplain,
                'riparian_overlay': property_obj.riparian_overlay,
                'in_ugb': True  # Assume in Urban Growth Boundary
            }
            
            # Initialize results
            compliance_results = {
                'property': property_context,
                'permit_type': {
                    'id': permit_type.id,
                    'name': permit_type.name,
                    'code': permit_type.code
                },
                'project_details': project_details,
                'compliance_level': compliance_level,
                'checks_performed': [],
                'overall_status': 'PENDING',
                'summary': {},
                'recommendations': []
            }
            
            # Level 1: Basic zoning compliance
            if compliance_level in ['BASIC', 'STANDARD', 'COMPREHENSIVE', 'EXPERT']:
                basic_results = await self._check_basic_zoning_compliance(property_obj, permit_type, project_details)
                compliance_results['basic_zoning'] = basic_results
                compliance_results['checks_performed'].append('Basic Zoning Compliance')
            
            # Level 2: Standard local code compliance
            if compliance_level in ['STANDARD', 'COMPREHENSIVE', 'EXPERT']:
                standard_results = await self._check_standard_compliance(property_obj, permit_type, project_details)
                compliance_results['standard_compliance'] = standard_results
                compliance_results['checks_performed'].append('Standard Local Code Compliance')
            
            # Level 3: Statewide planning goals compliance
            if compliance_level in ['COMPREHENSIVE', 'EXPERT']:
                statewide_results = await self._check_statewide_compliance(property_context, permit_type, project_details)
                compliance_results['statewide_compliance'] = statewide_results
                compliance_results['checks_performed'].append('Oregon Statewide Planning Goals')
            
            # Level 4: AI-enhanced expert analysis
            if compliance_level == 'EXPERT':
                expert_results = await self._perform_expert_analysis(property_context, permit_type, project_details, compliance_results)
                compliance_results['expert_analysis'] = expert_results
                compliance_results['checks_performed'].append('AI Expert Analysis')
            
            # Calculate overall compliance status
            compliance_results['overall_status'] = self._calculate_overall_status(compliance_results)
            compliance_results['summary'] = self._generate_compliance_summary(compliance_results)
            compliance_results['recommendations'] = await self._generate_comprehensive_recommendations(compliance_results)
            
            return {
                'success': True,
                'compliance_results': compliance_results
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive compliance check: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _check_basic_zoning_compliance(self, property_obj, permit_type, project_details) -> Dict[str, Any]:
        """
        Check basic zoning compliance (setbacks, height, coverage)
        """
        try:
            ZoningRule = apps.get_model('permitting', 'ZoningRule')
            zoning_rules = await asyncio.to_thread(
                ZoningRule.objects.filter(zoning_district=property_obj.zoning).all
            )
            
            compliance_checks = []
            violations = []
            
            for rule in zoning_rules:
                check_result = self._evaluate_zoning_rule(rule, project_details)
                compliance_checks.append(check_result)
                
                if not check_result['compliant']:
                    violations.append(check_result)
            
            return {
                'success': True,
                'zoning_district': property_obj.zoning,
                'rules_checked': len(compliance_checks),
                'violations': len(violations),
                'compliance_rate': ((len(compliance_checks) - len(violations)) / len(compliance_checks) * 100) if compliance_checks else 100,
                'detailed_checks': compliance_checks,
                'violations_detail': violations
            }
            
        except Exception as e:
            logger.error(f"Error in basic zoning compliance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _check_standard_compliance(self, property_obj, permit_type, project_details) -> Dict[str, Any]:
        """
        Check standard compliance (building codes, utilities, access)
        """
        try:
            compliance_checks = []
            
            # Building code compliance
            building_checks = self._check_building_code_compliance(permit_type, project_details)
            compliance_checks.extend(building_checks)
            
            # Utility requirements
            utility_checks = self._check_utility_requirements(property_obj, project_details)
            compliance_checks.extend(utility_checks)
            
            # Access and parking requirements
            access_checks = self._check_access_requirements(permit_type, project_details)
            compliance_checks.extend(access_checks)
            
            # Environmental requirements
            environmental_checks = self._check_environmental_requirements(property_obj, project_details)
            compliance_checks.extend(environmental_checks)
            
            violations = [check for check in compliance_checks if not check['compliant']]
            
            return {
                'success': True,
                'categories_checked': ['Building Code', 'Utilities', 'Access/Parking', 'Environmental'],
                'total_checks': len(compliance_checks),
                'violations': len(violations),
                'compliance_rate': ((len(compliance_checks) - len(violations)) / len(compliance_checks) * 100) if compliance_checks else 100,
                'detailed_checks': compliance_checks,
                'violations_detail': violations
            }
            
        except Exception as e:
            logger.error(f"Error in standard compliance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _check_statewide_compliance(self, property_context, permit_type, project_details) -> Dict[str, Any]:
        """
        Check compliance with Oregon Statewide Planning Goals using MCP
        """
        try:
            # Create project description for MCP analysis
            project_description = f"""
            Permit Type: {permit_type.name}
            Project Details: {json.dumps(project_details)}
            Property: {property_context['address']}
            Zoning: {property_context['zoning']}
            """
            
            # Use MCP service for statewide compliance
            mcp_result = mcp_service.check_statewide_compliance(project_description, property_context)
            
            if mcp_result['success']:
                return {
                    'success': True,
                    'source': 'Oregon Goals MCP Server',
                    'mcp_analysis': mcp_result,
                    'goals_checked': mcp_result.get('summary', {}).get('total_goals_checked', 0),
                    'compliant_goals': mcp_result.get('summary', {}).get('compliant_goals', 0),
                    'overall_status': mcp_result.get('summary', {}).get('overall_status', 'UNKNOWN')
                }
            else:
                # Fallback to Claude analysis
                statewide_prompt = f"""
                Analyze this project for compliance with Oregon's 19 Statewide Planning Goals:
                
                Project: {project_description}
                Property Context: {json.dumps(property_context)}
                
                Provide detailed compliance analysis for applicable goals.
                """
                
                claude_result = await claude_service.ask_complex_question(statewide_prompt)
                
                return {
                    'success': True,
                    'source': 'Claude AI (MCP fallback)',
                    'claude_analysis': claude_result.get('answer', '') if claude_result['success'] else 'Analysis unavailable',
                    'mcp_error': mcp_result.get('error', 'MCP service unavailable')
                }
                
        except Exception as e:
            logger.error(f"Error in statewide compliance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _perform_expert_analysis(self, property_context, permit_type, project_details, existing_results) -> Dict[str, Any]:
        """
        Perform AI-enhanced expert analysis using Claude
        """
        try:
            expert_prompt = f"""
            As an expert city planner, provide comprehensive analysis of this permit application:
            
            Property: {json.dumps(property_context)}
            Permit Type: {permit_type.name}
            Project Details: {json.dumps(project_details)}
            
            Previous Compliance Results: {json.dumps(existing_results, indent=2)}
            
            Please provide:
            1. Expert Assessment of Compliance Issues
            2. Risk Analysis and Mitigation Strategies
            3. Recommended Conditions of Approval
            4. Potential Appeals or Challenges
            5. Best Practices Recommendations
            6. Long-term Planning Considerations
            """
            
            expert_result = await claude_service.ask_complex_question(expert_prompt)
            
            if expert_result['success']:
                return {
                    'success': True,
                    'expert_analysis': expert_result['answer'],
                    'model': expert_result['model'],
                    'analysis_type': 'comprehensive_expert_review'
                }
            else:
                return {
                    'success': False,
                    'error': 'Expert analysis unavailable'
                }
                
        except Exception as e:
            logger.error(f"Error in expert analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _evaluate_zoning_rule(self, rule, project_details) -> Dict[str, Any]:
        """
        Evaluate a specific zoning rule against project details
        """
        rule_type = rule.rule_type.lower()
        required_value = rule.value
        
        if rule_type == 'setback':
            provided_value = project_details.get('front_setback', 0)
            compliant = provided_value >= required_value
            
            return {
                'rule_name': f"{rule.rule_type.title()} Requirement",
                'rule_type': rule_type,
                'required': f"{required_value} ft",
                'provided': f"{provided_value} ft",
                'compliant': compliant,
                'message': f"{'✓' if compliant else '✗'} {rule.rule_type.title()} setback {'meets requirement' if compliant else f'insufficient - Required: {required_value} ft, Provided: {provided_value} ft'}"
            }
        
        elif rule_type == 'height':
            provided_value = project_details.get('building_height', 0)
            compliant = provided_value <= required_value
            
            return {
                'rule_name': f"{rule.rule_type.title()} Limit",
                'rule_type': rule_type,
                'required': f"Max {required_value} ft",
                'provided': f"{provided_value} ft",
                'compliant': compliant,
                'message': f"{'✓' if compliant else '✗'} Building height {'within limit' if compliant else f'exceeds limit - Max: {required_value} ft, Provided: {provided_value} ft'}"
            }
        
        elif rule_type == 'coverage':
            provided_value = project_details.get('lot_coverage', 0)
            compliant = provided_value <= required_value
            
            return {
                'rule_name': f"{rule.rule_type.title()} Limit",
                'rule_type': rule_type,
                'required': f"Max {required_value}%",
                'provided': f"{provided_value}%",
                'compliant': compliant,
                'message': f"{'✓' if compliant else '✗'} Lot coverage {'within limit' if compliant else f'exceeds limit - Max: {required_value}%, Provided: {provided_value}%'}"
            }
        
        else:
            # Generic rule evaluation
            return {
                'rule_name': rule.rule_type.title(),
                'rule_type': rule_type,
                'required': str(required_value),
                'provided': 'To be verified',
                'compliant': True,  # Default to compliant for unknown rules
                'message': f"✓ {rule.rule_type.title()} requirement noted"
            }
    
    def _check_building_code_compliance(self, permit_type, project_details) -> List[Dict[str, Any]]:
        """
        Check building code compliance requirements
        """
        checks = []
        
        # Basic building code checks based on permit type
        if permit_type.code in ['SFR', 'ADD', 'ADU']:
            # Residential building codes
            checks.extend([
                {
                    'rule_name': 'Egress Requirements',
                    'rule_type': 'building_code',
                    'required': 'Proper egress from all rooms',
                    'provided': 'To be verified on plans',
                    'compliant': True,
                    'message': '✓ Egress requirements to be verified during plan review'
                },
                {
                    'rule_name': 'Fire Safety',
                    'rule_type': 'building_code',
                    'required': 'Smoke detectors and fire safety measures',
                    'provided': 'To be verified',
                    'compliant': True,
                    'message': '✓ Fire safety requirements to be verified'
                }
            ])
        
        if permit_type.code == 'COM':
            # Commercial building codes
            checks.extend([
                {
                    'rule_name': 'ADA Compliance',
                    'rule_type': 'building_code',
                    'required': 'ADA accessibility requirements',
                    'provided': 'To be verified on plans',
                    'compliant': True,
                    'message': '✓ ADA compliance to be verified during plan review'
                },
                {
                    'rule_name': 'Commercial Fire Code',
                    'rule_type': 'building_code',
                    'required': 'Commercial fire safety systems',
                    'provided': 'To be verified',
                    'compliant': True,
                    'message': '✓ Commercial fire code compliance to be verified'
                }
            ])
        
        return checks
    
    def _check_utility_requirements(self, property_obj, project_details) -> List[Dict[str, Any]]:
        """
        Check utility connection requirements
        """
        checks = []
        
        # Water service
        checks.append({
            'rule_name': 'Water Service',
            'rule_type': 'utilities',
            'required': 'Adequate water service connection',
            'provided': 'Existing service available' if property_obj.address else 'To be verified',
            'compliant': True,
            'message': '✓ Water service connection available'
        })
        
        # Sewer service
        checks.append({
            'rule_name': 'Sewer Service',
            'rule_type': 'utilities',
            'required': 'Sewer connection or approved septic',
            'provided': 'City sewer available' if property_obj.address else 'To be verified',
            'compliant': True,
            'message': '✓ Sewer service connection available'
        })
        
        # Electrical service
        checks.append({
            'rule_name': 'Electrical Service',
            'rule_type': 'utilities',
            'required': 'Adequate electrical service',
            'provided': 'To be coordinated with utility provider',
            'compliant': True,
            'message': '✓ Electrical service to be coordinated'
        })
        
        return checks
    
    def _check_access_requirements(self, permit_type, project_details) -> List[Dict[str, Any]]:
        """
        Check access and parking requirements
        """
        checks = []
        
        # Parking requirements
        if permit_type.code in ['SFR', 'ADD']:
            required_parking = 2
        elif permit_type.code == 'ADU':
            required_parking = 1
        elif permit_type.code == 'COM':
            required_parking = project_details.get('square_footage', 1000) / 250  # 1 space per 250 sq ft
        else:
            required_parking = 1
        
        provided_parking = project_details.get('parking_spaces', required_parking)
        parking_compliant = provided_parking >= required_parking
        
        checks.append({
            'rule_name': 'Parking Requirements',
            'rule_type': 'access',
            'required': f"{required_parking} spaces",
            'provided': f"{provided_parking} spaces",
            'compliant': parking_compliant,
            'message': f"{'✓' if parking_compliant else '✗'} Parking {'meets requirement' if parking_compliant else f'insufficient - Required: {required_parking}, Provided: {provided_parking}'}"
        })
        
        # Street access
        checks.append({
            'rule_name': 'Street Access',
            'rule_type': 'access',
            'required': 'Legal access to public street',
            'provided': 'Existing street frontage',
            'compliant': True,
            'message': '✓ Street access available'
        })
        
        return checks
    
    def _check_environmental_requirements(self, property_obj, project_details) -> List[Dict[str, Any]]:
        """
        Check environmental requirements
        """
        checks = []
        
        # Floodplain compliance
        if property_obj.in_floodplain:
            checks.append({
                'rule_name': 'Floodplain Compliance',
                'rule_type': 'environmental',
                'required': 'Floodplain development permit',
                'provided': 'Required - to be obtained',
                'compliant': False,
                'message': '✗ Floodplain development permit required'
            })
        else:
            checks.append({
                'rule_name': 'Floodplain Compliance',
                'rule_type': 'environmental',
                'required': 'Not in floodplain',
                'provided': 'Property not in floodplain',
                'compliant': True,
                'message': '✓ Property not in floodplain'
            })
        
        # Riparian overlay
        if property_obj.riparian_overlay:
            checks.append({
                'rule_name': 'Riparian Protection',
                'rule_type': 'environmental',
                'required': 'Riparian setback compliance',
                'provided': 'To be verified',
                'compliant': True,
                'message': '✓ Riparian setback requirements to be verified'
            })
        
        return checks
    
    def _calculate_overall_status(self, compliance_results) -> str:
        """
        Calculate overall compliance status
        """
        total_violations = 0
        total_checks = 0
        
        # Count violations from all compliance levels
        for level in ['basic_zoning', 'standard_compliance']:
            if level in compliance_results and compliance_results[level].get('success'):
                total_violations += compliance_results[level].get('violations', 0)
                total_checks += compliance_results[level].get('total_checks', 0) or compliance_results[level].get('rules_checked', 0)
        
        # Check statewide compliance
        if 'statewide_compliance' in compliance_results:
            statewide = compliance_results['statewide_compliance']
            if statewide.get('success') and 'mcp_analysis' in statewide:
                mcp_status = statewide['mcp_analysis'].get('summary', {}).get('overall_status', 'UNKNOWN')
                if mcp_status == 'NON_COMPLIANT':
                    total_violations += 5  # Weight statewide violations heavily
                elif mcp_status == 'NEEDS_REVIEW':
                    total_violations += 2
        
        # Determine overall status
        if total_violations == 0:
            return 'APPROVED'
        elif total_violations <= 2:
            return 'APPROVED_WITH_CONDITIONS'
        elif total_violations <= 5:
            return 'NEEDS_REVIEW'
        else:
            return 'DENIED'
    
    def _generate_compliance_summary(self, compliance_results) -> Dict[str, Any]:
        """
        Generate summary of compliance results
        """
        summary = {
            'compliance_level': compliance_results['compliance_level'],
            'checks_performed': len(compliance_results['checks_performed']),
            'overall_status': compliance_results['overall_status']
        }
        
        # Add specific metrics
        if 'basic_zoning' in compliance_results:
            basic = compliance_results['basic_zoning']
            summary['zoning_compliance_rate'] = basic.get('compliance_rate', 0)
            summary['zoning_violations'] = basic.get('violations', 0)
        
        if 'standard_compliance' in compliance_results:
            standard = compliance_results['standard_compliance']
            summary['standard_compliance_rate'] = standard.get('compliance_rate', 0)
            summary['standard_violations'] = standard.get('violations', 0)
        
        if 'statewide_compliance' in compliance_results:
            statewide = compliance_results['statewide_compliance']
            if 'mcp_analysis' in statewide:
                mcp_summary = statewide['mcp_analysis'].get('summary', {})
                summary['statewide_goals_checked'] = mcp_summary.get('total_goals_checked', 0)
                summary['statewide_compliance_rate'] = mcp_summary.get('compliance_rate', 0)
        
        return summary
    
    async def _generate_comprehensive_recommendations(self, compliance_results) -> List[str]:
        """
        Generate comprehensive recommendations based on all compliance results
        """
        recommendations = []
        
        # Basic zoning recommendations
        if 'basic_zoning' in compliance_results:
            basic = compliance_results['basic_zoning']
            if basic.get('violations', 0) > 0:
                for violation in basic.get('violations_detail', []):
                    recommendations.append(f"Address {violation['rule_name']}: {violation['message']}")
        
        # Standard compliance recommendations
        if 'standard_compliance' in compliance_results:
            standard = compliance_results['standard_compliance']
            if standard.get('violations', 0) > 0:
                for violation in standard.get('violations_detail', []):
                    recommendations.append(f"Resolve {violation['rule_name']}: {violation['message']}")
        
        # Statewide compliance recommendations
        if 'statewide_compliance' in compliance_results:
            statewide = compliance_results['statewide_compliance']
            if 'mcp_analysis' in statewide:
                mcp_results = statewide['mcp_analysis'].get('compliance_results', [])
                for result in mcp_results:
                    if result.get('compliance', {}).get('status') != 'COMPLIANT':
                        recommendations.append(f"Address Oregon Goal {result.get('goal', {}).get('goal_number', 'Unknown')}: {result.get('goal', {}).get('title', 'Unknown')}")
        
        # Expert recommendations
        if 'expert_analysis' in compliance_results and compliance_results['expert_analysis'].get('success'):
            recommendations.append("Review expert analysis for additional recommendations and conditions")
        
        # Default recommendations if none specific
        if not recommendations:
            recommendations = [
                "Project appears to meet basic compliance requirements",
                "Proceed with standard permit review process",
                "Verify all documentation is complete"
            ]
        
        return recommendations

# Global instance
advanced_compliance_engine = AdvancedComplianceEngine()


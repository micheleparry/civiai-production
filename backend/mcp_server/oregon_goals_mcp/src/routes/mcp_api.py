"""
MCP API Routes for Oregon Statewide Planning Goals
Model Context Protocol server for planning compliance
"""

from flask import Blueprint, request, jsonify
from src.models.oregon_goals import db, StatewideGoal, ComplianceCheck, GoalRequirement
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

mcp_bp = Blueprint('mcp', __name__)

@mcp_bp.route('/goals', methods=['GET'])
def get_all_goals():
    """
    Get all Oregon Statewide Planning Goals
    """
    try:
        goals = StatewideGoal.query.order_by(StatewideGoal.goal_number).all()
        return jsonify({
            'success': True,
            'goals': [goal.to_dict() for goal in goals],
            'count': len(goals)
        })
    except Exception as e:
        logger.error(f"Error getting goals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mcp_bp.route('/goals/<int:goal_number>', methods=['GET'])
def get_goal_by_number(goal_number):
    """
    Get specific statewide goal by number
    """
    try:
        goal = StatewideGoal.query.filter_by(goal_number=goal_number).first()
        if not goal:
            return jsonify({'success': False, 'error': 'Goal not found'}), 404
        
        # Get detailed requirements
        requirements = GoalRequirement.query.filter_by(goal_id=goal.id).all()
        
        goal_data = goal.to_dict()
        goal_data['detailed_requirements'] = [req.to_dict() for req in requirements]
        
        return jsonify({
            'success': True,
            'goal': goal_data
        })
    except Exception as e:
        logger.error(f"Error getting goal {goal_number}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mcp_bp.route('/check-compliance', methods=['POST'])
def check_project_compliance():
    """
    Check project compliance against applicable statewide goals
    """
    try:
        data = request.get_json()
        
        project_id = data.get('project_id', f"project_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        project_description = data.get('project_description', '')
        property_context = data.get('property_context', {})
        
        if not project_description:
            return jsonify({'success': False, 'error': 'Project description is required'}), 400
        
        # Determine applicable goals based on project type and location
        applicable_goals = _determine_applicable_goals(project_description, property_context)
        
        compliance_results = []
        
        for goal in applicable_goals:
            # Check compliance for each applicable goal
            compliance_result = _check_goal_compliance(goal, project_description, property_context)
            
            # Save compliance check to database
            compliance_check = ComplianceCheck(
                project_id=project_id,
                goal_id=goal.id,
                project_description=project_description,
                property_context=json.dumps(property_context),
                compliance_status=compliance_result['status'],
                findings=compliance_result['findings'],
                recommendations=compliance_result['recommendations'],
                checked_by='MCP_AI_System'
            )
            
            db.session.add(compliance_check)
            compliance_results.append({
                'goal': goal.to_dict(),
                'compliance': compliance_result
            })
        
        db.session.commit()
        
        # Calculate overall compliance summary
        total_goals = len(compliance_results)
        compliant_goals = sum(1 for result in compliance_results if result['compliance']['status'] == 'COMPLIANT')
        compliance_rate = (compliant_goals / total_goals * 100) if total_goals > 0 else 100
        
        overall_status = "COMPLIANT" if compliant_goals == total_goals else "NEEDS_REVIEW"
        if compliant_goals < total_goals * 0.5:
            overall_status = "NON_COMPLIANT"
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'compliance_results': compliance_results,
            'summary': {
                'total_goals_checked': total_goals,
                'compliant_goals': compliant_goals,
                'non_compliant_goals': total_goals - compliant_goals,
                'compliance_rate': round(compliance_rate, 1),
                'overall_status': overall_status
            },
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking compliance: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@mcp_bp.route('/compliance-history/<project_id>', methods=['GET'])
def get_compliance_history(project_id):
    """
    Get compliance check history for a project
    """
    try:
        checks = ComplianceCheck.query.filter_by(project_id=project_id).order_by(ComplianceCheck.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'compliance_history': [check.to_dict() for check in checks],
            'count': len(checks)
        })
    except Exception as e:
        logger.error(f"Error getting compliance history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mcp_bp.route('/applicable-goals', methods=['POST'])
def get_applicable_goals():
    """
    Get applicable statewide goals for a project without running full compliance check
    """
    try:
        data = request.get_json()
        project_description = data.get('project_description', '')
        property_context = data.get('property_context', {})
        
        if not project_description:
            return jsonify({'success': False, 'error': 'Project description is required'}), 400
        
        applicable_goals = _determine_applicable_goals(project_description, property_context)
        
        return jsonify({
            'success': True,
            'applicable_goals': [goal.to_dict() for goal in applicable_goals],
            'count': len(applicable_goals)
        })
    except Exception as e:
        logger.error(f"Error getting applicable goals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mcp_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for MCP server
    """
    try:
        # Check database connection
        goal_count = StatewideGoal.query.count()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'goals_loaded': goal_count,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Helper functions

def _determine_applicable_goals(project_description, property_context):
    """
    Determine which statewide goals apply to a project
    """
    # Get all goals
    all_goals = StatewideGoal.query.all()
    applicable_goals = []
    
    # Convert to lowercase for keyword matching
    description_lower = project_description.lower()
    
    # Goal applicability logic
    for goal in all_goals:
        is_applicable = False
        
        if goal.goal_number == 1:  # Citizen Involvement
            # Always applicable for public projects
            is_applicable = True
            
        elif goal.goal_number == 2:  # Land Use Planning
            # Always applicable
            is_applicable = True
            
        elif goal.goal_number == 3:  # Agricultural Lands
            # Applicable if in agricultural zone or near farm land
            zoning = property_context.get('zoning', '').upper()
            is_applicable = 'AG' in zoning or 'FARM' in zoning or 'agricultural' in description_lower
            
        elif goal.goal_number == 4:  # Forest Lands
            # Applicable if in forest zone or involves trees
            zoning = property_context.get('zoning', '').upper()
            is_applicable = 'F' in zoning or 'forest' in description_lower or 'tree' in description_lower
            
        elif goal.goal_number == 5:  # Natural Resources, Scenic and Historic Areas
            # Applicable if near natural resources or historic areas
            is_applicable = any(keyword in description_lower for keyword in [
                'historic', 'scenic', 'natural', 'resource', 'wetland', 'habitat'
            ])
            
        elif goal.goal_number == 6:  # Air, Water and Land Resources Quality
            # Applicable for most development projects
            is_applicable = any(keyword in description_lower for keyword in [
                'construction', 'development', 'building', 'industrial', 'commercial'
            ])
            
        elif goal.goal_number == 7:  # Areas Subject to Natural Disasters and Hazards
            # Applicable if in floodplain or hazard areas
            in_floodplain = property_context.get('in_floodplain', False)
            is_applicable = in_floodplain or any(keyword in description_lower for keyword in [
                'flood', 'hazard', 'slope', 'earthquake', 'landslide'
            ])
            
        elif goal.goal_number == 8:  # Recreational Needs
            # Applicable for recreational projects
            is_applicable = any(keyword in description_lower for keyword in [
                'recreation', 'park', 'trail', 'sports', 'playground'
            ])
            
        elif goal.goal_number == 9:  # Economic Development
            # Applicable for commercial/industrial projects
            is_applicable = any(keyword in description_lower for keyword in [
                'commercial', 'business', 'industrial', 'economic', 'employment'
            ])
            
        elif goal.goal_number == 10:  # Housing
            # Applicable for residential projects
            is_applicable = any(keyword in description_lower for keyword in [
                'residential', 'housing', 'home', 'apartment', 'adu', 'dwelling'
            ])
            
        elif goal.goal_number == 11:  # Public Facilities and Services
            # Applicable for projects requiring public services
            is_applicable = any(keyword in description_lower for keyword in [
                'public', 'utility', 'sewer', 'water', 'school', 'fire', 'police'
            ])
            
        elif goal.goal_number == 12:  # Transportation
            # Applicable for most development projects
            is_applicable = any(keyword in description_lower for keyword in [
                'access', 'parking', 'traffic', 'transportation', 'road', 'street'
            ])
            
        elif goal.goal_number == 13:  # Energy Conservation
            # Applicable for building projects
            is_applicable = any(keyword in description_lower for keyword in [
                'building', 'construction', 'energy', 'heating', 'cooling'
            ])
            
        elif goal.goal_number == 14:  # Urbanization
            # Applicable within urban growth boundaries
            is_applicable = property_context.get('in_ugb', True)  # Assume in UGB if not specified
            
        elif goal.goal_number in [15, 16, 17, 18, 19]:  # Willamette River, Estuarine, Coastal, Beaches, Ocean
            # Applicable if near water bodies (Shady Cove has Rogue River)
            riparian_overlay = property_context.get('riparian_overlay', False)
            is_applicable = riparian_overlay or any(keyword in description_lower for keyword in [
                'river', 'water', 'riparian', 'wetland', 'stream'
            ])
        
        if is_applicable:
            applicable_goals.append(goal)
    
    return applicable_goals

def _check_goal_compliance(goal, project_description, property_context):
    """
    Check compliance with a specific statewide goal
    """
    # Get detailed requirements for this goal
    requirements = GoalRequirement.query.filter_by(goal_id=goal.id).all()
    
    findings = []
    recommendations = []
    compliance_issues = 0
    
    # Basic compliance checking logic (can be enhanced with AI/ML)
    for requirement in requirements:
        requirement_met = _evaluate_requirement(requirement, project_description, property_context)
        
        if requirement_met:
            findings.append(f"✓ {requirement.requirement_text}")
        else:
            findings.append(f"✗ {requirement.requirement_text}")
            recommendations.append(f"Address: {requirement.compliance_criteria}")
            compliance_issues += 1
    
    # Determine overall compliance status
    if compliance_issues == 0:
        status = "COMPLIANT"
    elif compliance_issues <= len(requirements) * 0.3:  # 30% threshold
        status = "NEEDS_REVIEW"
    else:
        status = "NON_COMPLIANT"
    
    return {
        'status': status,
        'findings': '\n'.join(findings),
        'recommendations': '\n'.join(recommendations),
        'requirements_checked': len(requirements),
        'compliance_issues': compliance_issues
    }

def _evaluate_requirement(requirement, project_description, property_context):
    """
    Evaluate if a specific requirement is met
    This is a simplified version - could be enhanced with AI/ML
    """
    requirement_text = requirement.requirement_text.lower()
    description_lower = project_description.lower()
    
    # Simple keyword-based evaluation
    if 'public notice' in requirement_text:
        return True  # Assume public notice will be handled by process
    
    if 'environmental impact' in requirement_text:
        return 'environmental' in description_lower or 'impact' in description_lower
    
    if 'transportation' in requirement_text:
        return 'parking' in description_lower or 'access' in description_lower
    
    if 'housing' in requirement_text:
        return 'residential' in description_lower or 'housing' in description_lower
    
    # Default to compliant for basic requirements
    return True


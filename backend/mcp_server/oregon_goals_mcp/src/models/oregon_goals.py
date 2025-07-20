"""
Oregon Statewide Planning Goals Model
Database models for tracking compliance with Oregon's 19 Statewide Planning Goals
"""

from src.models.user import db
from datetime import datetime
import json

class StatewideGoal(db.Model):
    """
    Oregon's 19 Statewide Planning Goals
    """
    __tablename__ = 'statewide_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_number = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)  # JSON string of requirements
    applicable_zones = db.Column(db.Text)  # JSON string of applicable zoning districts
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StatewideGoal {self.goal_number}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'goal_number': self.goal_number,
            'title': self.title,
            'description': self.description,
            'requirements': json.loads(self.requirements) if self.requirements else [],
            'applicable_zones': json.loads(self.applicable_zones) if self.applicable_zones else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ComplianceCheck(db.Model):
    """
    Track compliance checks against statewide goals
    """
    __tablename__ = 'compliance_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), nullable=False)  # External project reference
    goal_id = db.Column(db.Integer, db.ForeignKey('statewide_goals.id'), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    property_context = db.Column(db.Text)  # JSON string of property information
    compliance_status = db.Column(db.String(20), nullable=False)  # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW
    findings = db.Column(db.Text)  # Detailed findings
    recommendations = db.Column(db.Text)  # Recommendations for compliance
    checked_by = db.Column(db.String(100))  # System or user who performed check
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    goal = db.relationship('StatewideGoal', backref=db.backref('compliance_checks', lazy=True))
    
    def __repr__(self):
        return f'<ComplianceCheck {self.project_id} - Goal {self.goal.goal_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'goal': self.goal.to_dict() if self.goal else None,
            'project_description': self.project_description,
            'property_context': json.loads(self.property_context) if self.property_context else {},
            'compliance_status': self.compliance_status,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'checked_by': self.checked_by,
            'created_at': self.created_at.isoformat()
        }

class GoalRequirement(db.Model):
    """
    Specific requirements for each statewide goal
    """
    __tablename__ = 'goal_requirements'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('statewide_goals.id'), nullable=False)
    requirement_type = db.Column(db.String(50), nullable=False)  # ZONING, ENVIRONMENTAL, PROCEDURAL, etc.
    requirement_text = db.Column(db.Text, nullable=False)
    compliance_criteria = db.Column(db.Text)  # How to check compliance
    applicable_project_types = db.Column(db.Text)  # JSON string of applicable project types
    priority_level = db.Column(db.String(20), default='MEDIUM')  # HIGH, MEDIUM, LOW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    goal = db.relationship('StatewideGoal', backref=db.backref('requirements_detail', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'requirement_type': self.requirement_type,
            'requirement_text': self.requirement_text,
            'compliance_criteria': self.compliance_criteria,
            'applicable_project_types': json.loads(self.applicable_project_types) if self.applicable_project_types else [],
            'priority_level': self.priority_level,
            'created_at': self.created_at.isoformat()
        }


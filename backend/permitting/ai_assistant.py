"""
AI Assistant Module for CiviAI
Provides intelligent responses to planning questions and compliance checking
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from .models import Property, PermitType, ZoningRule, ComplianceCheck


class PlanningKnowledgeBase:
    """
    Knowledge base for planning regulations, procedures, and common questions
    """
    
    def __init__(self):
        self.knowledge_base = {
            # Zoning Questions
            "zoning": {
                "what_is_my_zoning": "Your property's zoning determines what types of uses are allowed and what development standards apply. I can look this up for you using your address or tax lot number.",
                "r1_requirements": "R-1 Low Density Residential allows single-family homes with maximum 35-foot height, 40% lot coverage, and setbacks of 20 feet front, 10 feet rear, 5 feet side.",
                "r2_requirements": "R-2 Medium Density Residential allows single-family and duplex homes with maximum 35-foot height, 50% lot coverage, and setbacks of 15 feet front, 10 feet rear, 5 feet side.",
                "commercial_requirements": "C-G General Commercial allows retail, office, and service uses with maximum 45-foot height, 70% lot coverage, and setbacks of 10 feet from residential zones."
            },
            
            # Permit Questions
            "permits": {
                "do_i_need_permit": "Most construction, alterations, and additions require permits. I can help determine what permits you need based on your project description.",
                "building_permit_required": "Building permits are required for new construction, additions, structural changes, electrical work, plumbing, and HVAC installations.",
                "deck_permit": "Decks over 30 inches high or attached to the house require a building permit. The fee is $75.00 plus any additional review fees.",
                "fence_permit": "Fences over 6 feet high or in front yards require permits. Standard residential fences under 6 feet in rear/side yards typically don't need permits.",
                "adu_permit": "Accessory Dwelling Units require building permits and must comply with size limits, parking requirements, and design standards."
            },
            
            # Process Questions
            "process": {
                "how_long_review": "Review times vary by permit type: Simple permits (deck, fence) typically 1-2 weeks, residential additions 2-3 weeks, new construction 3-4 weeks.",
                "public_notice_required": "Public notice is required for conditional use permits, variances, and some commercial developments. Most residential permits don't require public notice.",
                "appeal_process": "Planning decisions can be appealed to the Planning Commission within 14 days of the decision. Appeals require a $200 fee and written statement.",
                "variance_needed": "Variances are required when you can't meet standard setbacks, height limits, or other zoning requirements due to unique property constraints."
            },
            
            # Fees
            "fees": {
                "permit_fees": "Permit fees vary by type: Residential addition $200, New house $500, Commercial building $1000, Deck $75, Fence $50, ADU $300.",
                "additional_fees": "Additional fees may apply for plan review, inspections, public notices, or engineering review depending on project complexity.",
                "fee_calculation": "Fees are calculated based on permit type, project value, and square footage. I can calculate exact fees when you provide project details."
            },
            
            # Special Requirements
            "special": {
                "floodplain": "Properties in the floodplain require special permits and must meet FEMA requirements. Substantial improvements require elevation certificates.",
                "riparian": "Properties near the Rogue River have riparian setback requirements. Development within 50 feet of the river may require special review.",
                "historic": "Properties in historic districts require design review for exterior changes. Contact the planning department for historic guidelines.",
                "environmental": "Environmental review may be required for large developments, wetland impacts, or steep slope construction."
            }
        }
    
    def search_knowledge(self, question: str) -> str:
        """
        Search the knowledge base for relevant information
        """
        question_lower = question.lower()
        
        # Keywords to category mapping
        keyword_mapping = {
            "zoning": ["zoning", "zone", "r-1", "r-2", "commercial", "residential"],
            "permits": ["permit", "building", "deck", "fence", "adu", "addition"],
            "process": ["how long", "review time", "appeal", "variance", "notice"],
            "fees": ["fee", "cost", "price", "how much", "payment"],
            "special": ["floodplain", "riparian", "river", "historic", "environmental"]
        }
        
        # Find the most relevant category
        best_category = None
        best_score = 0
        
        for category, keywords in keyword_mapping.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        if best_category and best_score > 0:
            # Find the most relevant answer in the category
            category_knowledge = self.knowledge_base[best_category]
            
            for key, answer in category_knowledge.items():
                if any(keyword in question_lower for keyword in key.split("_")):
                    return answer
            
            # Return first answer in category if no specific match
            return list(category_knowledge.values())[0]
        
        return "I'd be happy to help with your planning question. Could you be more specific about what you need to know? I can help with zoning requirements, permit applications, fees, review processes, and special requirements."


class ComplianceEngine:
    """
    Enhanced compliance checking engine with AI-powered analysis
    """
    
    def __init__(self):
        self.knowledge_base = PlanningKnowledgeBase()
    
    def check_project_compliance(self, property_obj: Property, permit_type: PermitType, 
                               project_details: Dict) -> List[Dict]:
        """
        Comprehensive compliance checking for a project
        """
        compliance_results = []
        
        # Get zoning rules for the property
        zoning_rules = ZoningRule.objects.filter(zone_code=property_obj.zoning)
        
        for rule in zoning_rules:
            result = self._check_individual_rule(property_obj, rule, project_details)
            compliance_results.append(result)
        
        # Check permit-specific requirements
        permit_specific_checks = self._check_permit_specific_requirements(
            permit_type, project_details, property_obj
        )
        compliance_results.extend(permit_specific_checks)
        
        return compliance_results
    
    def _check_individual_rule(self, property_obj: Property, rule: ZoningRule, 
                              project_details: Dict) -> Dict:
        """
        Check compliance with an individual zoning rule
        """
        rule_name = rule.rule_name
        required_value = rule.required_value
        
        # Extract relevant project values
        project_value = self._extract_project_value(rule_name, project_details, property_obj)
        
        # Determine compliance
        is_compliant = self._evaluate_compliance(rule_name, required_value, project_value)
        
        return {
            "rule_name": rule_name,
            "required_value": required_value,
            "provided_value": project_value,
            "is_compliant": is_compliant,
            "message": self._generate_compliance_message(rule_name, required_value, project_value, is_compliant)
        }
    
    def _extract_project_value(self, rule_name: str, project_details: Dict, property_obj: Property) -> float:
        """
        Extract the relevant value from project details for a specific rule
        """
        rule_lower = rule_name.lower()
        
        if "height" in rule_lower:
            return float(project_details.get("building_height", 25.0))  # Default reasonable height
        elif "coverage" in rule_lower:
            # Calculate lot coverage based on project square footage
            project_sqft = float(project_details.get("square_footage", 0))
            lot_size_sqft = property_obj.size_acres * 43560  # Convert acres to sq ft
            if lot_size_sqft > 0:
                return (project_sqft / lot_size_sqft) * 100
            return 0
        elif "front" in rule_lower and "setback" in rule_lower:
            return float(project_details.get("front_setback", 15.0))  # Default that might not comply
        elif "rear" in rule_lower and "setback" in rule_lower:
            return float(project_details.get("rear_setback", 12.0))
        elif "side" in rule_lower and "setback" in rule_lower:
            return float(project_details.get("side_setback", 6.0))
        
        return 0.0
    
    def _evaluate_compliance(self, rule_name: str, required_value: float, project_value: float) -> bool:
        """
        Evaluate whether the project value complies with the rule
        """
        rule_lower = rule_name.lower()
        
        if "maximum" in rule_lower or "max" in rule_lower:
            return project_value <= required_value
        elif "minimum" in rule_lower or "min" in rule_lower:
            return project_value >= required_value
        
        return True  # Default to compliant if rule type unclear
    
    def _generate_compliance_message(self, rule_name: str, required_value: float, 
                                   project_value: float, is_compliant: bool) -> str:
        """
        Generate a human-readable compliance message
        """
        if is_compliant:
            return f"{rule_name}: Compliant"
        else:
            if "setback" in rule_name.lower():
                return f"{rule_name}: Required: {required_value} ft, Provided: {project_value} ft"
            elif "height" in rule_name.lower():
                return f"{rule_name}: Maximum {required_value} ft allowed, {project_value} ft proposed"
            elif "coverage" in rule_name.lower():
                return f"{rule_name}: Maximum {required_value}% allowed, {project_value:.1f}% proposed"
            else:
                return f"{rule_name}: Does not meet requirement of {required_value}"
    
    def _check_permit_specific_requirements(self, permit_type: PermitType, 
                                          project_details: Dict, property_obj: Property) -> List[Dict]:
        """
        Check requirements specific to the permit type
        """
        results = []
        permit_code = permit_type.code
        
        if permit_code == "DECK":
            # Deck-specific checks
            if float(project_details.get("deck_height", 0)) > 30:
                results.append({
                    "rule_name": "Deck Height Safety",
                    "required_value": "Railing required",
                    "provided_value": "Height > 30 inches",
                    "is_compliant": True,  # Assume railing will be included
                    "message": "Deck railing required for heights over 30 inches"
                })
        
        elif permit_code == "FENCE":
            # Fence-specific checks
            fence_height = float(project_details.get("fence_height", 6))
            if fence_height > 6:
                results.append({
                    "rule_name": "Maximum Fence Height",
                    "required_value": 6.0,
                    "provided_value": fence_height,
                    "is_compliant": False,
                    "message": f"Maximum fence height 6 ft, {fence_height} ft proposed"
                })
        
        elif permit_code == "ADU":
            # ADU-specific checks
            adu_size = float(project_details.get("square_footage", 0))
            if adu_size > 800:
                results.append({
                    "rule_name": "Maximum ADU Size",
                    "required_value": 800.0,
                    "provided_value": adu_size,
                    "is_compliant": False,
                    "message": f"Maximum ADU size 800 sq ft, {adu_size} sq ft proposed"
                })
        
        return results
    
    def answer_planning_question(self, question: str, context: Dict = None) -> str:
        """
        Answer planning-related questions using the knowledge base
        """
        # First try to get a direct answer from knowledge base
        answer = self.knowledge_base.search_knowledge(question)
        
        # If context is provided (like a specific property), customize the answer
        if context and "property" in context:
            property_obj = context["property"]
            answer = self._customize_answer_for_property(answer, property_obj)
        
        return answer
    
    def _customize_answer_for_property(self, answer: str, property_obj: Property) -> str:
        """
        Customize a generic answer for a specific property
        """
        # Add property-specific information
        if "zoning" in answer.lower():
            answer += f" Your property at {property_obj.address} is zoned {property_obj.zoning}."
        
        if "floodplain" in answer.lower() and property_obj.in_floodplain:
            answer += " Your property is located in the floodplain, so additional FEMA requirements apply."
        
        if "riparian" in answer.lower() and property_obj.riparian_overlay:
            answer += " Your property has riparian overlay restrictions due to proximity to the Rogue River."
        
        return answer


# Global instance for use throughout the application
compliance_engine = ComplianceEngine()


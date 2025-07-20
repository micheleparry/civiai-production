"""
Load Oregon's 19 Statewide Planning Goals into the MCP database
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.oregon_goals import db, StatewideGoal, GoalRequirement
import json

def load_statewide_goals():
    """
    Load all 19 Oregon Statewide Planning Goals
    """
    
    goals_data = [
        {
            "goal_number": 1,
            "title": "Citizen Involvement",
            "description": "To develop a citizen involvement program that insures the opportunity for citizens to be involved in all phases of the planning process.",
            "requirements": [
                "Citizen involvement program",
                "Public participation opportunities",
                "Notice and hearing requirements"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 2,
            "title": "Land Use Planning",
            "description": "To establish a land use planning process and policy framework as a basis for all decisions and actions related to use of land and to assure an adequate factual base for such decisions and actions.",
            "requirements": [
                "Comprehensive plan adoption",
                "Zoning ordinance consistency",
                "Factual base for decisions"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 3,
            "title": "Agricultural Lands",
            "description": "To preserve and maintain agricultural lands.",
            "requirements": [
                "Agricultural land preservation",
                "Farm use protection",
                "Non-farm dwelling restrictions"
            ],
            "applicable_zones": ["AG", "EFU", "FARM"]
        },
        {
            "goal_number": 4,
            "title": "Forest Lands",
            "description": "To conserve forest lands by maintaining the forest land base and to protect the state's forest economy by making possible economically efficient forest practices.",
            "requirements": [
                "Forest land conservation",
                "Forest practices protection",
                "Timber harvest sustainability"
            ],
            "applicable_zones": ["F", "FOREST"]
        },
        {
            "goal_number": 5,
            "title": "Natural Resources, Scenic and Historic Areas, and Open Spaces",
            "description": "To protect natural resources and conserve scenic and historic areas and open spaces.",
            "requirements": [
                "Natural resource inventory",
                "Historic preservation",
                "Scenic area protection",
                "Open space conservation"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 6,
            "title": "Air, Water and Land Resources Quality",
            "description": "To maintain and improve the quality of the air, water and land resources of the state.",
            "requirements": [
                "Air quality protection",
                "Water quality maintenance",
                "Soil conservation",
                "Pollution prevention"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 7,
            "title": "Areas Subject to Natural Disasters and Hazards",
            "description": "To protect people and property from natural hazards.",
            "requirements": [
                "Hazard identification",
                "Risk assessment",
                "Development restrictions in hazard areas",
                "Emergency planning"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 8,
            "title": "Recreational Needs",
            "description": "To satisfy the recreational needs of the citizens of the state and visitors and, where appropriate, to provide for the siting of necessary recreational facilities including destination resorts.",
            "requirements": [
                "Recreation needs assessment",
                "Park and recreation facilities",
                "Public access to recreation",
                "Destination resort siting"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 9,
            "title": "Economic Development",
            "description": "To provide adequate opportunities throughout the state for a variety of economic activities vital to the health, welfare, and prosperity of Oregon's citizens.",
            "requirements": [
                "Economic opportunities analysis",
                "Industrial and commercial land supply",
                "Economic development policies",
                "Employment land designation"
            ],
            "applicable_zones": ["C", "I", "COMMERCIAL", "INDUSTRIAL"]
        },
        {
            "goal_number": 10,
            "title": "Housing",
            "description": "To provide for the housing needs of citizens of the state.",
            "requirements": [
                "Housing needs analysis",
                "Variety of housing types",
                "Affordable housing opportunities",
                "Residential land supply"
            ],
            "applicable_zones": ["R", "RESIDENTIAL"]
        },
        {
            "goal_number": 11,
            "title": "Public Facilities and Services",
            "description": "To plan and develop a timely, orderly and efficient arrangement of public facilities and services to serve as a framework for urban and rural development.",
            "requirements": [
                "Public facilities planning",
                "Service capacity analysis",
                "Infrastructure coordination",
                "Urban service boundaries"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 12,
            "title": "Transportation",
            "description": "To provide and encourage a safe, convenient and economic transportation system.",
            "requirements": [
                "Transportation system plan",
                "Multi-modal transportation",
                "Traffic impact analysis",
                "Transportation demand management"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 13,
            "title": "Energy Conservation",
            "description": "To conserve energy.",
            "requirements": [
                "Energy conservation measures",
                "Building energy efficiency",
                "Transportation energy conservation",
                "Renewable energy promotion"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 14,
            "title": "Urbanization",
            "description": "To provide for an orderly and efficient transition from rural to urban land use, to accommodate urban population and urban employment inside urban growth boundaries, to ensure efficient use of land, and to provide for livable communities.",
            "requirements": [
                "Urban growth boundary",
                "Urban land use efficiency",
                "Rural land protection",
                "Livable community design"
            ],
            "applicable_zones": ["ALL"]
        },
        {
            "goal_number": 15,
            "title": "Willamette River Greenway",
            "description": "To protect, conserve, enhance and maintain the natural, scenic, historical, agricultural, economic and recreational qualities of lands along the Willamette River as the Willamette River Greenway.",
            "requirements": [
                "Greenway protection",
                "River access",
                "Compatible development",
                "Natural resource protection"
            ],
            "applicable_zones": ["GREENWAY", "RIPARIAN"]
        },
        {
            "goal_number": 16,
            "title": "Estuarine Resources",
            "description": "To recognize and protect the unique environmental, economic, and social values of each estuary and associated wetlands.",
            "requirements": [
                "Estuary protection",
                "Wetland conservation",
                "Water-dependent uses",
                "Habitat preservation"
            ],
            "applicable_zones": ["ESTUARY", "WETLAND"]
        },
        {
            "goal_number": 17,
            "title": "Coastal Shorelands",
            "description": "To conserve, protect, where appropriate develop, and where appropriate restore the resources and benefits of all coastal shorelands, recognizing their value for protection and buffering of coastal waters, fish and wildlife habitat, water-dependent uses, economic resources and recreation and aesthetics.",
            "requirements": [
                "Shoreland protection",
                "Coastal resource conservation",
                "Water-dependent development",
                "Habitat protection"
            ],
            "applicable_zones": ["COASTAL", "SHORELAND"]
        },
        {
            "goal_number": 18,
            "title": "Beaches and Dunes",
            "description": "To conserve, protect, where appropriate develop, and where appropriate restore the resources and benefits of coastal beach and dune areas.",
            "requirements": [
                "Beach and dune protection",
                "Public access maintenance",
                "Natural processes protection",
                "Compatible development"
            ],
            "applicable_zones": ["BEACH", "DUNE"]
        },
        {
            "goal_number": 19,
            "title": "Ocean Resources",
            "description": "To conserve the long-term values, benefits, and natural resources of the nearshore ocean and the continental shelf.",
            "requirements": [
                "Ocean resource protection",
                "Marine habitat conservation",
                "Sustainable ocean use",
                "Coastal zone coordination"
            ],
            "applicable_zones": ["OCEAN", "MARINE"]
        }
    ]
    
    with app.app_context():
        # Clear existing data
        GoalRequirement.query.delete()
        StatewideGoal.query.delete()
        db.session.commit()
        
        print("Loading Oregon Statewide Planning Goals...")
        
        for goal_data in goals_data:
            # Create goal
            goal = StatewideGoal(
                goal_number=goal_data["goal_number"],
                title=goal_data["title"],
                description=goal_data["description"],
                requirements=json.dumps(goal_data["requirements"]),
                applicable_zones=json.dumps(goal_data["applicable_zones"])
            )
            
            db.session.add(goal)
            db.session.flush()  # Get the ID
            
            # Add detailed requirements
            for i, requirement in enumerate(goal_data["requirements"]):
                req = GoalRequirement(
                    goal_id=goal.id,
                    requirement_type="GENERAL",
                    requirement_text=requirement,
                    compliance_criteria=f"Ensure {requirement.lower()} is addressed in project planning",
                    applicable_project_types=json.dumps(["ALL"]),
                    priority_level="MEDIUM"
                )
                db.session.add(req)
            
            print(f"✓ Loaded Goal {goal_data['goal_number']}: {goal_data['title']}")
        
        db.session.commit()
        print(f"\n✅ Successfully loaded all {len(goals_data)} Oregon Statewide Planning Goals!")
        
        # Verify the data
        total_goals = StatewideGoal.query.count()
        total_requirements = GoalRequirement.query.count()
        print(f"📊 Database contains {total_goals} goals and {total_requirements} requirements")

if __name__ == "__main__":
    load_statewide_goals()


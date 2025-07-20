"""
MCP Integration Service for CiviAI
Connects to Oregon Statewide Planning Goals MCP Server
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class MCPService:
    """
    Service to interact with Oregon Statewide Planning Goals MCP Server
    """
    
    def __init__(self):
        # MCP Server URL - can be configured in settings
        self.mcp_base_url = getattr(settings, 'MCP_SERVER_URL', 'https://5000-i949ezw629r8b2x60289e-d8f6014d.manusvm.computer')
        self.timeout = 30
    
    def check_server_health(self) -> Dict[str, Any]:
        """
        Check if MCP server is healthy and responsive
        """
        try:
            response = requests.get(f"{self.mcp_base_url}/mcp/health", timeout=self.timeout)
            if response.status_code == 200:
                return {
                    'success': True,
                    'status': 'healthy',
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}"
                }
        except Exception as e:
            logger.error(f"MCP health check failed: {str(e)}")
            return {
                'success': False,
                'status': 'unreachable',
                'error': str(e)
            }
    
    def get_all_statewide_goals(self) -> Dict[str, Any]:
        """
        Get all Oregon Statewide Planning Goals
        """
        try:
            response = requests.get(f"{self.mcp_base_url}/mcp/goals", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error getting statewide goals: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_goal_by_number(self, goal_number: int) -> Dict[str, Any]:
        """
        Get specific statewide goal by number
        """
        try:
            response = requests.get(f"{self.mcp_base_url}/mcp/goals/{goal_number}", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error getting goal {goal_number}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_statewide_compliance(self, project_description: str, property_context: Dict) -> Dict[str, Any]:
        """
        Check project compliance against Oregon Statewide Planning Goals
        """
        try:
            payload = {
                'project_description': project_description,
                'property_context': property_context
            }
            
            response = requests.post(
                f"{self.mcp_base_url}/mcp/check-compliance",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error checking statewide compliance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_applicable_goals(self, project_description: str, property_context: Dict) -> Dict[str, Any]:
        """
        Get applicable statewide goals for a project
        """
        try:
            payload = {
                'project_description': project_description,
                'property_context': property_context
            }
            
            response = requests.post(
                f"{self.mcp_base_url}/mcp/applicable-goals",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error getting applicable goals: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_compliance_history(self, project_id: str) -> Dict[str, Any]:
        """
        Get compliance check history for a project
        """
        try:
            response = requests.get(
                f"{self.mcp_base_url}/mcp/compliance-history/{project_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error getting compliance history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
mcp_service = MCPService()


"""Members tool for managing Dooray members."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class MembersTool:
    """Tool for managing Dooray members."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle members tool requests.
        
        Args:
            arguments: Tool arguments containing action and parameters
            
        Returns:
            JSON string with results
        """
        action = arguments.get("action")
        if not action:
            return json.dumps({"error": "Action parameter is required"})
        
        try:
            if action == "search_by_email":
                return await self._search_by_email(arguments)
            elif action == "search_by_id":
                return await self._search_by_id(arguments)
            elif action == "get_details":
                return await self._get_details(arguments)
            elif action == "list_project_members":
                return await self._list_project_members(arguments)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"Error in members tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _search_by_email(self, arguments: Dict[str, Any]) -> str:
        """Search member by email address."""
        email = arguments.get("email")
        if not email:
            return json.dumps({"error": "email is required for search_by_email action"})
        
        result = await self.client.search_member_by_email(email)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_id(self, arguments: Dict[str, Any]) -> str:
        """Search member by user ID."""
        user_id = arguments.get("userId")
        if not user_id:
            return json.dumps({"error": "userId is required for search_by_id action"})
        
        result = await self.client.search_member_by_id(user_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_details(self, arguments: Dict[str, Any]) -> str:
        """Get member details."""
        user_id = arguments.get("userId")
        if not user_id:
            return json.dumps({"error": "userId is required for get_details action"})
        
        result = await self.client.get_member_details(user_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _list_project_members(self, arguments: Dict[str, Any]) -> str:
        """List members of a project."""
        project_id = arguments.get("projectId")
        if not project_id:
            return json.dumps({"error": "projectId is required for list_project_members action"})
        
        result = await self.client.list_project_members(project_id)
        return json.dumps(result, ensure_ascii=False)
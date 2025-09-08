"""Files tool for managing Dooray files and images."""

import base64
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class FilesTool:
    """Tool for managing Dooray files and images."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle files tool requests.
        
        Args:
            arguments: Tool arguments containing action and parameters
            
        Returns:
            JSON string with results
        """
        action = arguments.get("action")
        if not action:
            return json.dumps({"error": "Action parameter is required"})
        
        try:
            if action == "list_task_files":
                return await self._list_task_files(arguments)
            elif action == "get_task_file_metadata":
                return await self._get_task_file_metadata(arguments)
            elif action == "get_task_file_content":
                return await self._get_task_file_content(arguments)
            elif action == "get_drive_file_metadata":
                return await self._get_drive_file_metadata(arguments)
            elif action == "get_drive_file_content":
                return await self._get_drive_file_content(arguments)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"Error in files tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _list_task_files(self, arguments: Dict[str, Any]) -> str:
        """List files attached to a task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        
        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for list_task_files action"})
        
        result = await self.client.list_task_files(project_id, task_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_task_file_metadata(self, arguments: Dict[str, Any]) -> str:
        """Get metadata for a file attached to a task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        file_id = arguments.get("fileId")
        
        if not project_id or not task_id or not file_id:
            return json.dumps({"error": "projectId, taskId, and fileId are required for get_task_file_metadata action"})
        
        result = await self.client.get_task_file_metadata(project_id, task_id, file_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_task_file_content(self, arguments: Dict[str, Any]) -> str:
        """Get content of a file attached to a task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        file_id = arguments.get("fileId")
        
        if not project_id or not task_id or not file_id:
            return json.dumps({"error": "projectId, taskId, and fileId are required for get_task_file_content action"})
        
        content = await self.client.get_task_file_content(project_id, task_id, file_id)
        
        # Encode binary content as base64 for JSON transport
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        result = {
            "content": content_b64,
            "content_type": "binary",
            "size": len(content),
            "encoding": "base64"
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_drive_file_metadata(self, arguments: Dict[str, Any]) -> str:
        """Get metadata for a file by content ID from Drive."""
        file_id = arguments.get("fileId")
        
        if not file_id:
            return json.dumps({"error": "fileId is required for get_drive_file_metadata action"})
        
        result = await self.client.get_drive_file_metadata(file_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_drive_file_content(self, arguments: Dict[str, Any]) -> str:
        """Get content of a file by content ID from Drive."""
        file_id = arguments.get("fileId")
        
        if not file_id:
            return json.dumps({"error": "fileId is required for get_drive_file_content action"})
        
        content = await self.client.get_drive_file_content(file_id)
        
        # Encode binary content as base64 for JSON transport
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        result = {
            "content": content_b64,
            "content_type": "binary",
            "size": len(content),
            "encoding": "base64"
        }
        
        return json.dumps(result, ensure_ascii=False)
"""Tags tool for managing Dooray tags."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class TagsTool:
    """Tool for managing Dooray tags."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle tags tool requests.
        
        Args:
            arguments: Tool arguments containing action and parameters
            
        Returns:
            JSON string with results
        """
        action = arguments.get("action")
        if not action:
            return json.dumps({"error": "Action parameter is required"})
        
        try:
            if action == "list":
                return await self._list_tags(arguments)
            elif action == "create":
                return await self._create_tag(arguments)
            elif action == "add_to_task":
                return await self._add_tag_to_task(arguments)
            elif action == "remove_from_task":
                return await self._remove_tag_from_task(arguments)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"Error in tags tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _list_tags(self, arguments: Dict[str, Any]) -> str:
        """List tags in a project."""
        project_id = arguments.get("projectId")
        if not project_id:
            return json.dumps({"error": "projectId is required for list action"})
        
        result = await self.client.list_tags(project_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _create_tag(self, arguments: Dict[str, Any]) -> str:
        """Create a new tag."""
        project_id = arguments.get("projectId")
        tag_name = arguments.get("tagName")
        
        if not project_id or not tag_name:
            return json.dumps({"error": "projectId and tagName are required for create action"})
        
        # Build tag data
        tag_color = arguments.get("tagColor", "4CAF50")  # 기본 녹색
        
        # Remove # if present in color
        if tag_color.startswith("#"):
            tag_color = tag_color[1:]
        
        tag_data = {
            "name": tag_name,
            "color": tag_color
        }
        
        result = await self.client.create_tag(project_id, tag_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _add_tag_to_task(self, arguments: Dict[str, Any]) -> str:
        """Add a tag to a task."""
        task_id = arguments.get("taskId")
        tag_name = arguments.get("tagName")
        project_id = arguments.get("projectId")
        
        if not task_id or not tag_name:
            return json.dumps({"error": "taskId and tagName are required for add_to_task action"})
        
        if not project_id:
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not project_id:
            return json.dumps({"error": "projectId is required (either as parameter or DOORAY_DEFAULT_PROJECT_ID env var)"})
        
        # First, get current task data
        task_data = await self.client.get_task(project_id, task_id)
        if not task_data.get("result"):
            return json.dumps({"error": "Task not found"})
        
        task_info = task_data["result"]
        
        # Get current tag IDs
        current_tag_ids = [str(tag["id"]) for tag in task_info.get("tags", [])]
        
        # Find the tag ID by name
        tags_result = await self.client.list_tags(project_id)
        tag_id = None
        
        if "result" in tags_result and isinstance(tags_result["result"], list):
            for tag in tags_result["result"]:
                if tag.get("name") == tag_name:
                    tag_id = str(tag.get("id"))
                    break
        
        if not tag_id:
            return json.dumps({"error": f"Tag '{tag_name}' not found in project"})
        
        # Add tag ID if not already present
        if tag_id not in current_tag_ids:
            current_tag_ids.append(tag_id)
        
        # Update task with new tag IDs
        update_data = {
            "tagIds": current_tag_ids,
            "subject": task_info["subject"],
            "body": task_info["body"]
        }
        
        result = await self.client.update_task(project_id, task_id, update_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _remove_tag_from_task(self, arguments: Dict[str, Any]) -> str:
        """Remove a tag from a task."""
        task_id = arguments.get("taskId")
        tag_name = arguments.get("tagName")
        project_id = arguments.get("projectId")
        
        if not task_id or not tag_name:
            return json.dumps({"error": "taskId and tagName are required for remove_from_task action"})
        
        if not project_id:
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not project_id:
            return json.dumps({"error": "projectId is required (either as parameter or DOORAY_DEFAULT_PROJECT_ID env var)"})
        
        # First, get current task data
        task_data = await self.client.get_task(project_id, task_id)
        if not task_data.get("result"):
            return json.dumps({"error": "Task not found"})
        
        task_info = task_data["result"]
        
        # Get current tag IDs
        current_tag_ids = [str(tag["id"]) for tag in task_info.get("tags", [])]
        
        # Find the tag ID by name
        tags_result = await self.client.list_tags(project_id)
        tag_id = None
        
        if "result" in tags_result and isinstance(tags_result["result"], list):
            for tag in tags_result["result"]:
                if tag.get("name") == tag_name:
                    tag_id = str(tag.get("id"))
                    break
        
        if not tag_id:
            return json.dumps({"error": f"Tag '{tag_name}' not found in project"})
        
        # Remove tag ID if present
        if tag_id in current_tag_ids:
            current_tag_ids.remove(tag_id)
        else:
            return json.dumps({"error": f"Tag '{tag_name}' is not assigned to this task"})
        
        # Update task with remaining tag IDs
        update_data = {
            "tagIds": current_tag_ids,
            "subject": task_info["subject"],
            "body": task_info["body"]
        }
        
        result = await self.client.update_task(project_id, task_id, update_data)
        return json.dumps({"success": True, "message": f"Tag '{tag_name}' removed from task", "result": result})
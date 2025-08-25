"""Tasks tool for managing Dooray tasks."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class TasksTool:
    """Tool for managing Dooray tasks."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle tasks tool requests.
        
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
                return await self._list_tasks(arguments)
            elif action == "get":
                return await self._get_task(arguments)
            elif action == "create":
                return await self._create_task(arguments)
            elif action == "update":
                return await self._update_task(arguments)
            elif action == "delete":
                return await self._delete_task(arguments)
            elif action == "change_status":
                return await self._change_status(arguments)
            elif action == "assign":
                return await self._assign_task(arguments)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"Error in tasks tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _list_tasks(self, arguments: Dict[str, Any]) -> str:
        """List tasks in a project."""
        project_id = arguments.get("projectId")
        if not project_id:
            return json.dumps({"error": "projectId is required for list action"})
        
        # Build query parameters
        params = {}
        if arguments.get("status"):
            params["workflowClass"] = arguments["status"]
        if arguments.get("assigneeId"):
            params["assigneeId"] = arguments["assigneeId"]
        
        result = await self.client.list_tasks(project_id, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_task(self, arguments: Dict[str, Any]) -> str:
        """Get a specific task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        
        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for get action"})
        
        result = await self.client.get_task(project_id, task_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _create_task(self, arguments: Dict[str, Any]) -> str:
        """Create a new task."""
        project_id = arguments.get("projectId")
        title = arguments.get("title")
        
        if not project_id or not title:
            return json.dumps({"error": "projectId and title are required for create action"})
        
        # Build task data
        task_data = {
            "subject": title,
            "body": {
                "mimeType": "text/x-markdown",
                "content": arguments.get("description", "")
            }
        }
        
        if arguments.get("assigneeId"):
            task_data["users"] = [{"member": {"id": arguments["assigneeId"]}}]
        
        if arguments.get("priority"):
            task_data["priority"] = arguments["priority"]
        
        if arguments.get("status"):
            task_data["workflowClass"] = arguments["status"]
        
        result = await self.client.create_task(project_id, task_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _update_task(self, arguments: Dict[str, Any]) -> str:
        """Update an existing task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        
        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for update action"})
        
        # Build update data
        task_data = {}
        
        if arguments.get("title"):
            task_data["subject"] = arguments["title"]
        
        if arguments.get("description"):
            task_data["body"] = {
                "mimeType": "text/x-markdown",
                "content": arguments["description"]
            }
        
        if arguments.get("assigneeId"):
            task_data["users"] = [{"member": {"id": arguments["assigneeId"]}}]
        
        if arguments.get("priority"):
            task_data["priority"] = arguments["priority"]
        
        if arguments.get("status"):
            task_data["workflowClass"] = arguments["status"]
        
        result = await self.client.update_task(project_id, task_id, task_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _delete_task(self, arguments: Dict[str, Any]) -> str:
        """Delete a task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        
        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for delete action"})
        
        result = await self.client.delete_task(project_id, task_id)
        return json.dumps({"success": True, "message": "Task deleted successfully"})
    
    async def _change_status(self, arguments: Dict[str, Any]) -> str:
        """Change task status."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        status = arguments.get("status")
        
        if not project_id or not task_id or not status:
            return json.dumps({"error": "projectId, taskId, and status are required for change_status action"})
        
        task_data = {"workflowClass": status}
        result = await self.client.update_task(project_id, task_id, task_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _assign_task(self, arguments: Dict[str, Any]) -> str:
        """Assign task to a member."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        assignee_id = arguments.get("assigneeId")
        
        if not project_id or not task_id or not assignee_id:
            return json.dumps({"error": "projectId, taskId, and assigneeId are required for assign action"})
        
        task_data = {"users": [{"member": {"id": assignee_id}}]}
        result = await self.client.update_task(project_id, task_id, task_data)
        return json.dumps(result, ensure_ascii=False)
"""Tasks tool for managing Dooray tasks."""

import json
import logging
import os
from typing import Any, Dict, Optional

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
    
    def _resolve_project_id(self, arguments: Dict[str, Any]) -> Optional[str]:
        """Resolve project ID from arguments or defaults."""
        project_id = arguments.get("projectId") or self.client.project_id or os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        if project_id:
            return str(project_id)
        return None

    def _ensure_task_id(self, arguments: Dict[str, Any]) -> Optional[str]:
        task_id = arguments.get("taskId")
        if task_id is None:
            return None
        return str(task_id)

    def _ensure_assignee_id(self, arguments: Dict[str, Any]) -> Optional[str]:
        assignee_id = arguments.get("assigneeId")
        if assignee_id is None:
            return None
        return str(assignee_id)

    async def _list_tasks(self, arguments: Dict[str, Any]) -> str:
        """List tasks in a project."""
        project_id = self._resolve_project_id(arguments)
        if not project_id:
            return json.dumps({"error": "projectId is required for list action (set DOORAY_DEFAULT_PROJECT_ID or provide projectId)"})
        
        # Build query parameters
        params = {}
        if arguments.get("status"):
            params["workflowClass"] = arguments["status"]
        assignee_id = self._ensure_assignee_id(arguments)
        if assignee_id:
            params["assigneeId"] = assignee_id
        
        result = await self.client.list_tasks(project_id, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_task(self, arguments: Dict[str, Any]) -> str:
        """Get a specific task."""
        project_id = self._resolve_project_id(arguments)
        task_id = self._ensure_task_id(arguments)

        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for get action"})

        result = await self.client.get_task(project_id, task_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _create_task(self, arguments: Dict[str, Any]) -> str:
        """Create a new task."""
        project_id = self._resolve_project_id(arguments)
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
        
        assignee_id = self._ensure_assignee_id(arguments)
        if assignee_id:
            task_data["users"] = [{"member": {"id": assignee_id}}]
        
        if arguments.get("priority"):
            task_data["priority"] = arguments["priority"]
        
        if arguments.get("status"):
            task_data["workflowClass"] = arguments["status"]
        
        result = await self.client.create_task(project_id, task_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _update_task(self, arguments: Dict[str, Any]) -> str:
        """Update an existing task."""
        project_id = self._resolve_project_id(arguments)
        task_id = self._ensure_task_id(arguments)

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
        
        assignee_id = self._ensure_assignee_id(arguments)
        if assignee_id:
            task_data["users"] = [{"member": {"id": assignee_id}}]

        if arguments.get("priority"):
            task_data["priority"] = arguments["priority"]

        if arguments.get("status"):
            task_data["workflowClass"] = arguments["status"]
        
        result = await self.client.update_task(project_id, task_id, task_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _delete_task(self, arguments: Dict[str, Any]) -> str:
        """Delete a task."""
        project_id = self._resolve_project_id(arguments)
        task_id = self._ensure_task_id(arguments)

        if not project_id or not task_id:
            return json.dumps({"error": "projectId and taskId are required for delete action"})

        result = await self.client.delete_task(project_id, task_id)
        return json.dumps({"success": True, "message": "Task deleted successfully"})
    
    async def _change_status(self, arguments: Dict[str, Any]) -> str:
        """Change task status."""
        project_id = self._resolve_project_id(arguments)
        task_id = self._ensure_task_id(arguments)
        status = arguments.get("status")

        workflow_id_arg = arguments.get("workflowId")

        if not project_id or not task_id or (status is None and workflow_id_arg is None):
            return json.dumps({"error": "projectId, taskId, and either status or workflowId are required for change_status action"})

        workflow_id = str(workflow_id_arg) if workflow_id_arg is not None else None

        if not workflow_id and status is not None:
            workflow_id = await self._resolve_workflow_id(project_id, status)

        if not workflow_id:
            return json.dumps({"error": "Unable to resolve workflow. Provide workflowId or use status/workflow name."}, ensure_ascii=False)

        result = await self.client.set_task_workflow(project_id, task_id, workflow_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _assign_task(self, arguments: Dict[str, Any]) -> str:
        """Assign task to a member."""
        project_id = self._resolve_project_id(arguments)
        task_id = self._ensure_task_id(arguments)
        assignee_id = self._ensure_assignee_id(arguments)

        if not task_id or not assignee_id:
            return json.dumps({"error": "taskId and assigneeId are required for assign action"})
        
        task_data = {"users": [{"member": {"id": assignee_id}}]}
        result = await self.client.update_task(project_id, task_id, task_data)
        return json.dumps(result, ensure_ascii=False)

    async def _resolve_workflow_id(self, project_id: str, identifier: str) -> Optional[str]:
        if identifier is None:
            return None

        identifier_text = str(identifier).strip()
        if not identifier_text:
            return None

        workflows = await self.client.list_workflows(project_id)
        items = workflows.get("result") or []

        normalized = identifier_text.lower()
        class_matches: list[tuple[int, str]] = []

        for item in items:
            workflow_id = str(item.get("id")) if item.get("id") is not None else None
            if not workflow_id:
                continue

            if workflow_id == identifier_text:
                return workflow_id

            name = item.get("name")
            if isinstance(name, str) and name.lower() == normalized:
                return workflow_id

            for localized in item.get("names", []) or []:
                localized_name = localized.get("name")
                if isinstance(localized_name, str) and localized_name.lower() == normalized:
                    return workflow_id

            workflow_class = item.get("class")
            if isinstance(workflow_class, str) and workflow_class.lower() == normalized:
                order_value = item.get("order")
                try:
                    order = int(order_value)
                except (TypeError, ValueError):
                    order = 0
                class_matches.append((order, workflow_id))

        if class_matches:
            class_matches.sort(key=lambda pair: pair[0])
            return class_matches[0][1]

        return None

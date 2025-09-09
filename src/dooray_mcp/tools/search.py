"""Search tool for searching Dooray content."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class SearchTool:
    """Tool for searching Dooray content."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle search tool requests.
        
        Args:
            arguments: Tool arguments containing searchType and parameters
            
        Returns:
            JSON string with results
        """
        search_type = arguments.get("searchType")
        if not search_type:
            return json.dumps({"error": "searchType parameter is required"})
        
        try:
            if search_type == "tasks":
                return await self._search_tasks(arguments)
            elif search_type == "by_assignee":
                return await self._search_by_assignee(arguments)
            elif search_type == "by_status":
                return await self._search_by_status(arguments)
            elif search_type == "by_tag":
                return await self._search_by_tag(arguments)
            elif search_type == "by_date_range":
                return await self._search_by_date_range(arguments)
            elif search_type == "by_workflow":
                return await self._search_by_workflow(arguments)
            elif search_type == "advanced":
                return await self._advanced_search(arguments)
            else:
                return json.dumps({"error": f"Unknown search type: {search_type}"})
                
        except Exception as e:
            logger.error(f"Error in search tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _search_tasks(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by query text."""
        project_id = arguments.get("projectId")
        query = arguments.get("query")
        
        if not query:
            return json.dumps({"error": "query is required for tasks search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks(project_id, query, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_assignee(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by assignee."""
        project_id = arguments.get("projectId")
        assignee_id = arguments.get("assigneeId")
        
        if not assignee_id:
            return json.dumps({"error": "assigneeId is required for by_assignee search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks_by_assignee(project_id, assignee_id, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_status(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by status."""
        project_id = arguments.get("projectId")
        status = arguments.get("status")
        
        if not status:
            return json.dumps({"error": "status is required for by_status search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks_by_status(project_id, status, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_tag(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by tag."""
        project_id = arguments.get("projectId")
        tag_name = arguments.get("tagName")
        
        if not tag_name:
            return json.dumps({"error": "tagName is required for by_tag search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks_by_tag(project_id, tag_name, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_date_range(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by date range."""
        project_id = arguments.get("projectId")
        start_date = arguments.get("startDate")
        end_date = arguments.get("endDate")
        
        if not start_date or not end_date:
            return json.dumps({"error": "startDate and endDate are required for by_date_range search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks_by_date_range(project_id, start_date, end_date, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _search_by_workflow(self, arguments: Dict[str, Any]) -> str:
        """Search tasks by workflow ID."""
        project_id = arguments.get("projectId")
        workflow_id = arguments.get("workflowId")
        
        if not workflow_id:
            return json.dumps({"error": "workflowId is required for by_workflow search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.search_tasks_by_workflow(project_id, workflow_id, **params)
        return json.dumps(result, ensure_ascii=False)
    
    async def _advanced_search(self, arguments: Dict[str, Any]) -> str:
        """Advanced search with multiple conditions and AND/OR logic."""
        project_id = arguments.get("projectId")
        conditions = arguments.get("conditions", [])
        logic_operator = arguments.get("logicOperator", "AND")  # AND or OR
        
        if not conditions:
            return json.dumps({"error": "conditions array is required for advanced search"})
        
        # Build search parameters
        params = {}
        if arguments.get("limit"):
            params["size"] = arguments["limit"]
        
        result = await self.client.advanced_search_tasks(project_id, conditions, logic_operator, **params)
        return json.dumps(result, ensure_ascii=False)
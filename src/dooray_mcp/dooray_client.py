"""Dooray API Client for interacting with Dooray REST API."""

import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

class DoorayClient:
    """Client for interacting with Dooray API."""
    
    def __init__(self, api_token: str, base_url: str = "https://api.dooray.com", project_id: Optional[str] = None):
        """Initialize Dooray client.
        
        Args:
            api_token: Dooray API token
            base_url: Base URL for Dooray API
            project_id: Default project ID (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.headers = {
            "Authorization": f"dooray-api {api_token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Dooray API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx
            
        Returns:
            JSON response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"Dooray API error: {str(e)}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self._request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self._request("POST", endpoint, json=data, **kwargs)
    
    async def put(self, endpoint: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._request("PUT", endpoint, json=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint, **kwargs)
    
    # Project methods
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project information."""
        return await self._request("GET", f"/project/v1/projects/{project_id}")
    
    async def list_projects(self) -> Dict[str, Any]:
        """List user's projects."""
        return await self._request("GET", "/project/v1/projects")
    
    # Task methods
    async def list_tasks(self, project_id: str, **params) -> Dict[str, Any]:
        """List tasks in a project."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=params)
    
    async def get_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Get task details."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts/{task_id}")
    
    async def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        return await self._request("POST", f"/project/v1/projects/{project_id}/posts", json=task_data)
    
    async def update_task(self, project_id: str, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task."""
        return await self._request("PUT", f"/project/v1/projects/{project_id}/posts/{task_id}", json=task_data)
    
    async def delete_task(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """Delete a task."""
        return await self._request("DELETE", f"/project/v1/projects/{project_id}/posts/{task_id}")
    
    # Comment methods (using logs endpoint)
    async def list_comments(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """List comments for a task."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts/{task_id}/logs")
    
    async def create_comment(self, project_id: str, task_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comment on a task."""
        return await self._request("POST", f"/project/v1/projects/{project_id}/posts/{task_id}/logs", json=comment_data)
    
    async def update_comment(self, project_id: str, task_id: str, comment_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a comment."""
        return await self._request("PUT", f"/project/v1/projects/{project_id}/posts/{task_id}/logs/{comment_id}", json=comment_data)
    
    async def delete_comment(self, project_id: str, task_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment."""
        return await self._request("DELETE", f"/project/v1/projects/{project_id}/posts/{task_id}/logs/{comment_id}")
    
    # Tag methods
    async def list_tags(self, project_id: str) -> Dict[str, Any]:
        """List tags in a project."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/tags")
    
    async def create_tag(self, project_id: str, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tag."""
        return await self._request("POST", f"/project/v1/projects/{project_id}/tags", json=tag_data)
    
    
    # Member methods
    async def search_member_by_email(self, email: str) -> Dict[str, Any]:
        """Search member by email."""
        return await self._request("GET", f"/common/v1/members", params={"externalEmailAddresses": email})
    
    async def search_member_by_id(self, user_id: str) -> Dict[str, Any]:
        """Search member by user ID."""
        return await self._request("GET", f"/common/v1/members", params={"userCode": user_id})
    
    async def get_member_details(self, member_id: str) -> Dict[str, Any]:
        """Get member details."""
        return await self._request("GET", f"/common/v1/members/{member_id}")
    
    async def list_project_members(self, project_id: str) -> Dict[str, Any]:
        """List project members."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/members")
    
    # Search methods
    async def search_tasks(self, project_id: str, query: str, **params) -> Dict[str, Any]:
        """Search tasks by query."""
        search_params = {"query": query, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def search_tasks_by_assignee(self, project_id: str, assignee_id: str, **params) -> Dict[str, Any]:
        """Search tasks by assignee."""
        search_params = {"assigneeId": assignee_id, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def search_tasks_by_status(self, project_id: str, status: str, **params) -> Dict[str, Any]:
        """Search tasks by status."""
        search_params = {"workflowClass": status, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def search_tasks_by_tag(self, project_id: str, tag_name: str, **params) -> Dict[str, Any]:
        """Search tasks by tag."""
        search_params = {"tagName": tag_name, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def search_tasks_by_date_range(self, project_id: str, start_date: str, end_date: str, **params) -> Dict[str, Any]:
        """Search tasks by date range."""
        search_params = {"from": start_date, "to": end_date, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def search_tasks_by_workflow(self, project_id: str, workflow_id: str, **params) -> Dict[str, Any]:
        """Search tasks by workflow ID."""
        search_params = {"workflowId": workflow_id, **params}
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
    
    async def advanced_search_tasks(self, project_id: str, conditions: List[Dict[str, Any]], logic_operator: str = "AND", **params) -> Dict[str, Any]:
        """
        Advanced search with multiple conditions and AND/OR logic.
        
        Args:
            project_id: Project ID
            conditions: List of search conditions, each containing:
                - type: 'workflow', 'assignee', 'tag', 'status', 'query', 'date_range'
                - value: condition value (varies by type)
                - Additional fields based on type
            logic_operator: 'AND' or 'OR' for combining conditions
            **params: Additional parameters
            
        Returns:
            Combined search results
        """
        if logic_operator.upper() == "AND":
            # For AND logic, apply all filters at once
            search_params = {}
            
            for condition in conditions:
                cond_type = condition.get("type")
                value = condition.get("value")
                
                if cond_type == "workflow" and value:
                    search_params["workflowId"] = value
                elif cond_type == "assignee" and value:
                    search_params["assigneeId"] = value
                elif cond_type == "tag" and value:
                    search_params["tagName"] = value
                elif cond_type == "status" and value:
                    search_params["workflowClass"] = value
                elif cond_type == "query" and value:
                    search_params["query"] = value
                elif cond_type == "date_range":
                    start_date = condition.get("startDate")
                    end_date = condition.get("endDate")
                    if start_date and end_date:
                        search_params["from"] = start_date
                        search_params["to"] = end_date
            
            search_params.update(params)
            return await self._request("GET", f"/project/v1/projects/{project_id}/posts", params=search_params)
        
        else:  # OR logic
            # For OR logic, make separate requests and combine results
            all_results = []
            all_task_ids = set()
            
            for condition in conditions:
                try:
                    cond_type = condition.get("type")
                    value = condition.get("value")
                    
                    if cond_type == "workflow" and value:
                        result = await self.search_tasks_by_workflow(project_id, value, **params)
                    elif cond_type == "assignee" and value:
                        result = await self.search_tasks_by_assignee(project_id, value, **params)
                    elif cond_type == "tag" and value:
                        result = await self.search_tasks_by_tag(project_id, value, **params)
                    elif cond_type == "status" and value:
                        result = await self.search_tasks_by_status(project_id, value, **params)
                    elif cond_type == "query" and value:
                        result = await self.search_tasks(project_id, value, **params)
                    elif cond_type == "date_range":
                        start_date = condition.get("startDate")
                        end_date = condition.get("endDate")
                        if start_date and end_date:
                            result = await self.search_tasks_by_date_range(project_id, start_date, end_date, **params)
                        else:
                            continue
                    else:
                        continue
                    
                    # Add unique results
                    if result.get("result"):
                        for task in result["result"]:
                            task_id = task.get("id")
                            if task_id and task_id not in all_task_ids:
                                all_task_ids.add(task_id)
                                all_results.append(task)
                
                except Exception as e:
                    logger.warning(f"Error in condition {condition}: {e}")
                    continue
            
            # Return combined results in the same format as other search methods
            return {
                "header": {"resultCode": 0, "resultMessage": "", "isSuccessful": True},
                "result": all_results,
                "totalCount": len(all_results)
            }
    
    # File methods for Tasks (Posts)
    async def list_task_files(self, project_id: str, task_id: str) -> Dict[str, Any]:
        """List files attached to a task."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts/{task_id}/files")
    
    async def get_task_file_metadata(self, project_id: str, task_id: str, file_id: str) -> Dict[str, Any]:
        """Get file metadata for a task file."""
        return await self._request("GET", f"/project/v1/projects/{project_id}/posts/{task_id}/files/{file_id}", params={"media": "meta"})
    
    async def get_task_file_content(self, project_id: str, task_id: str, file_id: str) -> bytes:
        """Get raw file content from a task."""
        url = f"{self.base_url}/project/v1/projects/{project_id}/posts/{task_id}/files/{file_id}?media=raw"
        logger.debug(f"Making GET request for task file content to {url}")
        
        try:
            # First request to get redirect URL
            response = await self.client.get(url, follow_redirects=False)
            
            if response.status_code in [307, 302, 301]:
                # Handle redirect manually with proper headers
                redirect_url = response.headers.get("location")
                if redirect_url:
                    logger.debug(f"Following redirect to {redirect_url}")
                    response = await self.client.get(redirect_url)
                    response.raise_for_status()
                    return response.content
            
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"Dooray API error: {str(e)}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    # File methods for Drive (direct content access)
    async def get_drive_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata from Drive by content ID."""
        return await self._request("GET", f"/drive/v1/files/{file_id}", params={"media": "meta"})
    
    async def get_drive_file_content(self, file_id: str) -> bytes:
        """Get raw file content from Drive by content ID."""
        url = f"{self.base_url}/drive/v1/files/{file_id}?media=raw"
        logger.debug(f"Making GET request for drive file content to {url}")
        
        try:
            # First request to get redirect URL
            response = await self.client.get(url, follow_redirects=False)
            
            if response.status_code in [307, 302, 301]:
                # Handle redirect manually with proper headers
                redirect_url = response.headers.get("location")
                if redirect_url:
                    logger.debug(f"Following redirect to {redirect_url}")
                    response = await self.client.get(redirect_url)
                    response.raise_for_status()
                    return response.content
            
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"Dooray API error: {str(e)}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {str(e)}")
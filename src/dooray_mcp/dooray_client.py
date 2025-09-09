"""Dooray API Client for interacting with Dooray REST API."""

import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

class DoorayClient:
    """Client for interacting with Dooray API."""
    
    def __init__(self, api_token: str, base_url: str = "https://api.dooray.com"):
        """Initialize Dooray client.
        
        Args:
            api_token: Dooray API token
            base_url: Base URL for Dooray API
        """
        self.base_url = base_url.rstrip('/')
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
            response = await self.client.get(url, follow_redirects=True)
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
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"Dooray API error: {str(e)}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Request failed: {str(e)}")
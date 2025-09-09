"""
Dooray Workflow management tools
"""
from typing import Dict, Any, Optional, List
from ..dooray_client import DoorayClient


class WorkflowsTool:
    """Handle Dooray workflow operations."""
    
    def __init__(self, client: DoorayClient):
        self.client = client
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow tool calls."""
        action = args.get("action")
        
        if action == "list":
            return await list_workflows(
                self.client, 
                args.get("projectId")
            )
        elif action == "get":
            return await get_workflow_details(
                self.client,
                args["workflowId"],
                args.get("projectId")
            )
        elif action == "create":
            return await create_workflow(
                self.client,
                args["name"],
                args.get("projectId")
            )
        elif action == "update":
            return await update_workflow(
                self.client,
                args["workflowId"],
                args["name"],
                args.get("projectId")
            )
        elif action == "delete":
            return await delete_workflow(
                self.client,
                args["workflowId"],
                args.get("projectId")
            )
        else:
            raise ValueError(f"Unknown action: {action}")


async def list_workflows(client: DoorayClient, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    List all workflows for a project
    
    Args:
        client: DoorayClient instance
        project_id: Project ID (optional - uses default from environment if not provided)
        
    Returns:
        Dictionary containing workflow list response
    """
    # Use default project ID if not provided
    if not project_id:
        project_id = client.project_id
        
    if not project_id:
        raise ValueError("Project ID must be provided either as parameter or environment variable")
    
    endpoint = f"/project/v1/projects/{project_id}/workflows"
    return await client.get(endpoint)


async def get_workflow_details(client: DoorayClient, workflow_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get details of a specific workflow
    
    Args:
        client: DoorayClient instance
        workflow_id: Workflow ID
        project_id: Project ID (optional - uses default from environment if not provided)
        
    Returns:
        Dictionary containing workflow details
    """
    # Use default project ID if not provided
    if not project_id:
        project_id = client.project_id
        
    if not project_id:
        raise ValueError("Project ID must be provided either as parameter or environment variable")
    
    endpoint = f"/project/v1/projects/{project_id}/workflows/{workflow_id}"
    return await client.get(endpoint)


async def create_workflow(client: DoorayClient, name: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new workflow
    
    Args:
        client: DoorayClient instance
        name: Workflow name
        project_id: Project ID (optional - uses default from environment if not provided)
        
    Returns:
        Dictionary containing created workflow response
    """
    # Use default project ID if not provided
    if not project_id:
        project_id = client.project_id
        
    if not project_id:
        raise ValueError("Project ID must be provided either as parameter or environment variable")
    
    endpoint = f"/project/v1/projects/{project_id}/workflows"
    data = {"name": name}
    return await client.post(endpoint, data)


async def update_workflow(client: DoorayClient, workflow_id: str, name: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing workflow
    
    Args:
        client: DoorayClient instance
        workflow_id: Workflow ID
        name: New workflow name
        project_id: Project ID (optional - uses default from environment if not provided)
        
    Returns:
        Dictionary containing updated workflow response
    """
    # Use default project ID if not provided
    if not project_id:
        project_id = client.project_id
        
    if not project_id:
        raise ValueError("Project ID must be provided either as parameter or environment variable")
    
    endpoint = f"/project/v1/projects/{project_id}/workflows/{workflow_id}"
    data = {"name": name}
    return await client.put(endpoint, data)


async def delete_workflow(client: DoorayClient, workflow_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a workflow
    
    Args:
        client: DoorayClient instance
        workflow_id: Workflow ID
        project_id: Project ID (optional - uses default from environment if not provided)
        
    Returns:
        Dictionary containing delete response
    """
    # Use default project ID if not provided
    if not project_id:
        project_id = client.project_id
        
    if not project_id:
        raise ValueError("Project ID must be provided either as parameter or environment variable")
    
    endpoint = f"/project/v1/projects/{project_id}/workflows/{workflow_id}/delete"
    return await client.post(endpoint, {})
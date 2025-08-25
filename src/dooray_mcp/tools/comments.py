"""Comments tool for managing Dooray task comments."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class CommentsTool:
    """Tool for managing Dooray task comments."""
    
    def __init__(self, dooray_client):
        """Initialize with Dooray client."""
        self.client = dooray_client
    
    async def handle(self, arguments: Dict[str, Any]) -> str:
        """Handle comments tool requests.
        
        Args:
            arguments: Tool arguments containing action and parameters
            
        Returns:
            JSON string with results
        """
        action = arguments.get("action")
        task_id = arguments.get("taskId")
        
        if not action:
            return json.dumps({"error": "Action parameter is required"})
        
        if not task_id:
            return json.dumps({"error": "taskId parameter is required"})
        
        try:
            if action == "list":
                return await self._list_comments(arguments)
            elif action == "create":
                return await self._create_comment(arguments)
            elif action == "update":
                return await self._update_comment(arguments)
            elif action == "delete":
                return await self._delete_comment(arguments)
            else:
                return json.dumps({"error": f"Unknown action: {action}"})
                
        except Exception as e:
            logger.error(f"Error in comments tool: {e}")
            return json.dumps({"error": str(e)})
    
    async def _list_comments(self, arguments: Dict[str, Any]) -> str:
        """List comments for a task."""
        task_id = arguments.get("taskId")
        
        # Use provided projectId or default from environment
        project_id = arguments.get("projectId")
        if not project_id:
            # Import at function level to avoid circular import
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not project_id:
            return json.dumps({"error": "projectId is required (either as parameter or DOORAY_DEFAULT_PROJECT_ID env var)"})
        
        result = await self.client.list_comments(project_id, task_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _create_comment(self, arguments: Dict[str, Any]) -> str:
        """Create a new comment."""
        task_id = arguments.get("taskId")
        content = arguments.get("content")
        
        # Use provided projectId or default from environment
        project_id = arguments.get("projectId")
        if not project_id:
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not content:
            return json.dumps({"error": "content is required for create action"})
        
        # Build comment data
        comment_data = {
            "body": {
                "mimeType": "text/x-markdown",
                "content": content
            }
        }
        
        # Add mentions if provided
        mentions = arguments.get("mentions", [])
        if mentions:
            # Format mentions in Dooray format
            mention_text = ""
            for user_id in mentions:
                mention_text += f"@{user_id} "
            
            if mention_text:
                comment_data["body"]["content"] = mention_text + content
        
        result = await self.client.create_comment(project_id, task_id, comment_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _update_comment(self, arguments: Dict[str, Any]) -> str:
        """Update an existing comment."""
        task_id = arguments.get("taskId")
        comment_id = arguments.get("commentId")
        content = arguments.get("content")
        
        # Use provided projectId or default from environment
        project_id = arguments.get("projectId")
        if not project_id:
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not comment_id:
            return json.dumps({"error": "commentId is required for update action"})
        
        if not content:
            return json.dumps({"error": "content is required for update action"})
        
        # Build update data
        comment_data = {
            "body": {
                "mimeType": "text/x-markdown",
                "content": content
            }
        }
        
        # Add mentions if provided
        mentions = arguments.get("mentions", [])
        if mentions:
            mention_text = ""
            for user_id in mentions:
                mention_text += f"@{user_id} "
            
            if mention_text:
                comment_data["body"]["content"] = mention_text + content
        
        result = await self.client.update_comment(project_id, task_id, comment_id, comment_data)
        return json.dumps(result, ensure_ascii=False)
    
    async def _delete_comment(self, arguments: Dict[str, Any]) -> str:
        """Delete a comment."""
        task_id = arguments.get("taskId")
        comment_id = arguments.get("commentId")
        
        # Use provided projectId or default from environment
        project_id = arguments.get("projectId")
        if not project_id:
            import os
            project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
        
        if not comment_id:
            return json.dumps({"error": "commentId is required for delete action"})
        
        result = await self.client.delete_comment(project_id, task_id, comment_id)
        return json.dumps({"success": True, "message": "Comment deleted successfully"})
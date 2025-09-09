"""Files tool for managing Dooray files and images."""

import base64
import json
import logging
import os
import tempfile
from typing import Any, Dict
from urllib.parse import urlparse

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
        """Get content of a file attached to a task and save to temporary file."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        file_id = arguments.get("fileId")
        
        if not project_id or not task_id or not file_id:
            return json.dumps({"error": "projectId, taskId, and fileId are required for get_task_file_content action"})
        
        try:
            # Get file metadata first to get filename
            metadata = await self.client.get_task_file_metadata(project_id, task_id, file_id)
            filename = metadata.get("result", {}).get("name", f"file_{file_id}")
            
            # Download file content
            content = await self.client.get_task_file_content(project_id, task_id, file_id)
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            dooray_temp_dir = os.path.join(temp_dir, "dooray_files")
            os.makedirs(dooray_temp_dir, exist_ok=True)
            
            # Use original filename but ensure it's safe
            safe_filename = self._make_safe_filename(filename)
            temp_file_path = os.path.join(dooray_temp_dir, f"{task_id}_{file_id}_{safe_filename}")
            
            # Write content to file
            with open(temp_file_path, 'wb') as f:
                f.write(content)
            
            result = {
                "file_path": temp_file_path,
                "filename": filename,
                "size": len(content),
                "content_type": "file",
                "task_id": task_id,
                "file_id": file_id
            }
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error downloading task file: {e}")
            return json.dumps({"error": f"Failed to download file: {str(e)}"})
    
    def _make_safe_filename(self, filename: str) -> str:
        """Make filename safe for filesystem."""
        # Remove or replace unsafe characters
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(safe_name) > 100:
            name_parts = safe_name.rsplit('.', 1)
            if len(name_parts) == 2:
                safe_name = name_parts[0][:95] + '.' + name_parts[1]
            else:
                safe_name = safe_name[:100]
        return safe_name
    
    async def _get_drive_file_metadata(self, arguments: Dict[str, Any]) -> str:
        """Get metadata for a file by content ID from Drive."""
        file_id = arguments.get("fileId")
        
        if not file_id:
            return json.dumps({"error": "fileId is required for get_drive_file_metadata action"})
        
        result = await self.client.get_drive_file_metadata(file_id)
        return json.dumps(result, ensure_ascii=False)
    
    async def _get_drive_file_content(self, arguments: Dict[str, Any]) -> str:
        """Get content of a file by content ID from Drive and save to temporary file."""
        file_id = arguments.get("fileId")
        
        if not file_id:
            return json.dumps({"error": "fileId is required for get_drive_file_content action"})
        
        try:
            # Get file metadata first to get filename
            metadata = await self.client.get_drive_file_metadata(file_id)
            filename = metadata.get("result", {}).get("name", f"drive_file_{file_id}")
            
            # Download file content
            content = await self.client.get_drive_file_content(file_id)
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            dooray_temp_dir = os.path.join(temp_dir, "dooray_files")
            os.makedirs(dooray_temp_dir, exist_ok=True)
            
            # Use original filename but ensure it's safe
            safe_filename = self._make_safe_filename(filename)
            temp_file_path = os.path.join(dooray_temp_dir, f"drive_{file_id}_{safe_filename}")
            
            # Write content to file
            with open(temp_file_path, 'wb') as f:
                f.write(content)
            
            result = {
                "file_path": temp_file_path,
                "filename": filename,
                "size": len(content),
                "content_type": "file",
                "file_id": file_id
            }
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error downloading drive file: {e}")
            return json.dumps({"error": f"Failed to download file: {str(e)}"})
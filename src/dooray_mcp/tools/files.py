"""Files tool for managing Dooray files and images."""

import json
import logging
import mimetypes
import os
import tempfile
from typing import Any, Dict

from ..s3_uploader import S3Config, S3Uploader

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
            elif action == "upload_task_file":
                return await self._upload_task_file(arguments)
            elif action == "upload_body_image":
                return await self._upload_body_image(arguments)
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
    
    async def _upload_task_file(self, arguments: Dict[str, Any]) -> str:
        """Upload a file to a task."""
        project_id = arguments.get("projectId")
        task_id = arguments.get("taskId")
        file_path = arguments.get("filePath")
        filename = arguments.get("filename")
        mime_type = arguments.get("mimeType")

        if not project_id or not task_id or not file_path:
            return json.dumps({"error": "projectId, taskId, and filePath are required for upload_task_file action"})

        normalized_file_path = os.path.abspath(os.path.expanduser(str(file_path)))
        if not os.path.isfile(normalized_file_path):
            return json.dumps({"error": f"filePath does not exist or is not a file: {normalized_file_path}"})

        result = await self.client.upload_task_file(
            project_id,
            task_id,
            normalized_file_path,
            filename=filename,
            mime_type=mime_type,
        )
        return json.dumps(result, ensure_ascii=False)

    async def _upload_body_image(self, arguments: Dict[str, Any]) -> str:
        """Upload an image to S3 for use in Dooray body markdown/html."""
        file_path = arguments.get("filePath")
        filename = arguments.get("filename")
        mime_type = arguments.get("mimeType")
        s3_key = arguments.get("s3Key")
        alt_text = arguments.get("altText")

        if not file_path:
            return json.dumps({"error": "filePath is required for upload_body_image action"})

        normalized_file_path = os.path.abspath(os.path.expanduser(str(file_path)))
        if not os.path.isfile(normalized_file_path):
            return json.dumps({"error": f"filePath does not exist or is not a file: {normalized_file_path}"})

        upload_filename = str(filename) if filename else os.path.basename(normalized_file_path)
        upload_mime_type = mime_type or mimetypes.guess_type(upload_filename)[0] or "application/octet-stream"
        if not str(upload_mime_type).startswith("image/"):
            return json.dumps({"error": f"upload_body_image only supports image/* MIME types: {upload_mime_type}"})

        try:
            uploader = S3Uploader(S3Config.from_env())
            result = await uploader.upload_file(
                normalized_file_path,
                filename=upload_filename,
                content_type=str(upload_mime_type),
                key=str(s3_key) if s3_key else None,
            )
            image_alt = str(alt_text) if alt_text else result["filename"]
            result.update({
                "markdown": f"![{image_alt}]({result['url']})",
                "html": f'<img src="{result["url"]}" alt="{image_alt}">',
                "usageNote": "Dooray 업무/댓글 본문에 markdown 값을 넣으면 이미지로 표시됩니다. S3 객체는 Dooray 사용자가 인증 없이 접근 가능해야 합니다.",
            })
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error uploading body image to S3: {e}")
            return json.dumps({"error": f"Failed to upload body image to S3: {str(e)}"}, ensure_ascii=False)

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
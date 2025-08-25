#!/usr/bin/env python3
"""Dooray MCP Server for Claude Code integration."""

import asyncio
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

from .dooray_client import DoorayClient
from .tools.tasks import TasksTool
from .tools.comments import CommentsTool
from .tools.tags import TagsTool
from .tools.search import SearchTool
from .tools.members import MembersTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = Server("dooray-mcp")

# Initialize Dooray client
dooray_client = None
default_project_id = None

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available Dooray tools."""
    return [
        types.Tool(
            name="dooray_tasks",
            description="Manage Dooray tasks - list, get details, create, update, delete, change status, assign members",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "get", "create", "update", "delete", "change_status", "assign"],
                        "description": "Action to perform"
                    },
                    "projectId": {
                        "type": "string",
                        "description": "Project ID (required for most actions)"
                    },
                    "taskId": {
                        "type": "string", 
                        "description": "Task ID (required for get/update/delete/status/assign)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (for create/update)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (for create/update)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (for create/update/change_status)"
                    },
                    "assigneeId": {
                        "type": "string",
                        "description": "Assignee member ID (for assign action)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Task priority (for create/update)"
                    }
                },
                "required": ["action"]
            }
        ),
        types.Tool(
            name="dooray_comments",
            description="Manage Dooray task comments - get list, create, update, delete comments with mention support",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "update", "delete"],
                        "description": "Action to perform on comments"
                    },
                    "taskId": {
                        "type": "string",
                        "description": "Task ID (required)"
                    },
                    "commentId": {
                        "type": "string",
                        "description": "Comment ID (required for update/delete)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Comment content (for create/update)"
                    },
                    "mentions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "User IDs to mention (optional)"
                    }
                },
                "required": ["action", "taskId"]
            }
        ),
        types.Tool(
            name="dooray_tags",
            description="Manage Dooray tags - list available tags, create new tags, add/remove tags from tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "add_to_task", "remove_from_task"],
                        "description": "Action to perform on tags"
                    },
                    "projectId": {
                        "type": "string",
                        "description": "Project ID (required for list/create)"
                    },
                    "taskId": {
                        "type": "string",
                        "description": "Task ID (required for add_to_task/remove_from_task)"
                    },
                    "tagName": {
                        "type": "string",
                        "description": "Tag name (for create/add_to_task/remove_from_task)"
                    },
                    "tagColor": {
                        "type": "string",
                        "description": "Tag color (for create action, optional)"
                    }
                },
                "required": ["action"]
            }
        ),
        types.Tool(
            name="dooray_search",
            description="Search Dooray content - tasks by various criteria, filter by status/assignee/tags/date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "searchType": {
                        "type": "string",
                        "enum": ["tasks", "by_assignee", "by_status", "by_tag", "by_date_range"],
                        "description": "Type of search to perform"
                    },
                    "projectId": {
                        "type": "string",
                        "description": "Project ID (required for most searches)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query text (for tasks search)"
                    },
                    "assigneeId": {
                        "type": "string",
                        "description": "Assignee ID (for by_assignee search)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Task status (for by_status search)"
                    },
                    "tagName": {
                        "type": "string",
                        "description": "Tag name (for by_tag search)"
                    },
                    "startDate": {
                        "type": "string",
                        "description": "Start date (for by_date_range search)"
                    },
                    "endDate": {
                        "type": "string",
                        "description": "End date (for by_date_range search)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (optional)"
                    }
                },
                "required": ["searchType"]
            }
        ),
        types.Tool(
            name="dooray_members",
            description="Manage Dooray members - search by email/ID, get member details, check project membership",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["search_by_email", "search_by_id", "get_details", "list_project_members"],
                        "description": "Action to perform on members"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address (for search_by_email)"
                    },
                    "userId": {
                        "type": "string",
                        "description": "User ID (for search_by_id/get_details)"
                    },
                    "projectId": {
                        "type": "string",
                        "description": "Project ID (for list_project_members)"
                    }
                },
                "required": ["action"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    """Handle tool calls from Claude."""
    global dooray_client
    
    if not dooray_client:
        return [types.TextContent(
            type="text",
            text="Error: Dooray client not initialized. Please check your DOORAY_API_TOKEN environment variable."
        )]
    
    try:
        if name == "dooray_tasks":
            tool = TasksTool(dooray_client)
            result = await tool.handle(arguments or {})
        elif name == "dooray_comments":
            tool = CommentsTool(dooray_client)
            result = await tool.handle(arguments or {})
        elif name == "dooray_tags":
            tool = TagsTool(dooray_client)
            result = await tool.handle(arguments or {})
        elif name == "dooray_search":
            tool = SearchTool(dooray_client)
            result = await tool.handle(arguments or {})
        elif name == "dooray_members":
            tool = MembersTool(dooray_client)
            result = await tool.handle(arguments or {})
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        return [types.TextContent(type="text", text=str(result))]
        
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}")
        return [types.TextContent(
            type="text", 
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main entry point for the MCP server."""
    global dooray_client, default_project_id
    
    # Initialize Dooray client
    api_token = os.getenv("DOORAY_API_TOKEN")
    base_url = os.getenv("DOORAY_BASE_URL", "https://api.dooray.com")
    default_project_id = os.getenv("DOORAY_DEFAULT_PROJECT_ID")
    
    if not api_token:
        logger.error("DOORAY_API_TOKEN environment variable is required")
        sys.exit(1)
    
    dooray_client = DoorayClient(api_token, base_url)
    logger.info(f"Dooray MCP Server starting... (Default Project: {default_project_id})")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dooray-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
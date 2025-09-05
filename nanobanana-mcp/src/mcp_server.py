#!/usr/bin/env python3
"""Standard MCP server for Nanobanana (Gemini 2.5 Flash Image)."""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import MCP modules
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

from config import Config
from gemini_client import GeminiImageClient
from tools.generate_image import GenerateImageTool
from tools.edit_image import EditImageTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the server instance
server = Server("nanobanana")

# Initialize components
Config.validate()
gemini_client = GeminiImageClient()
generate_tool = GenerateImageTool(gemini_client)
edit_tool = EditImageTool(gemini_client)

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="nanobanana_generate",
            description="Generate images from text prompts using Gemini 2.5 Flash Image",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description for image generation (Korean/English supported)"
                    },
                    "style": {
                        "type": "string", 
                        "enum": ["photo", "illustration", "art", "sketch"],
                        "default": "photo",
                        "description": "Image style"
                    },
                    "quality": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "default": "high", 
                        "description": "Quality setting"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="nanobanana_edit",
            description="Edit or transform existing images using natural language instructions",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file to edit"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Editing instructions in natural language"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["preserve", "enhance", "transform"],
                        "default": "preserve",
                        "description": "Style to apply"
                    }
                },
                "required": ["image_path", "instruction"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "nanobanana_generate":
            result = await generate_tool.generate_image(
                prompt=arguments["prompt"],
                style=arguments.get("style", "photo"),
                quality=arguments.get("quality", "high")
            )
            return [TextContent(type="text", text=str(result))]
            
        elif name == "nanobanana_edit":
            result = await edit_tool.edit_image(
                image_path=arguments["image_path"],
                instruction=arguments["instruction"],
                style=arguments.get("style", "preserve")
            )
            return [TextContent(type="text", text=str(result))]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main server entry point."""
    # Import here to avoid issues with asyncio
    from mcp.server.stdio import stdio_server
    
    logger.info(f"Starting {Config.MCP_SERVER_NAME} MCP server v{Config.MCP_SERVER_VERSION}")
    logger.info(f"Using model: {Config.GEMINI_MODEL}")
    logger.info(f"Vertex AI mode: {Config.GOOGLE_GENAI_USE_VERTEXAI}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nanobanana",
                server_version=Config.MCP_SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
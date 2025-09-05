"""Main MCP server for Nanobanana (Gemini 2.5 Flash Image)."""

import asyncio
import sys
import os
from pathlib import Path
from typing import Any, Dict
from loguru import logger

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from fastmcp import FastMCP
from config import Config
from gemini_client import GeminiImageClient
from tools.generate_image import GenerateImageTool
from tools.edit_image import EditImageTool


class NanobananaMCPServer:
    """Main MCP server class."""
    
    def __init__(self):
        """Initialize the MCP server."""
        # Validate configuration
        Config.validate()
        
        # Setup logging
        logger.remove()
        logger.add(
            sys.stderr,
            level=Config.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        # Initialize FastMCP server
        self.mcp = FastMCP(Config.MCP_SERVER_NAME)
        
        # Initialize Gemini client
        self.gemini_client = GeminiImageClient()
        
        # Initialize tools
        self.generate_tool = GenerateImageTool(self.gemini_client)
        self.edit_tool = EditImageTool(self.gemini_client)
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self) -> None:
        """Register MCP tools."""
        
        @self.mcp.tool()
        async def nanobanana_generate(
            prompt: str,
            style: str = "photo",
            quality: str = "high"
        ) -> Dict[str, Any]:
            """
            Generate images from text prompts using Gemini 2.5 Flash Image.
            
            Args:
                prompt: Text description for image generation (Korean/English supported)
                style: Image style (photo, illustration, art, sketch)
                quality: Quality setting (high, medium, low)
                
            Returns:
                Dictionary containing image data, file path, and description
            """
            logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            try:
                result = await self.generate_tool.generate_image(
                    prompt=prompt,
                    style=style,
                    quality=quality
                )
                
                logger.success("Image generated successfully")
                return result
                
            except Exception as e:
                logger.error(f"Failed to generate image: {str(e)}")
                raise
        
        @self.mcp.tool()
        async def nanobanana_edit(
            image_path: str,
            instruction: str,
            style: str = "preserve"
        ) -> Dict[str, Any]:
            """
            Edit or transform existing images using natural language instructions.
            
            Args:
                image_path: Path to the image file to edit
                instruction: Editing instructions in natural language
                style: Style to apply (preserve, enhance, transform)
                
            Returns:
                Dictionary containing edited image data, file path, and description
            """
            logger.info(f"Editing image: {image_path} with instruction: {instruction[:50]}...")
            
            try:
                result = await self.edit_tool.edit_image(
                    image_path=image_path,
                    instruction=instruction,
                    style=style
                )
                
                logger.success("Image edited successfully")
                return result
                
            except Exception as e:
                logger.error(f"Failed to edit image: {str(e)}")
                raise
                
    def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting {Config.MCP_SERVER_NAME} MCP server v{Config.MCP_SERVER_VERSION}")
        logger.info(f"Using model: {Config.GEMINI_MODEL}")
        logger.info(f"Vertex AI mode: {Config.GOOGLE_GENAI_USE_VERTEXAI}")
        
        # FastMCP handles its own event loop - no await needed
        self.mcp.run()


if __name__ == "__main__":
    """Main entry point."""
    server = NanobananaMCPServer()
    server.run()
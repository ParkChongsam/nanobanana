"""Image generation tool for Nanobanana MCP Server."""

from typing import Dict, Any
from pathlib import Path
import hashlib
from datetime import datetime

from loguru import logger
from PIL import Image

from src.gemini_client import GeminiImageClient
from src.config import Config


class GenerateImageTool:
    """Tool for generating images from text prompts."""
    
    def __init__(self, gemini_client: GeminiImageClient):
        """Initialize the generation tool."""
        self.client = gemini_client
        
    async def generate_image(
        self,
        prompt: str,
        style: str = "photo",
        quality: str = "high"
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description for image generation
            style: Image style (photo, illustration, art, sketch, digital_art, painting)
            quality: Quality setting (high, medium, low)
            
        Returns:
            Dictionary containing:
            - success: bool
            - description: Generated description text
            - image_path: Path to saved image file
            - image_data: Base64 encoded image
            - metadata: Generation metadata
        """
        
        try:
            logger.info(f"Starting image generation with style: {style}, quality: {quality}")
            
            # Optimize prompt based on style and quality (now includes quality handling)
            optimized_prompt = self.client._optimize_prompt(prompt, style, quality)
            
            logger.info(f"Optimized prompt: {optimized_prompt}")
            
            # Generate content using Gemini
            result = await self.client.generate_content(optimized_prompt)
            
            if not result["images"]:
                raise ValueError("No images were generated")
            
            # Get the first (and typically only) generated image
            image_data = result["images"][0]
            image = image_data["image"]
            
            # Generate intelligent filename based on prompt
            filename = self._generate_filename(prompt, style)
            
            # Save image to disk
            saved_path = self.client.save_image(
                image=image,
                filename=filename,
                prefix="generated"
            )
            
            # Prepare metadata
            metadata = {
                "original_prompt": prompt,
                "optimized_prompt": optimized_prompt,
                "style": style,
                "quality": quality,
                "model": Config.GEMINI_MODEL,
                "timestamp": datetime.now().isoformat(),
                "image_size": image.size,
                "image_format": image_data["format"],
                "file_size": saved_path.stat().st_size if saved_path.exists() else 0
            }
            
            # Return comprehensive result (without large base64 data to prevent MCP response size issues)
            return {
                "success": True,
                "description": result["text"].strip() if result["text"] else f"Generated image: {prompt}",
                "image_path": str(saved_path.absolute()),
                "file_size_mb": round(saved_path.stat().st_size / (1024 * 1024), 2) if saved_path.exists() else 0,
                "metadata": metadata,
                "prompt_translation": {
                    "original": prompt,
                    "optimized": optimized_prompt,
                    "auto_translated": Config.AUTO_TRANSLATE
                }
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "description": f"Failed to generate image: {str(e)}",
                "metadata": {
                    "original_prompt": prompt,
                    "style": style,
                    "quality": quality,
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
            }
    
    def _generate_filename(self, prompt: str, style: str) -> str:
        """Generate an intelligent filename based on the prompt."""
        
        # Clean and truncate prompt for filename
        clean_prompt = "".join(c for c in prompt if c.isalnum() or c in ' -_')
        clean_prompt = clean_prompt.replace(' ', '_').lower()[:30]
        
        # Create hash for uniqueness
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine elements
        filename = f"{clean_prompt}_{style}_{timestamp}_{prompt_hash}.png"
        
        return filename
    
    def get_supported_styles(self) -> Dict[str, str]:
        """Get list of supported image styles."""
        return {
            "photo": "High-quality photographic style",
            "illustration": "Detailed illustration artwork", 
            "art": "Artistic rendering with creative interpretation",
            "sketch": "Hand-drawn pencil sketch style",
            "digital_art": "Modern digital artwork",
            "painting": "Traditional painted artwork style"
        }
    
    def get_supported_qualities(self) -> Dict[str, str]:
        """Get list of supported quality settings."""
        return {
            "high": "Maximum quality with fine details (8K, ultra-detailed)",
            "medium": "Good quality with clear details (high resolution)", 
            "low": "Simple style with basic details"
        }
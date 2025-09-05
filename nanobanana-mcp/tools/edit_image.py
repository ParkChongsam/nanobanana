"""Image editing tool for Nanobanana MCP Server."""

from typing import Dict, Any, Union
from pathlib import Path
import hashlib
from datetime import datetime

from loguru import logger
from PIL import Image

from src.gemini_client import GeminiImageClient
from src.config import Config


class EditImageTool:
    """Tool for editing and transforming existing images."""
    
    def __init__(self, gemini_client: GeminiImageClient):
        """Initialize the editing tool."""
        self.client = gemini_client
        
    async def edit_image(
        self,
        image_path: str,
        instruction: str,
        style: str = "preserve"
    ) -> Dict[str, Any]:
        """
        Edit or transform an existing image using natural language instructions.
        
        Args:
            image_path: Path to the image file to edit
            instruction: Editing instructions in natural language
            style: Style to apply (preserve, enhance, transform, artistic)
            
        Returns:
            Dictionary containing:
            - success: bool
            - description: Generated description text
            - image_path: Path to edited image file
            - image_data: Base64 encoded image
            - metadata: Editing metadata
        """
        
        try:
            logger.info(f"Starting image editing: {image_path}")
            
            # Validate input image
            input_path = Path(image_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if not self._is_valid_image(input_path):
                raise ValueError(f"Invalid image file: {image_path}")
            
            # Load input image
            input_image = Image.open(input_path)
            logger.info(f"Loaded image: {input_image.size} {input_image.format}")
            
            # Optimize instruction based on style
            optimized_instruction = self._optimize_instruction(instruction, style, input_image)
            
            logger.info(f"Optimized instruction: {optimized_instruction}")
            
            # Generate edited content using Gemini
            result = await self.client.generate_content(
                prompt=optimized_instruction,
                input_image=input_image
            )
            
            if not result["images"]:
                raise ValueError("No edited images were generated")
            
            # Get the edited image
            image_data = result["images"][0]
            edited_image = image_data["image"]
            
            # Generate filename for edited image
            filename = self._generate_edited_filename(input_path, instruction, style)
            
            # Save edited image
            saved_path = self.client.save_image(
                image=edited_image,
                filename=filename,
                prefix="edited"
            )
            
            # Prepare metadata
            metadata = {
                "original_image": str(input_path.absolute()),
                "original_size": input_image.size,
                "original_format": input_image.format,
                "instruction": instruction,
                "optimized_instruction": optimized_instruction,
                "style": style,
                "model": Config.GEMINI_MODEL,
                "timestamp": datetime.now().isoformat(),
                "edited_size": edited_image.size,
                "edited_format": image_data["format"],
                "file_size": saved_path.stat().st_size if saved_path.exists() else 0
            }
            
            # Return comprehensive result (without large base64 data to prevent MCP response size issues)
            return {
                "success": True,
                "description": result["text"].strip() if result["text"] else f"Edited image: {instruction}",
                "image_path": str(saved_path.absolute()),
                "original_path": str(input_path.absolute()),
                "file_size_mb": round(saved_path.stat().st_size / (1024 * 1024), 2) if saved_path.exists() else 0,
                "metadata": metadata,
                "instruction_processing": {
                    "original": instruction,
                    "optimized": optimized_instruction,
                    "style_applied": style,
                    "auto_translated": Config.AUTO_TRANSLATE
                }
            }
            
        except Exception as e:
            logger.error(f"Image editing failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "description": f"Failed to edit image: {str(e)}",
                "metadata": {
                    "original_image": image_path,
                    "instruction": instruction,
                    "style": style,
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__
                }
            }
    
    def _optimize_instruction(self, instruction: str, style: str, input_image: Image.Image) -> str:
        """Optimize editing instruction for better results."""
        
        # Translate to English if needed
        optimized = self.client._translate_to_english(instruction)
        
        # Add style-specific prefixes
        style_prefixes = {
            "preserve": "Edit this image while preserving its original style:",
            "enhance": "Enhance and improve this image:",
            "transform": "Transform this image by:",
            "artistic": "Apply artistic transformation to this image:",
            "photorealistic": "Make this image more photorealistic:",
            "stylized": "Apply stylized effects to this image:"
        }
        
        if style in style_prefixes:
            optimized = f"{style_prefixes[style]} {optimized}"
        
        # Add image context information
        optimized += f" The input image is {input_image.size[0]}x{input_image.size[1]} pixels in {input_image.format} format."
        
        # Add text exclusion if enabled
        if Config.ADD_TEXT_EXCLUSION:
            optimized += " Do not add any text, letters, or words to the image."
        
        # Add quality instruction
        optimized += " Maintain high quality and detail in the output."
        
        return optimized
    
    def _generate_edited_filename(self, original_path: Path, instruction: str, style: str) -> str:
        """Generate filename for edited image."""
        
        # Get original filename without extension
        base_name = original_path.stem
        
        # Clean instruction for filename
        clean_instruction = "".join(c for c in instruction if c.isalnum() or c in ' -_')
        clean_instruction = clean_instruction.replace(' ', '_').lower()[:20]
        
        # Create hash for uniqueness
        instruction_hash = hashlib.md5(instruction.encode()).hexdigest()[:6]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Combine elements
        filename = f"{base_name}_edited_{clean_instruction}_{style}_{timestamp}_{instruction_hash}.png"
        
        return filename
    
    def _is_valid_image(self, file_path: Path) -> bool:
        """Check if file is a valid image."""
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def get_supported_styles(self) -> Dict[str, str]:
        """Get list of supported editing styles."""
        return {
            "preserve": "Maintain original style while making requested changes",
            "enhance": "Improve quality and details of the image",
            "transform": "Apply significant transformations to the image",
            "artistic": "Apply artistic effects and creative transformations", 
            "photorealistic": "Make the image more photorealistic",
            "stylized": "Apply stylized visual effects"
        }
    
    def get_supported_formats(self) -> list:
        """Get list of supported image formats."""
        return [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"]
    
    async def batch_edit(
        self,
        image_paths: list,
        instruction: str,
        style: str = "preserve"
    ) -> Dict[str, Any]:
        """
        Edit multiple images with the same instruction.
        
        Args:
            image_paths: List of image file paths
            instruction: Common editing instruction
            style: Style to apply to all images
            
        Returns:
            Dictionary with results for each image
        """
        results = {}
        
        for image_path in image_paths:
            try:
                result = await self.edit_image(image_path, instruction, style)
                results[image_path] = result
            except Exception as e:
                results[image_path] = {
                    "success": False,
                    "error": str(e),
                    "description": f"Batch edit failed for {image_path}: {str(e)}"
                }
        
        return {
            "batch_results": results,
            "total_images": len(image_paths),
            "successful": len([r for r in results.values() if r.get("success", False)]),
            "failed": len([r for r in results.values() if not r.get("success", False)])
        }
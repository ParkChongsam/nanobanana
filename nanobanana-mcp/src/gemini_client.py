"""Gemini API client for image generation and editing."""

import base64
import asyncio
from typing import Dict, Any, List, Optional, Union
from io import BytesIO
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai.types import GenerateContentConfig, Modality
from PIL import Image
from loguru import logger
from googletrans import Translator

from config import Config


class GeminiImageClient:
    """Client for Gemini 2.5 Flash Image API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        # Initialize client with proper authentication
        if Config.GOOGLE_GENAI_USE_VERTEXAI:
            # Vertex AI mode
            self.client = genai.Client(
                vertexai=True,
                project=Config.GOOGLE_CLOUD_PROJECT,
                location=Config.GOOGLE_CLOUD_LOCATION
            )
            logger.info(f"Using Vertex AI with project: {Config.GOOGLE_CLOUD_PROJECT}")
        else:
            # Direct API mode
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            logger.info("Using Gemini API with direct API key")
        
        self.translator = Translator() if Config.AUTO_TRANSLATE else None
        self.config = self._get_generation_config()
        
        logger.info(f"Initialized Gemini client with model: {Config.GEMINI_MODEL}")
        
    def _get_generation_config(self) -> GenerateContentConfig:
        """Get generation configuration for Gemini API."""
        return GenerateContentConfig(
            response_modalities=[Modality.TEXT, Modality.IMAGE],  # Required: both TEXT and IMAGE
            candidate_count=min(Config.MAX_CANDIDATE_COUNT, 8)  # Max 8 candidates
        )
    
    def _translate_to_english(self, text: str) -> str:
        """Translate text to English if needed."""
        if not Config.AUTO_TRANSLATE or not self.translator:
            return text
            
        try:
            # Detect language
            detected = self.translator.detect(text)
            
            if detected.lang != 'en':
                translated = self.translator.translate(text, src=detected.lang, dest='en')
                logger.info(f"Translated prompt from {detected.lang} to English")
                return translated.text
            
        except Exception as e:
            logger.warning(f"Translation failed, using original text: {e}")
            
        return text
    
    def _optimize_prompt(self, prompt: str, style: str = "photo", quality: str = "high") -> str:
        """Optimize prompt for better image generation with smart text handling."""
        # Translate to English if needed
        optimized = self._translate_to_english(prompt)
        
        # Add style indicators
        style_prefixes = {
            "photo": "A high-quality photograph of",
            "illustration": "A detailed illustration of", 
            "art": "An artistic rendering of",
            "sketch": "A pencil sketch of",
            "digital_art": "A digital artwork of",
            "painting": "A painted image of"
        }
        
        if style in style_prefixes and not optimized.lower().startswith(("a ", "an ", "the ")):
            optimized = f"{style_prefixes[style]} {optimized}"
        
        # Smart text handling - check if user wants text in image
        text_indicators = ["sign", "placard", "banner", "text", "writing", "words", "letters", "팻말", "간판", "글자", "텍스트", "signboard", "written", "bold", "clear text"]
        wants_text = any(indicator in optimized.lower() for indicator in text_indicators)
        
        # Enhanced Korean text detection
        korean_text_patterns = ["참좋은복사기", "한글", "글씨", "문자"]
        has_korean_text = any(pattern in optimized for pattern in korean_text_patterns)
        
        logger.info(f"Text detection - wants_text: {wants_text}, has_korean_text: {has_korean_text}")
        
        if wants_text or has_korean_text:
            # User wants text - add instructions for clear text rendering (NEVER exclude text when requested)
            optimized += ". Ensure any text is clearly visible, readable, and properly aligned with high contrast"
            logger.info("Added text visibility instructions")
        # Completely removed text exclusion logic to fix the text generation issue
            
        # Add quality indicators
        quality_suffixes = {
            "high": ", 8K resolution, ultra-detailed, masterpiece quality",
            "medium": ", good quality, clear details", 
            "low": ", simple style"
        }
        
        if quality in quality_suffixes:
            optimized += quality_suffixes[quality]
        
        return optimized
    
    async def generate_content(
        self,
        prompt: str,
        input_image: Optional[Union[str, bytes, Image.Image]] = None
    ) -> Dict[str, Any]:
        """Generate content using Gemini API."""
        
        try:
            # Prepare contents
            contents = [prompt]
            
            # Add input image if provided
            if input_image is not None:
                if isinstance(input_image, str):
                    # File path
                    with open(input_image, 'rb') as f:
                        image_data = f.read()
                elif isinstance(input_image, bytes):
                    # Raw bytes
                    image_data = input_image
                elif isinstance(input_image, Image.Image):
                    # PIL Image
                    buffer = BytesIO()
                    input_image.save(buffer, format='PNG')
                    image_data = buffer.getvalue()
                else:
                    raise ValueError("Unsupported input image format")
                
                # Add image to contents
                contents.append(Image.open(BytesIO(image_data)))
            
            # Generate content with simplified config
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=Config.GEMINI_MODEL,
                contents=contents,
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE],
                    candidate_count=1
                )
            )
            
            # Process response
            result = {"text": "", "images": []}
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                for part in candidate.content.parts:
                    if part.text:
                        result["text"] += part.text
                    elif part.inline_data:
                        # Convert image data to PIL Image
                        image_bytes = part.inline_data.data
                        image = Image.open(BytesIO(image_bytes))
                        
                        # Save image first to avoid large data in MCP response
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        temp_filename = f"temp_generated_{timestamp}.png"
                        saved_path = self.save_image(image, temp_filename, "generated")
                        
                        result["images"].append({
                            # "image": image,  # REMOVED: PIL Image causes MCP response size issues
                            "format": image.format or "PNG",
                            "size": list(image.size),  # Convert tuple to list for JSON serialization
                            "width": image.size[0],
                            "height": image.size[1],
                            "saved_path": str(saved_path),
                            "file_exists": saved_path.exists()
                            # All binary data removed to prevent MCP response size issues
                        })
            
            logger.info(f"Generated {len(result['images'])} image(s) with text: {result['text'][:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate content: {str(e)}")
            raise
    
    def save_image(
        self,
        image: Image.Image,
        filename: Optional[str] = None,
        prefix: str = "nanobanana"
    ) -> Path:
        """Save image to disk with intelligent filename."""
        import uuid
        import hashlib
        from datetime import datetime
        
        if filename is None:
            # Generate intelligent filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{prefix}_{timestamp}_{unique_id}.png"
        
        file_path = Config.IMAGE_SAVE_PATH / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image
        image.save(file_path, format="PNG", optimize=True)
        
        logger.info(f"Saved image to: {file_path}")
        return file_path
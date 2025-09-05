"""Tests for image generation functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.gemini_client import GeminiImageClient
from tools.generate_image import GenerateImageTool


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    client = Mock(spec=GeminiImageClient)
    client._optimize_prompt = Mock(return_value="optimized test prompt")
    client.generate_content = AsyncMock(return_value={
        "text": "Test generated image description",
        "images": [{
            "image": Mock(),
            "bytes": b"fake_image_data",
            "base64": "ZmFrZV9pbWFnZV9kYXRh",
            "format": "PNG"
        }]
    })
    client.save_image = Mock(return_value=Path("test_image.png"))
    return client


@pytest.fixture
def generate_tool(mock_gemini_client):
    """Generate tool instance with mocked client."""
    return GenerateImageTool(mock_gemini_client)


class TestGenerateImageTool:
    """Test cases for GenerateImageTool."""
    
    @pytest.mark.asyncio
    async def test_generate_image_success(self, generate_tool, mock_gemini_client):
        """Test successful image generation."""
        result = await generate_tool.generate_image(
            prompt="A beautiful sunset",
            style="photo",
            quality="high"
        )
        
        assert result["success"] is True
        assert "description" in result
        assert "image_path" in result
        assert "image_data" in result
        assert "metadata" in result
        
        # Verify client calls
        mock_gemini_client._optimize_prompt.assert_called_once()
        mock_gemini_client.generate_content.assert_called_once()
        mock_gemini_client.save_image.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_image_failure(self, generate_tool, mock_gemini_client):
        """Test image generation failure handling."""
        mock_gemini_client.generate_content.side_effect = Exception("API Error")
        
        result = await generate_tool.generate_image(
            prompt="Test prompt",
            style="art",
            quality="medium"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "API Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_generate_image_no_images(self, generate_tool, mock_gemini_client):
        """Test handling when no images are generated."""
        mock_gemini_client.generate_content.return_value = {
            "text": "No images generated",
            "images": []
        }
        
        result = await generate_tool.generate_image(
            prompt="Test prompt",
            style="sketch",
            quality="low"
        )
        
        assert result["success"] is False
        assert "No images were generated" in result["error"]
    
    def test_generate_filename(self, generate_tool):
        """Test filename generation."""
        filename = generate_tool._generate_filename("A beautiful sunset over mountains", "photo")
        
        assert filename.endswith(".png")
        assert "photo" in filename
        assert len(filename) > 10  # Should have meaningful content
    
    def test_get_supported_styles(self, generate_tool):
        """Test getting supported styles."""
        styles = generate_tool.get_supported_styles()
        
        assert isinstance(styles, dict)
        assert "photo" in styles
        assert "illustration" in styles
        assert "art" in styles
    
    def test_get_supported_qualities(self, generate_tool):
        """Test getting supported qualities."""
        qualities = generate_tool.get_supported_qualities()
        
        assert isinstance(qualities, dict)
        assert "high" in qualities
        assert "medium" in qualities  
        assert "low" in qualities


if __name__ == "__main__":
    pytest.main([__file__])
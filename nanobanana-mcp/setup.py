"""Setup script for Nanobanana MCP Server."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt" 
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() 
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="nanobanana-mcp",
    version="1.0.0",
    author="Claude Code Assistant",
    author_email="noreply@anthropic.com",
    description="MCP server for Gemini 2.5 Flash Image (nanobanana) with image generation and editing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ParkChongsam/nanobanana-mcp",
    packages=find_packages(include=["src", "src.*", "tools", "tools.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "nanobanana-mcp=src.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=["mcp", "gemini", "nanobanana", "image-generation", "ai", "google", "claude"],
)
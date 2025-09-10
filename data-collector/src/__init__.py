"""
Data Collector - API Specification Processing and Conversion

A comprehensive tool for converting various API specification formats
(Swagger/OpenAPI, WSDL) into a common structure for vector database storage.
"""

__version__ = "1.0.0"
__author__ = "CatalystAI Team"
__email__ = "team@catalystai.com"
__description__ = "API Specification Processing and Conversion Tool"

from .connectors import SwaggerConnector, WSDLConnector, APIConnectorManager
from .models import CommonAPISpec
from .utils import APISpecChunker, ChunkingConfig, ChunkingStrategy, Chunk

__all__ = [
    "SwaggerConnector",
    "WSDLConnector", 
    "APIConnectorManager",
    "CommonAPISpec",
    "APISpecChunker",
    "ChunkingConfig",
    "ChunkingStrategy",
    "Chunk",
]

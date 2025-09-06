"""
Data Models Module

This module contains data models and schemas for API specifications.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class CommonAPISpec:
    """Common structure for API specifications"""
    api_name: str
    version: str
    description: str
    base_url: str
    category: str
    endpoints: List[Dict[str, Any]]
    authentication: Dict[str, Any]
    rate_limits: Dict[str, Any]
    pricing: Optional[str]
    sdk_languages: List[str]
    documentation_url: str
    integration_steps: List[str]
    best_practices: List[str]
    common_use_cases: List[str]
    tags: List[str]
    contact_info: Dict[str, str]
    license_info: Dict[str, str]
    external_docs: List[Dict[str, str]]
    examples: List[Dict[str, Any]]
    schema_version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""

__all__ = ["CommonAPISpec"]

#!/usr/bin/env python3
"""
Data Collector - API Specification Processing and Conversion

A comprehensive tool for converting various API specification formats
(Swagger/OpenAPI, WSDL) into a common structure for vector database storage.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Data Collector - API Specification Processing and Conversion"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="data-collector",
    version="1.0.0",
    author="CatalystAI Team",
    author_email="team@catalystai.com",
    description="API Specification Processing and Conversion Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/catalystai/data-collector",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "data-collector=data_collector.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "data_collector": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="api, swagger, openapi, wsdl, data-collection, vector-database, chromadb",
    project_urls={
        "Bug Reports": "https://github.com/catalystai/data-collector/issues",
        "Source": "https://github.com/catalystai/data-collector",
        "Documentation": "https://data-collector.readthedocs.io/",
    },
)

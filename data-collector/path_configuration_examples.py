#!/usr/bin/env python3
"""
Examples of how to set input and output directory paths for the SOAP converter
"""

import os
import subprocess
from pathlib import Path

def example_1_command_line_args():
    """Example 1: Using command line arguments"""
    print("🔧 Example 1: Command Line Arguments")
    print("=" * 50)
    
    examples = [
        "# Using long form arguments",
        "python soap_converter.py --input-dir ./my_wsdl_files --output-dir ./my_output",
        "",
        "# Using short form arguments", 
        "python soap_converter.py -i ./soap_services -o ./converted_json",
        "",
        "# Using absolute paths",
        "python soap_converter.py --input-dir /Users/username/soap_files --output-dir /Users/username/api_specs",
        "",
        "# Using relative paths",
        "python soap_converter.py -i ../wsdl_files -o ../output"
    ]
    
    for example in examples:
        print(example)

def example_2_environment_variables():
    """Example 2: Using environment variables"""
    print("\n🔧 Example 2: Environment Variables")
    print("=" * 50)
    
    examples = [
        "# Set environment variables",
        "export SOAP_INPUT_DIR=/path/to/your/wsdl/files",
        "export SOAP_OUTPUT_DIR=/path/to/your/output",
        "python soap_converter.py",
        "",
        "# Or set them inline",
        "SOAP_INPUT_DIR=./soap_files SOAP_OUTPUT_DIR=./output python soap_converter.py",
        "",
        "# In a script or .env file",
        "echo 'SOAP_INPUT_DIR=./input' >> .env",
        "echo 'SOAP_OUTPUT_DIR=./output' >> .env"
    ]
    
    for example in examples:
        print(example)

def example_3_default_directories():
    """Example 3: Using default directories"""
    print("\n🔧 Example 3: Default Directories")
    print("=" * 50)
    
    examples = [
        "# Uses default directories: ./input and ./output",
        "python soap_converter.py",
        "",
        "# Make sure directories exist",
        "mkdir -p input output",
        "cp your_wsdl_files/*.wsdl input/",
        "cp your_xsd_files/*.xsd input/",
        "python soap_converter.py"
    ]
    
    for example in examples:
        print(example)

def example_4_programmatic_usage():
    """Example 4: Programmatic usage"""
    print("\n🔧 Example 4: Programmatic Usage")
    print("=" * 50)
    
    code_example = '''
from soap_converter import SOAPConverter
from pathlib import Path

# Create converter with custom paths
converter = SOAPConverter(
    input_dir="/path/to/your/wsdl/files",
    output_dir="/path/to/your/output",
    chunking_strategy="ENDPOINT_BASED"
)

# Process all files
converter.process_all_files()
'''
    
    print(code_example)

def example_5_directory_structure():
    """Example 5: Recommended directory structure"""
    print("\n🔧 Example 5: Recommended Directory Structure")
    print("=" * 50)
    
    structure = '''
project/
├── soap_converter.py
├── input/                    # Default input directory
│   ├── service1.wsdl
│   ├── service1.xsd
│   ├── service2.wsdl
│   └── external-types.xsd
├── output/                   # Default output directory
│   ├── service1_20250912_120000.json
│   └── service2_20250912_120001.json
└── custom_input/             # Custom input directory
    ├── enterprise/
    │   ├── user-service.wsdl
    │   └── user-types.xsd
    └── payment/
        ├── payment-service.wsdl
        └── payment-types.xsd
'''
    
    print(structure)

def example_6_practical_examples():
    """Example 6: Practical usage examples"""
    print("\n🔧 Example 6: Practical Usage Examples")
    print("=" * 50)
    
    examples = [
        "# Convert all WSDL files in current directory",
        "python soap_converter.py -i . -o ./converted",
        "",
        "# Convert files from a specific service directory",
        "python soap_converter.py --input-dir ./services/user-service --output-dir ./api-specs",
        "",
        "# Convert with different chunking strategy",
        "python soap_converter.py -i ./soap_files -o ./output --chunking-strategy SEMANTIC",
        "",
        "# Batch convert multiple service directories",
        "for dir in ./services/*/; do",
        "    service_name=$(basename \"$dir\")",
        "    python soap_converter.py -i \"$dir\" -o \"./output/$service_name\"",
        "done"
    ]
    
    for example in examples:
        print(example)

def main():
    """Show all examples"""
    print("📚 SOAP Converter: Input and Output Directory Configuration")
    print("=" * 70)
    
    example_1_command_line_args()
    example_2_environment_variables()
    example_3_default_directories()
    example_4_programmatic_usage()
    example_5_directory_structure()
    example_6_practical_examples()
    
    print("\n🎯 Quick Reference:")
    print("=" * 20)
    print("Command Line: python soap_converter.py -i INPUT_DIR -o OUTPUT_DIR")
    print("Environment:  export SOAP_INPUT_DIR=INPUT_DIR && export SOAP_OUTPUT_DIR=OUTPUT_DIR")
    print("Default:      python soap_converter.py  # Uses ./input and ./output")
    print("Help:         python soap_converter.py --help")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Example usage of the SOAP to CommonAPISpec converter

This script demonstrates how to use the standalone converter programmatically.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from soap_converter import SOAPConverter

def main():
    """Example usage of the SOAP converter"""
    
    print("🔧 SOAP Converter Example")
    print("=" * 40)
    
    # Define directories
    input_dir = "input"
    output_dir = "output"
    
    # Create converter instance
    converter = SOAPConverter(
        input_dir=input_dir,
        output_dir=output_dir,
        chunking_strategy="ENDPOINT_BASED"
    )
    
    # Process all files
    converter.process_all_files()
    
    print("\n✅ Example completed!")
    print(f"📁 Check the '{output_dir}' directory for generated JSON files")

if __name__ == "__main__":
    main()

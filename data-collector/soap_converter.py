#!/usr/bin/env python3
"""
Standalone SOAP to CommonAPISpec Converter

This script converts WSDL and XSD files to CommonAPISpec JSON format.
It processes all WSDL and XSD files from an input directory and outputs
the results to an output directory.

Usage:
    python soap_converter.py --input-dir /path/to/wsdl/files --output-dir /path/to/output
    python soap_converter.py -i ./soap_files -o ./output
    python soap_converter.py  # Uses default directories: ./input and ./output

Features:
    - Processes multiple WSDL files with XSD dependencies
    - Automatically detects WSDL and XSD files
    - Handles external XSD dependencies
    - Generates CommonAPISpec JSON files
    - Provides detailed processing logs
    - Error handling and recovery
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from connectors.api_connector import APIConnectorManager, WSDLConnector
    from utils.chunking import ChunkingConfig, ChunkingStrategy
    from models import CommonAPISpec
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running this script from the data-collector directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('soap_converter.log')
    ]
)
logger = logging.getLogger(__name__)

class SOAPConverter:
    """Standalone SOAP to CommonAPISpec converter"""
    
    def __init__(self, input_dir: str, output_dir: str, chunking_strategy: str = "ENDPOINT_BASED"):
        """
        Initialize the SOAP converter
        
        Args:
            input_dir: Directory containing WSDL and XSD files
            output_dir: Directory to output CommonAPISpec JSON files
            chunking_strategy: Chunking strategy for ChromaDB storage
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunking_strategy = chunking_strategy
        
        # Initialize API connector manager
        self.chunking_config = ChunkingConfig(
            strategy=getattr(ChunkingStrategy, chunking_strategy.upper()),
            chunk_size=512,
            chunk_overlap=50,
            max_chunks_per_spec=20,
            min_chunk_size=100,
            max_chunk_size=2048
        )
        
        self.api_manager = APIConnectorManager(self.chunking_config)
        self.api_manager.load_environment()
        
        # Initialize WSDL connector
        self.wsdl_connector = WSDLConnector()
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'wsdl_files': 0,
            'xsd_files': 0,
            'processed_successfully': 0,
            'failed': 0,
            'errors': []
        }
    
    def setup_directories(self):
        """Create input and output directories if they don't exist"""
        try:
            self.input_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Input directory: {self.input_dir}")
            logger.info(f"📁 Output directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ Error creating directories: {e}")
            raise
    
    def find_soap_files(self) -> Dict[str, List[Path]]:
        """
        Find all WSDL and XSD files in the input directory
        
        Returns:
            Dictionary with 'wsdl' and 'xsd' keys containing lists of file paths
        """
        soap_files = {
            'wsdl': [],
            'xsd': []
        }
        
        if not self.input_dir.exists():
            logger.error(f"❌ Input directory does not exist: {self.input_dir}")
            return soap_files
        
        # Find all WSDL and XSD files
        for file_path in self.input_dir.rglob("*"):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                if file_ext == '.wsdl':
                    soap_files['wsdl'].append(file_path)
                elif file_ext == '.xsd':
                    soap_files['xsd'].append(file_path)
        
        self.stats['wsdl_files'] = len(soap_files['wsdl'])
        self.stats['xsd_files'] = len(soap_files['xsd'])
        self.stats['total_files'] = self.stats['wsdl_files'] + self.stats['xsd_files']
        
        logger.info(f"📄 Found {self.stats['wsdl_files']} WSDL files")
        logger.info(f"📄 Found {self.stats['xsd_files']} XSD files")
        logger.info(f"📄 Total files: {self.stats['total_files']}")
        
        return soap_files
    
    def group_files_by_service(self, soap_files: Dict[str, List[Path]]) -> List[Dict[str, Any]]:
        """
        Group WSDL and XSD files by service (heuristic grouping)
        
        Args:
            soap_files: Dictionary containing WSDL and XSD file lists
            
        Returns:
            List of service groups, each containing a main WSDL and related XSD files
        """
        service_groups = []
        
        # For each WSDL file, try to find related XSD files
        for wsdl_file in soap_files['wsdl']:
            service_name = wsdl_file.stem.lower()
            
            # Find XSD files that might be related to this WSDL
            related_xsd_files = []
            for xsd_file in soap_files['xsd']:
                xsd_name = xsd_file.stem.lower()
                
                # Simple heuristic: if XSD name contains WSDL name or vice versa
                if (service_name in xsd_name or 
                    xsd_name in service_name or
                    any(part in xsd_name for part in service_name.split('_')) or
                    any(part in service_name for part in xsd_name.split('_'))):
                    related_xsd_files.append(xsd_file)
            
            service_group = {
                'service_name': service_name,
                'main_wsdl': wsdl_file,
                'xsd_files': related_xsd_files,
                'all_files': [wsdl_file] + related_xsd_files
            }
            
            service_groups.append(service_group)
            logger.info(f"🔗 Service '{service_name}': 1 WSDL + {len(related_xsd_files)} XSD files")
        
        # Handle orphaned XSD files (not associated with any WSDL)
        orphaned_xsd_files = []
        for xsd_file in soap_files['xsd']:
            is_orphaned = True
            for group in service_groups:
                if xsd_file in group['xsd_files']:
                    is_orphaned = False
                    break
            
            if is_orphaned:
                orphaned_xsd_files.append(xsd_file)
        
        # Create a group for orphaned XSD files
        if orphaned_xsd_files:
            orphaned_group = {
                'service_name': 'orphaned_xsd',
                'main_wsdl': None,
                'xsd_files': orphaned_xsd_files,
                'all_files': orphaned_xsd_files
            }
            service_groups.append(orphaned_group)
            logger.info(f"🔗 Orphaned XSD files: {len(orphaned_xsd_files)} files")
        
        return service_groups
    
    def convert_service_group(self, service_group: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert a service group (WSDL + XSD files) to CommonAPISpec
        
        Args:
            service_group: Service group containing WSDL and XSD files
            
        Returns:
            Dictionary containing conversion results or None if failed
        """
        service_name = service_group['service_name']
        main_wsdl = service_group['main_wsdl']
        xsd_files = service_group['xsd_files']
        
        try:
            logger.info(f"🔄 Converting service: {service_name}")
            
            if main_wsdl:
                # Convert WSDL with XSD dependencies
                file_paths = [str(main_wsdl)] + [str(xsd) for xsd in xsd_files]
                
                # Use the multifile parsing method
                common_spec = self.wsdl_connector.parse_wsdl_files_with_dependencies(file_paths)
                
                # Store in ChromaDB (initialize if needed)
                if self.api_manager.chroma_client is None:
                    self.api_manager.initialize_chromadb()
                success = self.api_manager._store_in_chromadb(common_spec)
                
                if success:
                    logger.info(f"✅ Successfully converted service: {service_name}")
                    self.stats['processed_successfully'] += 1
                    
                    return {
                        'service_name': service_name,
                        'common_spec': common_spec,
                        'file_paths': file_paths,
                        'success': True
                    }
                else:
                    logger.error(f"❌ Failed to store service in ChromaDB: {service_name}")
                    self.stats['failed'] += 1
                    return None
            else:
                # Handle orphaned XSD files
                logger.warning(f"⚠️ Orphaned XSD files found: {service_name}")
                logger.warning("⚠️ XSD files without WSDL cannot be converted to CommonAPISpec")
                self.stats['failed'] += 1
                return None
                
        except Exception as e:
            error_msg = f"Error converting service {service_name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            self.stats['failed'] += 1
            self.stats['errors'].append({
                'service_name': service_name,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            
            return None
    
    def save_common_spec_to_json(self, common_spec: CommonAPISpec, service_name: str) -> str:
        """
        Save CommonAPISpec to JSON file
        
        Args:
            common_spec: CommonAPISpec object to save
            service_name: Name of the service for filename
            
        Returns:
            Path to the saved JSON file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in service_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"{safe_name}_{timestamp}.json"
            file_path = self.output_dir / filename
            
            # Convert to dictionary
            spec_dict = common_spec.__dict__
            
            # Write to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(spec_dict, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Saved CommonAPISpec to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving CommonAPISpec to JSON: {str(e)}")
            raise
    
    def process_all_files(self):
        """Process all WSDL and XSD files in the input directory"""
        logger.info("🚀 Starting SOAP to CommonAPISpec conversion")
        logger.info("=" * 60)
        
        try:
            # Setup directories
            self.setup_directories()
            
            # Find all SOAP files
            soap_files = self.find_soap_files()
            
            if self.stats['total_files'] == 0:
                logger.warning("⚠️ No WSDL or XSD files found in input directory")
                return
            
            # Group files by service
            service_groups = self.group_files_by_service(soap_files)
            
            # Process each service group
            successful_conversions = []
            
            for service_group in service_groups:
                result = self.convert_service_group(service_group)
                if result and result['success']:
                    # Save to JSON file
                    json_path = self.save_common_spec_to_json(
                        result['common_spec'], 
                        result['service_name']
                    )
                    result['json_path'] = json_path
                    successful_conversions.append(result)
            
            # Print summary
            self.print_summary(successful_conversions)
            
        except Exception as e:
            logger.error(f"❌ Fatal error during processing: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
    
    def print_summary(self, successful_conversions: List[Dict[str, Any]]):
        """Print processing summary"""
        logger.info("=" * 60)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"📄 Total files found: {self.stats['total_files']}")
        logger.info(f"   - WSDL files: {self.stats['wsdl_files']}")
        logger.info(f"   - XSD files: {self.stats['xsd_files']}")
        logger.info(f"✅ Successfully processed: {self.stats['processed_successfully']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        
        if successful_conversions:
            logger.info(f"\n📋 SUCCESSFULLY CONVERTED SERVICES:")
            for result in successful_conversions:
                logger.info(f"   - {result['service_name']}: {result['json_path']}")
        
        if self.stats['errors']:
            logger.info(f"\n❌ ERRORS:")
            for error in self.stats['errors']:
                logger.info(f"   - {error['service_name']}: {error['error']}")
        
        logger.info("=" * 60)
        logger.info("🎉 Processing complete!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert SOAP (WSDL/XSD) files to CommonAPISpec JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python soap_converter.py --input-dir ./soap_files --output-dir ./output
    python soap_converter.py -i ./wsdl_files -o ./json_output
    python soap_converter.py  # Uses default directories: ./input and ./output
    
Environment Variables:
    export SOAP_INPUT_DIR=/path/to/wsdl/files
    export SOAP_OUTPUT_DIR=/path/to/output
    python soap_converter.py  # Uses environment variables
        """
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        default=os.getenv('SOAP_INPUT_DIR', './input'),
        help='Directory containing WSDL and XSD files (default: ./input or SOAP_INPUT_DIR env var)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=os.getenv('SOAP_OUTPUT_DIR', './output'),
        help='Directory to output CommonAPISpec JSON files (default: ./output or SOAP_OUTPUT_DIR env var)'
    )
    
    parser.add_argument(
        '--chunking-strategy',
        choices=['FIXED_SIZE', 'SEMANTIC', 'HYBRID', 'ENDPOINT_BASED'],
        default='ENDPOINT_BASED',
        help='Chunking strategy for ChromaDB storage (default: ENDPOINT_BASED)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create and run converter
        converter = SOAPConverter(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            chunking_strategy=args.chunking_strategy
        )
        
        converter.process_all_files()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

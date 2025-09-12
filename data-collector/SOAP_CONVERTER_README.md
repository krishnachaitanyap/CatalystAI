# SOAP to CommonAPISpec Converter

A standalone Python script that converts SOAP (WSDL/XSD) files to CommonAPISpec JSON format.

## Features

- **Multifile Processing**: Handles WSDL files with external XSD dependencies
- **Automatic Detection**: Finds all WSDL and XSD files in input directory
- **Service Grouping**: Intelligently groups related WSDL and XSD files
- **ChromaDB Integration**: Stores processed specifications in vector database
- **JSON Output**: Generates CommonAPISpec JSON files for each service
- **Detailed Logging**: Comprehensive logging with error handling
- **Standalone**: No external dependencies beyond the data-collector modules

## Usage

### Basic Usage
```bash
# Use default directories (./input and ./output)
python soap_converter.py

# Specify custom directories
python soap_converter.py --input-dir ./soap_files --output-dir ./json_output

# Short form
python soap_converter.py -i ./wsdl_files -o ./output
```

### Advanced Options
```bash
# Use different chunking strategy
python soap_converter.py --chunking-strategy SEMANTIC

# Enable verbose logging
python soap_converter.py --verbose

# Full example
python soap_converter.py \
  --input-dir ./soap_services \
  --output-dir ./common_specs \
  --chunking-strategy ENDPOINT_BASED \
  --verbose
```

## Command Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--input-dir` | `-i` | `./input` | Directory containing WSDL and XSD files |
| `--output-dir` | `-o` | `./output` | Directory to output CommonAPISpec JSON files |
| `--chunking-strategy` | | `ENDPOINT_BASED` | Chunking strategy: `FIXED_SIZE`, `SEMANTIC`, `HYBRID`, `ENDPOINT_BASED` |
| `--verbose` | `-v` | `False` | Enable verbose logging |

## Directory Structure

### Input Directory
Place your WSDL and XSD files in the input directory:
```
input/
├── user-service.wsdl
├── user-types.xsd
├── common-types.xsd
├── order-service.wsdl
├── order-schema.xsd
└── payment-service.wsdl
```

### Output Directory
The script will create CommonAPISpec JSON files:
```
output/
├── user_service_20250912_143022.json
├── order_service_20250912_143025.json
└── payment_service_20250912_143028.json
```

## Service Grouping Logic

The script intelligently groups WSDL and XSD files by service using these heuristics:

1. **Name Matching**: XSD files with names containing the WSDL service name
2. **Partial Matching**: XSD files with partial name matches
3. **Underscore Splitting**: Matches based on underscore-separated parts
4. **Orphaned XSD**: XSD files not associated with any WSDL are flagged

## Processing Flow

1. **Discovery**: Scan input directory for WSDL and XSD files
2. **Grouping**: Group files by service using naming heuristics
3. **Conversion**: Process each service group:
   - Load XSD dependencies
   - Parse WSDL with external schemas
   - Generate CommonAPISpec
   - Store in ChromaDB
4. **Output**: Save CommonAPISpec as JSON file
5. **Summary**: Display processing statistics

## Example Output

### Console Output
```
2025-09-12 14:30:22 - INFO - 🚀 Starting SOAP to CommonAPISpec conversion
2025-09-12 14:30:22 - INFO - ============================================================
2025-09-12 14:30:22 - INFO - 📁 Input directory: /path/to/input
2025-09-12 14:30:22 - INFO - 📁 Output directory: /path/to/output
2025-09-12 14:30:22 - INFO - 📄 Found 3 WSDL files
2025-09-12 14:30:22 - INFO - 📄 Found 5 XSD files
2025-09-12 14:30:22 - INFO - 📄 Total files: 8
2025-09-12 14:30:22 - INFO - 🔗 Service 'user_service': 1 WSDL + 2 XSD files
2025-09-12 14:30:22 - INFO - 🔗 Service 'order_service': 1 WSDL + 1 XSD files
2025-09-12 14:30:22 - INFO - 🔗 Service 'payment_service': 1 WSDL + 0 XSD files
2025-09-12 14:30:22 - INFO - 🔄 Converting service: user_service
2025-09-12 14:30:22 - INFO - 📄 Main WSDL file: /path/to/user-service.wsdl
2025-09-12 14:30:22 - INFO - 📄 XSD dependencies: ['/path/to/user-types.xsd', '/path/to/common-types.xsd']
2025-09-12 14:30:22 - INFO - ✅ Loaded XSD dependency: /path/to/user-types.xsd
2025-09-12 14:30:22 - INFO - ✅ Loaded XSD dependency: /path/to/common-types.xsd
2025-09-12 14:30:22 - INFO - ✅ Successfully converted service: user_service
2025-09-12 14:30:22 - INFO - 💾 Saved CommonAPISpec to: /path/to/output/user_service_20250912_143022.json
```

### Summary Output
```
============================================================
📊 PROCESSING SUMMARY
============================================================
📄 Total files found: 8
   - WSDL files: 3
   - XSD files: 5
✅ Successfully processed: 3
❌ Failed: 0

📋 SUCCESSFULLY CONVERTED SERVICES:
   - user_service: /path/to/output/user_service_20250912_143022.json
   - order_service: /path/to/output/order_service_20250912_143025.json
   - payment_service: /path/to/output/payment_service_20250912_143028.json
============================================================
🎉 Processing complete!
```

## JSON Output Format

Each generated JSON file contains a complete CommonAPISpec:

```json
{
  "api_name": "UserService",
  "version": "1.0.0",
  "description": "SOAP Web Service",
  "base_url": "http://example.com/UserService",
  "category": "soap",
  "endpoints": [
    {
      "path": "/GetUser",
      "method": "POST",
      "summary": "GetUser",
      "description": "",
      "parameters": [...],
      "request_body": {...},
      "responses": {...},
      "tags": ["soap"],
      "operation_id": "GetUser",
      "deprecated": false,
      "soap_action": "http://example.com/GetUser"
    }
  ],
  "authentication": {...},
  "rate_limits": {...},
  "documentation_url": "",
  "integration_steps": [...],
  "best_practices": [...],
  "common_use_cases": [...],
  "tags": ["soap", "wsdl", "enterprise"],
  "contact_info": {},
  "license_info": {},
  "external_docs": [],
  "examples": [...],
  "sealId": "105961",
  "application": "PROFILE",
  "namespaces": {...},
  "schema_version": "1.0",
  "created_at": "2025-09-12T14:30:22.153416",
  "updated_at": "2025-09-12T14:30:22.153423"
}
```

## Error Handling

The script includes comprehensive error handling:

- **File Validation**: Checks for valid WSDL/XSD files
- **Dependency Resolution**: Handles missing or invalid XSD dependencies
- **Processing Errors**: Continues processing other services if one fails
- **Logging**: Detailed error messages with stack traces
- **Recovery**: Graceful handling of partial failures

## Logging

The script creates a log file `soap_converter.log` with detailed processing information:

- Processing steps and progress
- Error messages and stack traces
- Service grouping decisions
- File discovery results
- Conversion statistics

## Requirements

- Python 3.7+
- data-collector modules (connectors, utils, models)
- ChromaDB for vector storage
- Required Python packages from `api_requirements.txt`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the data-collector directory
2. **No Files Found**: Check that WSDL/XSD files are in the input directory
3. **Permission Errors**: Ensure write permissions for output directory
4. **ChromaDB Errors**: Check ChromaDB installation and configuration

### Debug Mode

Use `--verbose` flag for detailed debugging information:
```bash
python soap_converter.py --verbose
```

## Examples

### Process All Files in Current Directory
```bash
mkdir -p input output
# Copy your WSDL/XSD files to input/
python soap_converter.py
```

### Process Specific Service Files
```bash
mkdir -p my_services json_output
# Copy service files to my_services/
python soap_converter.py -i my_services -o json_output
```

### Batch Process Multiple Directories
```bash
for dir in service1 service2 service3; do
    python soap_converter.py -i $dir -o output_$dir
done
```

This standalone converter provides a complete solution for converting SOAP services to CommonAPISpec format with full dependency resolution and comprehensive error handling.

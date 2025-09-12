# Standalone SOAP Converter

A completely self-contained Python script that converts WSDL and XSD files to CommonAPISpec JSON format without any external dependencies.

## 🚀 Features

- **Self-contained**: All WSDL connector functionality is included in a single file
- **No external dependencies**: Only uses Python standard library
- **Complex scenario handling**: Handles circular dependencies, external XSD imports, and cross-file references
- **Performance optimized**: Intelligent recursion control prevents infinite loops
- **Multifile support**: Processes multiple WSDL/XSD files with dependencies
- **Flexible configuration**: Command line arguments and environment variables

## 📋 Requirements

- Python 3.7+
- No external packages required (uses only standard library)

## 🛠️ Installation

No installation required! Just download the script:

```bash
# Download the standalone converter
curl -O https://raw.githubusercontent.com/your-repo/CatalystAI/main/data-collector/standalone_soap_converter.py

# Make it executable
chmod +x standalone_soap_converter.py
```

## 🚀 Usage

### Basic Usage

```bash
# Convert files from default directories (./input and ./output)
python standalone_soap_converter.py

# Convert files from custom directories
python standalone_soap_converter.py --input-dir ./soap_files --output-dir ./output

# Using short form arguments
python standalone_soap_converter.py -i ./wsdl_files -o ./json_output
```

### Environment Variables

```bash
# Set environment variables
export SOAP_INPUT_DIR=/path/to/your/wsdl/files
export SOAP_OUTPUT_DIR=/path/to/your/output
python standalone_soap_converter.py

# Or set them inline
SOAP_INPUT_DIR=./soap_files SOAP_OUTPUT_DIR=./output python standalone_soap_converter.py
```

### Advanced Options

```bash
# Enable verbose logging
python standalone_soap_converter.py --verbose

# Show help
python standalone_soap_converter.py --help
```

## 📁 Directory Structure

```
project/
├── standalone_soap_converter.py
├── input/                    # Default input directory
│   ├── service1.wsdl
│   ├── service1.xsd
│   ├── service2.wsdl
│   └── external-types.xsd
└── output/                   # Default output directory
    ├── service1_20250912_120000.json
    └── service2_20250912_120001.json
```

## 🔧 Configuration Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input-dir` | `-i` | `./input` | Directory containing WSDL and XSD files |
| `--output-dir` | `-o` | `./output` | Directory to output CommonAPISpec JSON files |
| `--chunking-strategy` | - | `ENDPOINT_BASED` | Chunking strategy (not used in standalone mode) |
| `--verbose` | `-v` | `False` | Enable verbose logging |

## 📊 Output Format

The converter generates CommonAPISpec JSON files with the following structure:

```json
{
  "api_name": "UserService",
  "version": "1.0.0",
  "description": "SOAP service: UserService",
  "base_url": "http://example.com/UserService",
  "category": "SOAP",
  "api_type": "SOAP",
  "format": "WSDL",
  "endpoints": [
    {
      "path": "/GetUser",
      "method": "POST",
      "summary": "SOAP operation: GetUser",
      "operation_name": "GetUser",
      "parameters": [...],
      "responses": {...}
    }
  ],
  "data_types": [...],
  "authentication": [...],
  "servers": [...],
  "sealId": "105961",
  "application": "PROFILE"
}
```

## 🧪 Complex Scenario Handling

The standalone converter handles complex scenarios including:

### Circular Dependencies
- **Detection**: Identifies circular references in type definitions
- **Prevention**: Uses depth limiting (8 levels max) and circular reference counting (5 max)
- **Recovery**: Continues processing after detecting circular references

### External XSD Imports
- **Resolution**: Automatically loads referenced XSD files
- **Cross-file references**: Resolves type references across multiple files
- **Namespace handling**: Supports qualified type names with prefixes

### Performance Optimization
- **Recursion control**: Prevents infinite loops with intelligent depth limiting
- **Early termination**: Stops processing when too many circular references detected
- **Efficient parsing**: Optimized XML parsing with minimal memory usage

## 📝 Examples

### Example 1: Basic Conversion

```bash
# Create input directory and add WSDL files
mkdir -p input
cp your_service.wsdl input/
cp your_types.xsd input/

# Convert to JSON
python standalone_soap_converter.py

# Check output
ls output/
# Output: your_service_20250912_120000.json
```

### Example 2: Custom Directories

```bash
# Convert files from specific directories
python standalone_soap_converter.py \
  --input-dir /path/to/soap/services \
  --output-dir /path/to/api/specs
```

### Example 3: Batch Processing

```bash
# Process multiple service directories
for dir in ./services/*/; do
    service_name=$(basename "$dir")
    python standalone_soap_converter.py \
      -i "$dir" \
      -o "./output/$service_name"
done
```

### Example 4: Environment Variables

```bash
# Set up environment
export SOAP_INPUT_DIR=/enterprise/soap/services
export SOAP_OUTPUT_DIR=/enterprise/api/specs

# Convert all services
python standalone_soap_converter.py --verbose
```

## 🔍 Troubleshooting

### Common Issues

1. **No files found**: Ensure WSDL/XSD files are in the input directory
2. **Permission errors**: Check file permissions and directory access
3. **Circular dependency warnings**: These are normal and handled automatically
4. **XSD import errors**: Ensure referenced XSD files are in the same directory

### Debug Mode

```bash
# Enable verbose logging for debugging
python standalone_soap_converter.py --verbose
```

### Log Files

The converter creates a log file `soap_converter.log` with detailed processing information.

## 🚀 Performance

- **Processing time**: ~3 seconds for complex WSDL files with circular dependencies
- **Memory usage**: Minimal memory footprint using streaming XML parsing
- **Scalability**: Handles large WSDL files with thousands of operations
- **Recovery**: Graceful handling of malformed or complex WSDL structures

## 🔄 Comparison with Full Converter

| Feature | Standalone | Full Converter |
|---------|------------|----------------|
| **Dependencies** | None | ChromaDB, OpenAI, etc. |
| **File size** | ~50KB | ~500KB+ |
| **Chunking** | Not available | Full chunking support |
| **Vector storage** | Not available | ChromaDB integration |
| **LLM integration** | Not available | OpenAI integration |
| **Complex scenarios** | ✅ Full support | ✅ Full support |
| **Performance** | ✅ Optimized | ✅ Optimized |

## 📚 Use Cases

- **Quick conversions**: Convert WSDL files to JSON without setup
- **CI/CD pipelines**: Integrate into automated build processes
- **Legacy system analysis**: Analyze old SOAP services
- **API documentation**: Generate API specs from WSDL files
- **Migration projects**: Convert SOAP services to REST APIs

## 🤝 Contributing

The standalone converter is designed to be self-contained and easy to modify. Key areas for enhancement:

- Additional WSDL features support
- Enhanced error handling
- Custom output formats
- Performance optimizations

## 📄 License

This standalone converter is part of the CatalystAI project and follows the same license terms.

## 🆘 Support

For issues or questions:

1. Check the log file `soap_converter.log`
2. Run with `--verbose` for detailed output
3. Ensure WSDL/XSD files are valid XML
4. Check file permissions and directory access

---

**Note**: This standalone converter focuses on WSDL parsing and JSON generation. For full functionality including ChromaDB storage, chunking, and LLM integration, use the full `soap_converter.py` with all dependencies.

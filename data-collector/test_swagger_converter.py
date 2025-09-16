#!/usr/bin/env python3
"""
Test script for the standalone Swagger/OpenAPI converter

This script tests the converter with various Swagger and OpenAPI files
to ensure it handles different scenarios correctly.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from standalone_swagger_converter import StandaloneSwaggerConverter, ProcessingContext


def create_test_swagger2_file():
    """Create a test Swagger 2.0 file"""
    swagger2_spec = {
        "swagger": "2.0",
        "info": {
            "title": "Test API",
            "description": "A test API for validation",
            "version": "1.0.0",
            "contact": {
                "name": "Test Team",
                "email": "test@example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "host": "api.example.com",
        "basePath": "/v1",
        "schemes": ["https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "api_key": {
                "type": "apiKey",
                "name": "X-API-Key",
                "in": "header"
            }
        },
        "paths": {
            "/users": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get all users",
                    "description": "Retrieve a list of all users",
                    "operationId": "getUsers",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of users to return",
                            "required": False,
                            "type": "integer",
                            "format": "int32",
                            "default": 10
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/User"
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    },
                    "security": [
                        {
                            "api_key": []
                        }
                    ]
                },
                "post": {
                    "tags": ["users"],
                    "summary": "Create a new user",
                    "description": "Create a new user in the system",
                    "operationId": "createUser",
                    "parameters": [
                        {
                            "name": "user",
                            "in": "body",
                            "description": "User object to create",
                            "required": True,
                            "schema": {
                                "$ref": "#/definitions/NewUser"
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "User created successfully",
                            "schema": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get user by ID",
                    "description": "Retrieve a specific user by their ID",
                    "operationId": "getUserById",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "description": "User ID",
                            "required": True,
                            "type": "integer",
                            "format": "int64"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User found",
                            "schema": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "404": {
                            "description": "User not found",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            }
        },
        "definitions": {
            "User": {
                "type": "object",
                "required": ["id", "name", "email"],
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64",
                        "description": "Unique identifier for the user"
                    },
                    "name": {
                        "type": "string",
                        "description": "User's full name"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User's email address"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When the user was created"
                    },
                    "profile": {
                        "$ref": "#/definitions/UserProfile"
                    }
                }
            },
            "NewUser": {
                "type": "object",
                "required": ["name", "email"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "User's full name"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User's email address"
                    },
                    "profile": {
                        "$ref": "#/definitions/UserProfile"
                    }
                }
            },
            "UserProfile": {
                "type": "object",
                "properties": {
                    "bio": {
                        "type": "string",
                        "description": "User's biography"
                    },
                    "avatar_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL to user's avatar image"
                    },
                    "preferences": {
                        "type": "object",
                        "properties": {
                            "theme": {
                                "type": "string",
                                "enum": ["light", "dark"],
                                "default": "light"
                            },
                            "notifications": {
                                "type": "boolean",
                                "default": True
                            }
                        }
                    }
                }
            },
            "Error": {
                "type": "object",
                "required": ["code", "message"],
                "properties": {
                    "code": {
                        "type": "integer",
                        "format": "int32",
                        "description": "Error code"
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "details": {
                        "type": "string",
                        "description": "Additional error details"
                    }
                }
            }
        }
    }
    return swagger2_spec


def create_test_openapi3_file():
    """Create a test OpenAPI 3.x file"""
    openapi3_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test OpenAPI 3 API",
            "description": "A test API using OpenAPI 3.0 specification",
            "version": "2.0.0",
            "contact": {
                "name": "OpenAPI Test Team",
                "email": "openapi@example.com",
                "url": "https://example.com/contact"
            },
            "license": {
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
            }
        },
        "servers": [
            {
                "url": "https://api.example.com/v2",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.example.com/v2",
                "description": "Staging server"
            }
        ],
        "security": [
            {
                "ApiKeyAuth": []
            }
        ],
        "paths": {
            "/products": {
                "get": {
                    "tags": ["products"],
                    "summary": "List products",
                    "description": "Get a list of all products",
                    "operationId": "listProducts",
                    "parameters": [
                        {
                            "name": "category",
                            "in": "query",
                            "description": "Filter by product category",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["electronics", "clothing", "books"]
                            }
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of products to return",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 20
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Product"
                                        }
                                    },
                                    "example": [
                                        {
                                            "id": 1,
                                            "name": "Sample Product",
                                            "price": 29.99,
                                            "category": "electronics"
                                        }
                                    ]
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["products"],
                    "summary": "Create product",
                    "description": "Create a new product",
                    "operationId": "createProduct",
                    "requestBody": {
                        "description": "Product object to create",
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/NewProduct"
                                },
                                "example": {
                                    "name": "New Product",
                                    "price": 19.99,
                                    "category": "electronics",
                                    "description": "A great new product"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Product created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Product"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/products/{id}": {
                "get": {
                    "tags": ["products"],
                    "summary": "Get product by ID",
                    "description": "Retrieve a specific product by its ID",
                    "operationId": "getProductById",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "description": "Product ID",
                            "required": True,
                            "schema": {
                                "type": "integer",
                                "format": "int64"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Product found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Product"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Product not found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Error"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            },
            "schemas": {
                "Product": {
                    "type": "object",
                    "required": ["id", "name", "price", "category"],
                    "properties": {
                        "id": {
                            "type": "integer",
                            "format": "int64",
                            "description": "Unique identifier for the product"
                        },
                        "name": {
                            "type": "string",
                            "description": "Product name",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "price": {
                            "type": "number",
                            "format": "float",
                            "description": "Product price",
                            "minimum": 0
                        },
                        "category": {
                            "type": "string",
                            "description": "Product category",
                            "enum": ["electronics", "clothing", "books"]
                        },
                        "description": {
                            "type": "string",
                            "description": "Product description"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "When the product was created"
                        },
                        "metadata": {
                            "$ref": "#/components/schemas/ProductMetadata"
                        }
                    }
                },
                "NewProduct": {
                    "type": "object",
                    "required": ["name", "price", "category"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Product name",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "price": {
                            "type": "number",
                            "format": "float",
                            "description": "Product price",
                            "minimum": 0
                        },
                        "category": {
                            "type": "string",
                            "description": "Product category",
                            "enum": ["electronics", "clothing", "books"]
                        },
                        "description": {
                            "type": "string",
                            "description": "Product description"
                        },
                        "metadata": {
                            "$ref": "#/components/schemas/ProductMetadata"
                        }
                    }
                },
                "ProductMetadata": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Product tags"
                        },
                        "weight": {
                            "type": "number",
                            "description": "Product weight in kg"
                        },
                        "dimensions": {
                            "type": "object",
                            "properties": {
                                "length": {
                                    "type": "number",
                                    "description": "Length in cm"
                                },
                                "width": {
                                    "type": "number",
                                    "description": "Width in cm"
                                },
                                "height": {
                                    "type": "number",
                                    "description": "Height in cm"
                                }
                            }
                        }
                    }
                },
                "Error": {
                    "type": "object",
                    "required": ["code", "message"],
                    "properties": {
                        "code": {
                            "type": "integer",
                            "format": "int32",
                            "description": "Error code"
                        },
                        "message": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "details": {
                            "type": "string",
                            "description": "Additional error details"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "When the error occurred"
                        }
                    }
                }
            }
        }
    }
    return openapi3_spec


def run_tests():
    """Run comprehensive tests for the Swagger converter"""
    print("🧪 Starting Swagger Converter Tests")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create test files
        print("📝 Creating test files...")
        
        # Swagger 2.0 test file
        swagger2_spec = create_test_swagger2_file()
        swagger2_file = input_dir / "test_swagger2.json"
        with open(swagger2_file, 'w') as f:
            json.dump(swagger2_spec, f, indent=2)
        print(f"   ✅ Created {swagger2_file.name}")
        
        # OpenAPI 3.x test file
        openapi3_spec = create_test_openapi3_file()
        openapi3_file = input_dir / "test_openapi3.json"
        with open(openapi3_file, 'w') as f:
            json.dump(openapi3_spec, f, indent=2)
        print(f"   ✅ Created {openapi3_file.name}")
        
        # YAML test file
        yaml_file = input_dir / "test_yaml.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(swagger2_spec, f, default_flow_style=False, indent=2)
        print(f"   ✅ Created {yaml_file.name}")
        
        # Test the converter
        print("\n🔄 Testing converter...")
        
        context = ProcessingContext(
            max_depth=10,
            max_circular_refs=5,
            enable_caching=True
        )
        
        converter = StandaloneSwaggerConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            context=context
        )
        
        # Process all files
        stats = converter.process_all_files()
        
        # Check results
        print("\n📊 Test Results:")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Processed successfully: {stats['processed_successfully']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Cache hit rate: {converter.parser.cache.hit_rate:.2%}")
        
        # Check output files
        output_files = list(output_dir.glob("*.json"))
        print(f"\n📁 Output files created: {len(output_files)}")
        
        for output_file in output_files:
            print(f"   ✅ {output_file.name}")
            
            # Validate output structure
            with open(output_file, 'r') as f:
                output_data = json.load(f)
            
            # Check required fields
            required_fields = ['metadata', 'endpoints', 'schemas', 'security']
            for field in required_fields:
                if field not in output_data:
                    print(f"   ❌ Missing required field: {field}")
                else:
                    print(f"   ✅ Found field: {field}")
            
            # Check metadata
            metadata = output_data['metadata']
            print(f"   📋 Spec type: {metadata['spec_type']}")
            print(f"   📋 Title: {metadata['title']}")
            print(f"   📋 Endpoints: {len(output_data['endpoints'])}")
            print(f"   📋 Schemas: {len(output_data['schemas'])}")
        
        # Test error handling
        print("\n🔍 Testing error handling...")
        
        # Create invalid JSON file
        invalid_file = input_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Create non-Swagger JSON file
        non_swagger_file = input_dir / "not_swagger.json"
        with open(non_swagger_file, 'w') as f:
            json.dump({"not": "a swagger spec"}, f)
        
        # Process again to test error handling
        error_stats = converter.process_all_files()
        
        print(f"   Files with errors: {error_stats['failed']}")
        if error_stats['errors']:
            for error in error_stats['errors']:
                print(f"   ⚠️ {error['file']}: {error['error']}")
        
        print("\n🎉 Tests completed!")
        
        return stats['processed_successfully'] > 0 and stats['failed'] == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

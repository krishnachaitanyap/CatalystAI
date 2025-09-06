#!/usr/bin/env python3
"""
Sample Data Collection Script for CatalystAI RAG Service
Demonstrates how to collect and ingest sample API data
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from models.requests import DocumentMetadata, DocumentType, Environment
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.chunking_service import ChunkingService

class SampleDataCollector:
    """Collects and processes sample API data for testing"""
    
    def __init__(self):
        self.document_service = DocumentService()
        self.embedding_service = EmbeddingService()
        self.chunking_service = ChunkingService()
        
        # Sample data directory
        self.sample_data_dir = Path(__file__).parent / "sample_data"
        self.sample_data_dir.mkdir(exist_ok=True)
    
    async def collect_sample_data(self):
        """Collect and process sample API data"""
        print("🚀 Starting sample data collection for CatalystAI...")
        
        try:
            # Create sample OpenAPI specification
            await self._create_sample_openapi()
            
            # Create sample GraphQL schema
            await self._create_sample_graphql()
            
            # Create sample SOAP/WSDL
            await self._create_sample_soap()
            
            # Create sample markdown documentation
            await self._create_sample_markdown()
            
            # Create sample Postman collection
            await self._create_sample_postman()
            
            # Create sample HAR file
            await self._create_sample_har()
            
            print("✅ Sample data collection completed successfully!")
            print(f"📁 Sample data saved to: {self.sample_data_dir}")
            
        except Exception as e:
            print(f"❌ Error during data collection: {str(e)}")
            raise
    
    async def _create_sample_openapi(self):
        """Create sample OpenAPI specification"""
        print("📝 Creating sample OpenAPI specification...")
        
        openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Customer Banking API",
                "version": "1.0.0",
                "description": "API for customer banking operations including balances, transactions, and payments"
            },
            "servers": [
                {"url": "https://api.bank.com/v1", "description": "Production server"},
                {"url": "https://api-staging.bank.com/v1", "description": "Staging server"}
            ],
            "paths": {
                "/customers/{customerId}/balance": {
                    "get": {
                        "operationId": "getCustomerBalance",
                        "summary": "Get customer account balance",
                        "description": "Retrieves the current balance for a specific customer account",
                        "parameters": [
                            {
                                "name": "customerId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Unique identifier for the customer"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "balance": {"type": "number", "format": "decimal"},
                                                "currency": {"type": "string"},
                                                "lastUpdated": {"type": "string", "format": "date-time"}
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "tags": ["Customer", "Balance"],
                        "security": [{"bearerAuth": []}]
                    }
                },
                "/transactions": {
                    "get": {
                        "operationId": "getTransactions",
                        "summary": "Get transaction history",
                        "description": "Retrieves transaction history with optional filtering",
                        "parameters": [
                            {
                                "name": "customerId",
                                "in": "query",
                                "schema": {"type": "string"},
                                "description": "Filter by customer ID"
                            },
                            {
                                "name": "startDate",
                                "in": "query",
                                "schema": {"type": "string", "format": "date"},
                                "description": "Start date for transaction range"
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
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string"},
                                                    "amount": {"type": "number"},
                                                    "description": {"type": "string"},
                                                    "timestamp": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "tags": ["Transactions"],
                        "security": [{"bearerAuth": []}]
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "tags": [
                {"name": "Customer", "description": "Customer management operations"},
                {"name": "Balance", "description": "Account balance operations"},
                {"name": "Transactions", "description": "Transaction history operations"}
            ]
        }
        
        # Save OpenAPI spec
        openapi_file = self.sample_data_dir / "customer_banking_api.yaml"
        import yaml
        with open(openapi_file, 'w') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        print(f"   ✅ OpenAPI spec saved to: {openapi_file}")
    
    async def _create_sample_graphql(self):
        """Create sample GraphQL schema"""
        print("🔗 Creating sample GraphQL schema...")
        
        graphql_schema = """
        # Customer Banking GraphQL Schema
        
        type Customer {
          id: ID!
          name: String!
          email: String!
          accounts: [Account!]!
          createdAt: DateTime!
          updatedAt: DateTime!
        }
        
        type Account {
          id: ID!
          accountNumber: String!
          type: AccountType!
          balance: Decimal!
          currency: Currency!
          customer: Customer!
          transactions: [Transaction!]!
        }
        
        type Transaction {
          id: ID!
          amount: Decimal!
          type: TransactionType!
          description: String!
          timestamp: DateTime!
          account: Account!
        }
        
        enum AccountType {
          CHECKING
          SAVINGS
          CREDIT
          LOAN
        }
        
        enum TransactionType {
          DEPOSIT
          WITHDRAWAL
          TRANSFER
          PAYMENT
        }
        
        enum Currency {
          USD
          EUR
          GBP
          JPY
        }
        
        scalar DateTime
        scalar Decimal
        
        type Query {
          customer(id: ID!): Customer
          customers(limit: Int, offset: Int): [Customer!]!
          account(id: ID!): Account
          accounts(customerId: ID!): [Account!]!
          transaction(id: ID!): Transaction
          transactions(accountId: ID!, limit: Int, offset: Int): [Transaction!]!
        }
        
        type Mutation {
          createCustomer(input: CreateCustomerInput!): Customer!
          updateCustomer(id: ID!, input: UpdateCustomerInput!): Customer!
          createTransaction(input: CreateTransactionInput!): Transaction!
        }
        
        input CreateCustomerInput {
          name: String!
          email: String!
        }
        
        input UpdateCustomerInput {
          name: String
          email: String
        }
        
        input CreateTransactionInput {
          accountId: ID!
          amount: Decimal!
          type: TransactionType!
          description: String!
        }
        """
        
        # Save GraphQL schema
        graphql_file = self.sample_data_dir / "customer_banking_schema.graphql"
        with open(graphql_file, 'w') as f:
            f.write(graphql_schema)
        
        print(f"   ✅ GraphQL schema saved to: {graphql_file}")
    
    async def _create_sample_soap(self):
        """Create sample SOAP/WSDL specification"""
        print("🧼 Creating sample SOAP/WSDL specification...")
        
        wsdl_content = """<?xml version="1.0" encoding="UTF-8"?>
<wsdl:definitions name="CustomerService"
                  targetNamespace="http://bank.com/customer"
                  xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
                  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                  xmlns:tns="http://bank.com/customer"
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    
    <wsdl:types>
        <xsd:schema targetNamespace="http://bank.com/customer">
            <xsd:element name="GetCustomerRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="customerId" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:element name="GetCustomerResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="customer" type="tns:Customer"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:complexType name="Customer">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:string"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="email" type="xsd:string"/>
                    <xsd:element name="accounts" type="tns:AccountArray"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Account">
                <xsd:sequence>
                    <xsd:element name="accountNumber" type="xsd:string"/>
                    <xsd:element name="balance" type="xsd:decimal"/>
                    <xsd:element name="currency" type="xsd:string"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="AccountArray">
                <xsd:sequence>
                    <xsd:element name="account" type="tns:Account" maxOccurs="unbounded"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </wsdl:types>
    
    <wsdl:message name="GetCustomerInput">
        <wsdl:part name="body" element="tns:GetCustomerRequest"/>
    </wsdl:message>
    
    <wsdl:message name="GetCustomerOutput">
        <wsdl:part name="body" element="tns:GetCustomerResponse"/>
    </wsdl:message>
    
    <wsdl:portType name="CustomerPortType">
        <wsdl:operation name="GetCustomer">
            <wsdl:input message="tns:GetCustomerInput"/>
            <wsdl:output message="tns:GetCustomerOutput"/>
        </wsdl:operation>
    </wsdl:portType>
    
    <wsdl:binding name="CustomerBinding" type="tns:CustomerPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <wsdl:operation name="GetCustomer">
            <soap:operation soapAction="http://bank.com/customer/GetCustomer"/>
            <wsdl:input>
                <soap:body use="literal"/>
            </wsdl:input>
            <wsdl:output>
                <soap:body use="literal"/>
            </wsdl:output>
        </wsdl:operation>
    </wsdl:binding>
    
    <wsdl:service name="CustomerService">
        <wsdl:port name="CustomerPort" binding="tns:CustomerBinding">
            <soap:address location="http://bank.com/customer"/>
        </wsdl:port>
    </wsdl:service>
</wsdl:definitions>"""
        
        # Save WSDL file
        wsdl_file = self.sample_data_dir / "customer_service.wsdl"
        with open(wsdl_file, 'w') as f:
            f.write(wsdl_content)
        
        print(f"   ✅ WSDL file saved to: {wsdl_file}")
    
    async def _create_sample_markdown(self):
        """Create sample markdown documentation"""
        print("📄 Creating sample markdown documentation...")
        
        markdown_content = """# Customer Identity API Documentation

## Overview
The Customer Identity API provides endpoints for managing customer identity verification, authentication, and profile management.

## Base URL
- Production: `https://api.bank.com/identity/v1`
- Staging: `https://api-staging.bank.com/identity/v1`

## Authentication
All API calls require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### GET /customers/{customerId}/profile
Retrieves customer profile information.

**Parameters:**
- `customerId` (path): Unique customer identifier

**Response:**
```json
{
  "id": "cust_12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "status": "verified",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### POST /customers/verify
Initiates customer identity verification process.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "documentType": "drivers_license",
  "documentNumber": "DL123456789"
}
```

### PUT /customers/{customerId}/profile
Updates customer profile information.

**Parameters:**
- `customerId` (path): Unique customer identifier

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "phone": "+1-555-0124"
}
```

## Error Codes
- `400`: Bad Request - Invalid input parameters
- `401`: Unauthorized - Invalid or missing authentication
- `404`: Not Found - Customer not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

## Rate Limiting
- 100 requests per minute per API key
- 1000 requests per hour per API key

## SDKs
- [JavaScript SDK](https://github.com/bank/js-sdk)
- [Python SDK](https://github.com/bank/python-sdk)
- [Java SDK](https://github.com/bank/java-sdk)

## Support
For technical support, contact:
- Email: api-support@bank.com
- Documentation: https://docs.bank.com/api
- Status page: https://status.bank.com
"""
        
        # Save markdown file
        markdown_file = self.sample_data_dir / "customer_identity_api.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_content)
        
        print(f"   ✅ Markdown documentation saved to: {markdown_file}")
    
    async def _create_sample_postman(self):
        """Create sample Postman collection"""
        print("📮 Creating sample Postman collection...")
        
        postman_collection = {
            "info": {
                "name": "Customer Banking API",
                "description": "Postman collection for Customer Banking API endpoints",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "variable": [
                {
                    "key": "baseUrl",
                    "value": "https://api.bank.com/v1",
                    "type": "string"
                },
                {
                    "key": "customerId",
                    "value": "cust_12345",
                    "type": "string"
                }
            ],
            "item": [
                {
                    "name": "Get Customer Balance",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{token}}",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{baseUrl}}/customers/{{customerId}}/balance",
                            "host": ["{{baseUrl}}"],
                            "path": ["customers", "{{customerId}}", "balance"]
                        }
                    }
                },
                {
                    "name": "Get Transactions",
                    "request": {
                        "method": "GET",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{token}}",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{baseUrl}}/transactions?customerId={{customerId}}",
                            "host": ["{{baseUrl}}"],
                            "path": ["transactions"],
                            "query": [
                                {
                                    "key": "customerId",
                                    "value": "{{customerId}}"
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        # Save Postman collection
        postman_file = self.sample_data_dir / "customer_banking_api.postman_collection.json"
        with open(postman_file, 'w') as f:
            json.dump(postman_collection, f, indent=2)
        
        print(f"   ✅ Postman collection saved to: {postman_file}")
    
    async def _create_sample_har(self):
        """Create sample HAR file"""
        print("📊 Creating sample HAR file...")
        
        har_content = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "CatalystAI Sample Generator",
                    "version": "1.0.0"
                },
                "entries": [
                    {
                        "startedDateTime": "2024-01-15T10:30:00.000Z",
                        "time": 150,
                        "request": {
                            "method": "GET",
                            "url": "https://api.bank.com/v1/customers/cust_12345/balance",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {
                                    "name": "Authorization",
                                    "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                                },
                                {
                                    "name": "User-Agent",
                                    "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                }
                            ],
                            "queryString": [],
                            "cookies": [],
                            "headersSize": 450,
                            "bodySize": 0
                        },
                        "response": {
                            "status": 200,
                            "statusText": "OK",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {
                                    "name": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "cookies": [],
                            "content": {
                                "size": 89,
                                "mimeType": "application/json",
                                "text": "{\"balance\": 1250.75, \"currency\": \"USD\", \"lastUpdated\": \"2024-01-15T10:30:00Z\"}"
                            },
                            "redirectURL": "",
                            "headersSize": 200,
                            "bodySize": 89
                        },
                        "cache": {},
                        "timings": {
                            "dns": 5,
                            "connect": 15,
                            "send": 2,
                            "wait": 120,
                            "receive": 8
                        }
                    },
                    {
                        "startedDateTime": "2024-01-15T10:31:00.000Z",
                        "time": 200,
                        "request": {
                            "method": "GET",
                            "url": "https://api.bank.com/v1/transactions?customerId=cust_12345",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {
                                    "name": "Authorization",
                                    "value": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                                }
                            ],
                            "queryString": [
                                {
                                    "name": "customerId",
                                    "value": "cust_12345"
                                }
                            ],
                            "cookies": [],
                            "headersSize": 450,
                            "bodySize": 0
                        },
                        "response": {
                            "status": 200,
                            "statusText": "OK",
                            "httpVersion": "HTTP/1.1",
                            "headers": [
                                {
                                    "name": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "cookies": [],
                            "content": {
                                "size": 245,
                                "mimeType": "application/json",
                                "text": "[{\"id\": \"txn_001\", \"amount\": 100.00, \"description\": \"ATM Withdrawal\", \"timestamp\": \"2024-01-15T09:00:00Z\"}]"
                            },
                            "redirectURL": "",
                            "headersSize": 200,
                            "bodySize": 245
                        },
                        "cache": {},
                        "timings": {
                            "dns": 3,
                            "connect": 12,
                            "send": 1,
                            "wait": 175,
                            "receive": 9
                        }
                    }
                ]
            }
        }
        
        # Save HAR file
        har_file = self.sample_data_dir / "customer_banking_api.har"
        with open(har_file, 'w') as f:
            json.dump(har_content, f, indent=2)
        
        print(f"   ✅ HAR file saved to: {har_file}")
    
    async def process_sample_data(self):
        """Process the collected sample data to demonstrate the RAG service"""
        print("\n🔄 Processing sample data with RAG service...")
        
        try:
            # Process each sample file
            sample_files = [
                ("customer_banking_api.yaml", DocumentType.OPENAPI),
                ("customer_banking_schema.graphql", DocumentType.GRAPHQL),
                ("customer_service.wsdl", DocumentType.WSDL),
                ("customer_identity_api.md", DocumentType.MARKDOWN),
                ("customer_banking_api.postman_collection.json", DocumentType.POSTMAN),
                ("customer_banking_api.har", DocumentType.HAR)
            ]
            
            for filename, doc_type in sample_files:
                file_path = self.sample_data_dir / filename
                if file_path.exists():
                    await self._process_sample_file(file_path, doc_type)
            
            print("✅ Sample data processing completed!")
            
        except Exception as e:
            print(f"❌ Error during data processing: {str(e)}")
            raise
    
    async def _process_sample_file(self, file_path: Path, doc_type: DocumentType):
        """Process a single sample file"""
        print(f"   📝 Processing {file_path.name}...")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create metadata
            metadata = DocumentMetadata(
                title=f"Sample {doc_type.value.title()} - {file_path.stem}",
                description=f"Sample {doc_type.value} file for testing",
                document_type=doc_type,
                source_url=str(file_path),
                system_name="Sample Banking System",
                service_name="Customer Banking Service",
                api_name="Customer Banking API",
                tags=["sample", "banking", "customer"],
                environment=Environment.DEV,
                owners=["developer@bank.com"],
                criticality="low",
                domain="banking"
            )
            
            # Create chunks
            chunks = self.chunking_service.create_chunks(
                content=content,
                metadata=metadata,
                chunk_size=512,
                chunk_overlap=50
            )
            
            print(f"      ✅ Created {len(chunks)} chunks")
            
            # Validate chunks
            validation = self.chunking_service.validate_chunks(chunks)
            if validation["valid"]:
                print(f"      ✅ Chunks validated successfully")
            else:
                print(f"      ⚠️  Chunk validation warnings: {validation['warnings']}")
            
        except Exception as e:
            print(f"      ❌ Error processing {file_path.name}: {str(e)}")

async def main():
    """Main function"""
    collector = SampleDataCollector()
    
    # Collect sample data
    await collector.collect_sample_data()
    
    # Process sample data
    await collector.process_sample_data()
    
    print("\n🎉 Sample data collection and processing completed!")
    print("You can now use these sample files to test the CatalystAI RAG service.")

if __name__ == "__main__":
    asyncio.run(main())

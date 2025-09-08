import React, { useState, useRef } from 'react';
import { dataCollectorAPI, FileUploadResponse, ProcessingStatus, ConvertResponse, Application, APISpec } from '../services/dataCollectorAPI';

interface UploadedFile {
  id: string;
  file: File;
  type: 'REST' | 'SOAP' | 'Postman';
  format: 'Swagger' | 'OpenAPI' | 'WSDL' | 'XSD' | 'Postman Collection';
  status: 'pending' | 'validating' | 'valid' | 'invalid';
  errors: string[];
  metadata?: {
    name?: string;
    version?: string;
    description?: string;
    baseUrl?: string;
  };
}

interface ApiUploaderProps {
  application: Application;
  onApiUploaded: (apiSpec: APISpec) => void;
}

const ApiUploader: React.FC<ApiUploaderProps> = ({
  application,
  onApiUploaded
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Enhanced file type validation
  const validateFileType = (file: File): { type: string; format: string; isValid: boolean; error?: string } => {
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();

    // REST APIs - Swagger/OpenAPI
    if (fileExtension === 'json') {
      if (fileName.includes('swagger') || fileName.includes('openapi')) {
        return { type: 'REST', format: 'Swagger', isValid: true };
      }
      if (fileName.includes('postman')) {
        return { type: 'Postman', format: 'Postman Collection', isValid: true };
      }
      // Generic JSON - could be Swagger/OpenAPI
      return { type: 'REST', format: 'Swagger', isValid: true };
    }
    
    if (fileExtension === 'yaml' || fileExtension === 'yml') {
      return { type: 'REST', format: 'OpenAPI', isValid: true };
    }

    // SOAP APIs
    if (fileExtension === 'wsdl') {
      return { type: 'SOAP', format: 'WSDL', isValid: true };
    }
    if (fileExtension === 'xsd') {
      return { type: 'SOAP', format: 'XSD', isValid: true };
    }

    return { 
      type: 'Unknown', 
      format: 'Unknown', 
      isValid: false, 
      error: 'Unsupported file type. Please upload Swagger/OpenAPI JSON/YAML, WSDL/XSD, or Postman Collection files.' 
    };
  };

  // Enhanced JSON validation for Swagger/OpenAPI
  const validateJsonFile = async (file: File): Promise<string[]> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const json = JSON.parse(content);
          
          const errors: string[] = [];
          
          // Enhanced validation for Swagger/OpenAPI
          if (file.name.toLowerCase().includes('swagger') || file.name.toLowerCase().includes('openapi')) {
            if (!json.swagger && !json.openapi) {
              errors.push('Missing required field: swagger or openapi');
            }
            if (!json.info) {
              errors.push('Missing required field: info');
            }
            if (!json.paths) {
              errors.push('Missing required field: paths');
            }
            
            // Check for OpenAPI 3.x specific fields
            if (json.openapi && json.openapi.startsWith('3.')) {
              if (!json.components) {
                errors.push('OpenAPI 3.x should have components section');
              }
            }
            
            // Check for Swagger 2.x specific fields
            if (json.swagger && json.swagger.startsWith('2.')) {
              if (!json.definitions) {
                errors.push('Swagger 2.x should have definitions section');
              }
            }
          } else if (file.name.toLowerCase().includes('postman')) {
            if (!json.info) {
              errors.push('Missing required field: info');
            }
            if (!json.item) {
              errors.push('Missing required field: item');
            }
          } else {
            // Generic JSON validation - check if it looks like Swagger/OpenAPI
            if (json.swagger || json.openapi) {
              if (!json.info) {
                errors.push('Missing required field: info');
              }
              if (!json.paths) {
                errors.push('Missing required field: paths');
              }
            }
          }
          
          resolve(errors);
        } catch (error) {
          resolve(['Invalid JSON format']);
        }
      };
      reader.readAsText(file);
    });
  };

  // Enhanced XML validation for WSDL/XSD
  const validateXmlFile = async (file: File): Promise<string[]> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          
          const errors: string[] = [];
          
          // Basic XML structure validation
          if (!content.includes('<?xml')) {
            errors.push('Missing XML declaration');
          }
          
          if (file.name.toLowerCase().endsWith('.wsdl')) {
            if (!content.includes('<wsdl:definitions') && !content.includes('<definitions')) {
              errors.push('Invalid WSDL format: missing definitions element');
            }
            
            // Check for required WSDL elements
            if (!content.includes('<wsdl:types') && !content.includes('<types')) {
              errors.push('WSDL should have types section');
            }
            if (!content.includes('<wsdl:message') && !content.includes('<message')) {
              errors.push('WSDL should have message definitions');
            }
            if (!content.includes('<wsdl:portType') && !content.includes('<portType')) {
              errors.push('WSDL should have portType definitions');
            }
            if (!content.includes('<wsdl:binding') && !content.includes('<binding')) {
              errors.push('WSDL should have binding definitions');
            }
            if (!content.includes('<wsdl:service') && !content.includes('<service')) {
              errors.push('WSDL should have service definitions');
            }
          } else if (file.name.toLowerCase().endsWith('.xsd')) {
            if (!content.includes('<xsd:schema') && !content.includes('<schema')) {
              errors.push('Invalid XSD format: missing schema element');
            }
            
            // Check for XSD namespace
            if (!content.includes('xmlns:xsd') && !content.includes('xmlns:xs')) {
              errors.push('XSD should have proper namespace declarations');
            }
          }
          
          resolve(errors);
        } catch (error) {
          resolve(['Invalid XML format']);
        }
      };
      reader.readAsText(file);
    });
  };

  // Extract metadata from uploaded files
  const extractMetadata = async (file: File, type: string, format: string): Promise<any> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          
          if (type === 'REST' && (format === 'Swagger' || format === 'OpenAPI')) {
            const json = JSON.parse(content);
            resolve({
              name: json.info?.title || file.name.replace(/\.[^/.]+$/, ""),
              version: json.info?.version || json.swagger || json.openapi || '1.0.0',
              description: json.info?.description || `${format} specification for ${application.name}`,
              baseUrl: json.servers?.[0]?.url || json.host || 'https://api.example.com'
            });
          } else if (type === 'SOAP' && format === 'WSDL') {
            // Extract WSDL metadata
            const wsdlMatch = content.match(/<wsdl:definitions[^>]*name="([^"]*)"[^>]*>/i) || 
                            content.match(/<definitions[^>]*name="([^"]*)"[^>]*>/i);
            const targetNamespace = content.match(/targetNamespace="([^"]*)"/i)?.[1] || '';
            
            resolve({
              name: wsdlMatch?.[1] || file.name.replace(/\.[^/.]+$/, ""),
              version: '1.0.0',
              description: `WSDL specification for ${application.name}`,
              baseUrl: targetNamespace || 'https://api.example.com'
            });
          } else if (type === 'Postman') {
            const json = JSON.parse(content);
            resolve({
              name: json.info?.name || file.name.replace(/\.[^/.]+$/, ""),
              version: json.info?.schema || '2.1.0',
              description: json.info?.description || `Postman collection for ${application.name}`,
              baseUrl: 'https://api.example.com'
            });
          } else {
            resolve({
              name: file.name.replace(/\.[^/.]+$/, ""),
              version: '1.0.0',
              description: `${format} specification for ${application.name}`,
              baseUrl: 'https://api.example.com'
            });
          }
        } catch (error) {
          resolve({
            name: file.name.replace(/\.[^/.]+$/, ""),
            version: '1.0.0',
            description: `${format} specification for ${application.name}`,
            baseUrl: 'https://api.example.com'
          });
        }
      };
      reader.readAsText(file);
    });
  };

  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadedFile[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const validation = validateFileType(file);
      
      if (!validation.isValid) {
        newFiles.push({
          id: `file-${Date.now()}-${i}`,
          file,
          type: validation.type as any,
          format: validation.format as any,
          status: 'invalid',
          errors: [validation.error!]
        });
        continue;
      }

      const uploadedFile: UploadedFile = {
        id: `file-${Date.now()}-${i}`,
        file,
        type: validation.type as any,
        format: validation.format as any,
        status: 'validating',
        errors: []
      };

      newFiles.push(uploadedFile);

      // Validate file content
      try {
        let errors: string[] = [];
        
        if (file.name.toLowerCase().endsWith('.json')) {
          errors = await validateJsonFile(file);
        } else if (file.name.toLowerCase().endsWith('.xml') || file.name.toLowerCase().endsWith('.wsdl') || file.name.toLowerCase().endsWith('.xsd')) {
          errors = await validateXmlFile(file);
        } else if (file.name.toLowerCase().endsWith('.yaml') || file.name.toLowerCase().endsWith('.yml')) {
          // Basic YAML validation - in a real app, you'd use a YAML parser
          errors = [];
        }

        uploadedFile.status = errors.length === 0 ? 'valid' : 'invalid';
        uploadedFile.errors = errors;

        // Extract basic metadata for valid files
        if (errors.length === 0) {
          const metadata = await extractMetadata(file, validation.type, validation.format);
          uploadedFile.metadata = metadata;
        }
      } catch (error) {
        uploadedFile.status = 'invalid';
        uploadedFile.errors = ['File validation failed'];
      }
    }

    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const handleFileRemove = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  };

  const handleUpload = async () => {
    const validFiles = uploadedFiles.filter(file => file.status === 'valid');
    
    if (validFiles.length === 0) {
      alert('Please upload at least one valid file');
      return;
    }

    setIsUploading(true);

    try {
      // Upload files to data-collector API
      for (const uploadedFile of validFiles) {
        try {
          // Upload file to backend
          const uploadResponse: FileUploadResponse = await dataCollectorAPI.uploadFile(uploadedFile.file);
          
          // Convert file to CommonAPISpec
          const convertResponse: ConvertResponse = await dataCollectorAPI.convertFile(uploadResponse.file_id, true);
          
          if (convertResponse.success) {
            // Create API spec from converted data
                            const apiSpec: APISpec = {
                              id: convertResponse.api_spec_id || 0,
                              name: convertResponse.common_spec?.api_name || uploadedFile.metadata?.name || uploadedFile.file.name,
                              version: convertResponse.common_spec?.version || uploadedFile.metadata?.version || '1.0.0',
                              description: convertResponse.common_spec?.description || uploadedFile.metadata?.description || '',
                              api_type: uploadedFile.type,
                              format: uploadedFile.format,
                              base_url: convertResponse.common_spec?.base_url || uploadedFile.metadata?.baseUrl || '',
                              status: 'draft',
                              application_id: application.id,
                              created_by_id: 1, // This would come from auth context
                              processing_status: 'completed',
                              file_path: '',
                              file_size: uploadedFile.file.size,
                              created_at: new Date().toISOString(),
                              updated_at: new Date().toISOString()
                            };
            
            onApiUploaded(apiSpec);
          } else {
            console.error('Conversion failed:', convertResponse.error);
            alert(`Failed to convert ${uploadedFile.file.name}: ${convertResponse.error}`);
          }
        } catch (error) {
          console.error('Upload/conversion failed for', uploadedFile.file.name, ':', error);
          alert(`Failed to process ${uploadedFile.file.name}: ${error}`);
        }
      }

      setUploadedFiles([]);
      alert(`Successfully processed ${validFiles.length} API specification(s)`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'validating': return '⏳';
      case 'valid': return '✅';
      case 'invalid': return '❌';
      default: return '📄';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validating': return 'text-yellow-600';
      case 'valid': return 'text-green-600';
      case 'invalid': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-xl font-semibold text-gray-900">
          Upload API Specifications
        </h3>
        <p className="text-sm text-gray-600">
          Upload API specifications for <strong>{application.name}</strong> (SEALID: {application.sealid})
        </p>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
              isDragOver 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-4xl text-gray-400 mb-4">📁</div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              {isDragOver ? 'Drop files here!' : 'Drop files here or click to browse'}
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              {isDragOver 
                ? 'Release to upload your API specifications' 
                : 'Upload API specifications for automatic processing and validation'
              }
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <div className="font-medium text-gray-700 mb-2">Supported Formats:</div>
              <div>• <span className="font-medium">Swagger/OpenAPI</span>: .json, .yaml, .yml</div>
              <div>• <span className="font-medium">WSDL</span>: .wsdl (SOAP services)</div>
              <div>• <span className="font-medium">XSD</span>: .xsd (XML schemas)</div>
              <div>• <span className="font-medium">Postman</span>: .json (collections)</div>
            </div>
            <div className="mt-3 text-xs text-blue-600">
              ✓ Automatic validation ✓ Metadata extraction ✓ Type detection
            </div>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".json,.yaml,.yml,.wsdl,.xsd"
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
          />
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4">
              Uploaded Files ({uploadedFiles.length})
            </h4>
            
            <div className="space-y-3">
              {uploadedFiles.map((uploadedFile) => (
                <div
                  key={uploadedFile.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getStatusIcon(uploadedFile.status)}</span>
                    <div>
                      <div className="font-medium text-gray-900">
                        {uploadedFile.file.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {uploadedFile.type} • {uploadedFile.format} • {(uploadedFile.file.size / 1024).toFixed(1)} KB
                      </div>
                      {uploadedFile.metadata && (
                        <div className="text-xs text-gray-500 mt-1">
                          <div>Name: {uploadedFile.metadata.name}</div>
                          <div>Version: {uploadedFile.metadata.version}</div>
                          <div>Base URL: {uploadedFile.metadata.baseUrl}</div>
                        </div>
                      )}
                      {uploadedFile.errors.length > 0 && (
                        <div className="text-sm text-red-600 mt-1">
                          {uploadedFile.errors.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-medium ${getStatusColor(uploadedFile.status)}`}>
                      {uploadedFile.status.charAt(0).toUpperCase() + uploadedFile.status.slice(1)}
                    </span>
                    <button
                      onClick={() => handleFileRemove(uploadedFile.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Upload Actions */}
      {uploadedFiles.length > 0 && (
        <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">
            {uploadedFiles.filter(f => f.status === 'valid').length} valid file(s) ready for upload
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleUpload}
              disabled={isUploading || uploadedFiles.filter(f => f.status === 'valid').length === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiUploader;

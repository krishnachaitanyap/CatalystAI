import React, { useState, useRef } from 'react';

interface Application {
  id: string;
  name: string;
  description: string;
  sealId: string;
  createdAt: string;
  updatedAt: string;
  apiCount: number;
}

interface ApiSpec {
  id: string;
  applicationId: string;
  name: string;
  type: 'REST' | 'SOAP' | 'Postman';
  format: 'Swagger' | 'OpenAPI' | 'WSDL' | 'XSD' | 'Postman Collection';
  version: string;
  description: string;
  baseUrl: string;
  status: 'Active' | 'Draft' | 'Archived';
  createdAt: string;
  updatedAt: string;
}

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
  onApiUploaded: (apiSpec: ApiSpec) => void;
  onBack: () => void;
}

const ApiUploader: React.FC<ApiUploaderProps> = ({
  application,
  onApiUploaded,
  onBack
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File type validation
  const validateFileType = (file: File): { type: string; format: string; isValid: boolean; error?: string } => {
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();

    // REST APIs
    if (fileExtension === 'json' && (fileName.includes('swagger') || fileName.includes('openapi'))) {
      return { type: 'REST', format: 'Swagger', isValid: true };
    }
    if (fileExtension === 'yaml' || fileExtension === 'yml') {
      return { type: 'REST', format: 'OpenAPI', isValid: true };
    }
    if (fileExtension === 'json' && fileName.includes('postman')) {
      return { type: 'Postman', format: 'Postman Collection', isValid: true };
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

  // Basic JSON validation
  const validateJsonFile = async (file: File): Promise<string[]> => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const json = JSON.parse(content);
          
          const errors: string[] = [];
          
          // Basic validation based on file type
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
          } else if (file.name.toLowerCase().includes('postman')) {
            if (!json.info) {
              errors.push('Missing required field: info');
            }
            if (!json.item) {
              errors.push('Missing required field: item');
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

  // Basic XML validation
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
          } else if (file.name.toLowerCase().endsWith('.xsd')) {
            if (!content.includes('<xsd:schema') && !content.includes('<schema')) {
              errors.push('Invalid XSD format: missing schema element');
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
          uploadedFile.metadata = {
            name: file.name.replace(/\.[^/.]+$/, ""),
            version: '1.0.0',
            description: `${validation.format} specification for ${application.name}`,
            baseUrl: 'https://api.example.com'
          };
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

  const handleUpload = async () => {
    const validFiles = uploadedFiles.filter(file => file.status === 'valid');
    
    if (validFiles.length === 0) {
      alert('Please upload at least one valid file');
      return;
    }

    setIsUploading(true);

    try {
      // Simulate upload process
      for (const uploadedFile of validFiles) {
        const apiSpec: ApiSpec = {
          id: `api-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          applicationId: application.id,
          name: uploadedFile.metadata?.name || uploadedFile.file.name,
          type: uploadedFile.type,
          format: uploadedFile.format,
          version: uploadedFile.metadata?.version || '1.0.0',
          description: uploadedFile.metadata?.description || '',
          baseUrl: uploadedFile.metadata?.baseUrl || '',
          status: 'Draft',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        onApiUploaded(apiSpec);
      }

      setUploadedFiles([]);
      alert(`Successfully uploaded ${validFiles.length} API specification(s)`);
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
          Upload API specifications for <strong>{application.name}</strong> (SEALID: {application.sealId})
        </p>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="text-4xl text-gray-400 mb-4">📁</div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              Drop files here or click to browse
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              Support for Swagger/OpenAPI (JSON/YAML), WSDL/XSD, and Postman Collections
            </p>
            <div className="text-xs text-gray-500">
              <div>• REST APIs: .json, .yaml, .yml</div>
              <div>• SOAP APIs: .wsdl, .xsd</div>
              <div>• Postman Collections: .json</div>
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
              onClick={onBack}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Cancel
            </button>
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

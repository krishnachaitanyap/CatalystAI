import React, { useState, useMemo } from 'react';
import { ChevronRightIcon, ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface AttributeNode {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  children?: AttributeNode[];
  level: number;
  path: string;
}

interface AttributeHierarchyViewProps {
  endpoints: any[];
  title: string;
  showRequest?: boolean;
  showResponse?: boolean;
  apiType?: 'REST' | 'SOAP';
}

const AttributeHierarchyView: React.FC<AttributeHierarchyViewProps> = ({ 
  endpoints, 
  title, 
  showRequest = true, 
  showResponse = true,
  apiType = 'REST'
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // Recursively build attribute hierarchy
  const buildAttributeHierarchy = React.useCallback((attributes: any[], parentPath: string, level: number): AttributeNode[] => {
    return attributes.map((attr, index) => {
      const node: AttributeNode = {
        name: attr.name || attr.title || `Attribute ${index + 1}`,
        type: attr.type || 'object',
        description: attr.description,
        required: attr.required,
        level,
        path: `${parentPath}-${index}`,
        children: []
      };

      // Handle nested properties
      if (attr.properties && Array.isArray(attr.properties)) {
        node.children = buildAttributeHierarchy(attr.properties, node.path, level + 1);
      } else if (attr.properties && typeof attr.properties === 'object') {
        node.children = Object.entries(attr.properties).map(([key, value]: [string, any], propIndex) => ({
          name: key,
          type: value.type || 'string',
          description: value.description,
          required: value.required,
          level: level + 1,
          path: `${node.path}-prop-${propIndex}`,
          children: []
        }));
      }

      // Handle nested items (for arrays)
      if (attr.items && attr.items.properties) {
        node.children = buildAttributeHierarchy([attr.items], node.path, level + 1);
      }

      return node;
    });
  }, []);

  // Build hierarchical structure from endpoints/operations
  const attributeTree = useMemo(() => {
    const tree: AttributeNode[] = [];
    
    endpoints.forEach((endpoint, endpointIndex) => {
      let operationNode: AttributeNode;
      
      if (apiType === 'SOAP') {
        // SOAP operations
        operationNode = {
          name: endpoint.operation_name || endpoint.name || `Operation ${endpointIndex + 1}`,
          type: 'operation',
          description: endpoint.description || endpoint.summary,
          level: 0,
          path: `operation-${endpointIndex}`,
          children: []
        };
      } else {
        // REST endpoints
        operationNode = {
          name: `${endpoint.method} ${endpoint.path}`,
          type: 'endpoint',
          description: endpoint.description,
          level: 0,
          path: `endpoint-${endpointIndex}`,
          children: []
        };
      }

      // Add request attributes if showRequest is true
      if (showRequest) {
        if (apiType === 'SOAP') {
          // SOAP-specific request structure
          
          // SOAP Headers
          if (endpoint.soap_headers && endpoint.soap_headers.length > 0) {
            const headersNode: AttributeNode = {
              name: 'SOAP Headers',
              type: 'group',
              level: 1,
              path: `operation-${endpointIndex}-headers`,
              children: endpoint.soap_headers.map((header: any, headerIndex: number) => ({
                name: header.name,
                type: header.type || 'string',
                description: header.description,
                required: header.required,
                level: 2,
                path: `operation-${endpointIndex}-headers-${headerIndex}`,
                children: []
              }))
            };
            operationNode.children!.push(headersNode);
          }

          // SOAP Body (input message)
          if (endpoint.input_message && endpoint.input_message.all_attributes && endpoint.input_message.all_attributes.length > 0) {
            const inputNode: AttributeNode = {
              name: 'SOAP Body (Input)',
              type: 'group',
              level: 1,
              path: `operation-${endpointIndex}-input`,
              children: buildAttributeHierarchy(endpoint.input_message.all_attributes, `operation-${endpointIndex}-input`, 2)
            };
            operationNode.children!.push(inputNode);
          }
        } else {
          // REST-specific request structure
          
          // Request parameters
          if (endpoint.parameters && endpoint.parameters.length > 0) {
            const requestNode: AttributeNode = {
              name: 'Request Parameters',
              type: 'group',
              level: 1,
              path: `endpoint-${endpointIndex}-request`,
              children: endpoint.parameters.map((param: any, paramIndex: number) => ({
                name: param.name,
                type: param.type || 'string',
                description: param.description,
                required: param.required,
                level: 2,
                path: `endpoint-${endpointIndex}-request-${paramIndex}`,
                children: []
              }))
            };
            operationNode.children!.push(requestNode);
          }

          // Request body attributes
          if (endpoint.request_body && endpoint.request_body.all_attributes && endpoint.request_body.all_attributes.length > 0) {
            const requestBodyNode: AttributeNode = {
              name: 'Request Body',
              type: 'group',
              level: 1,
              path: `endpoint-${endpointIndex}-request-body`,
              children: buildAttributeHierarchy(endpoint.request_body.all_attributes, `endpoint-${endpointIndex}-request-body`, 2)
            };
            operationNode.children!.push(requestBodyNode);
          }
        }
      }

      // Add response attributes if showResponse is true
      if (showResponse) {
        if (apiType === 'SOAP') {
          // SOAP-specific response structure
          
          // SOAP Output Message
          if (endpoint.output_message && endpoint.output_message.all_attributes && endpoint.output_message.all_attributes.length > 0) {
            const outputNode: AttributeNode = {
              name: 'SOAP Body (Output)',
              type: 'group',
              level: 1,
              path: `operation-${endpointIndex}-output`,
              children: buildAttributeHierarchy(endpoint.output_message.all_attributes, `operation-${endpointIndex}-output`, 2)
            };
            operationNode.children!.push(outputNode);
          }
        } else {
          // REST-specific response structure
          Object.entries(endpoint.responses || {}).forEach(([statusCode, response]: [string, any]) => {
            if (response.all_attributes && response.all_attributes.length > 0) {
              const responseNode: AttributeNode = {
                name: `Response ${statusCode}`,
                type: 'group',
                level: 1,
                path: `endpoint-${endpointIndex}-response-${statusCode}`,
                children: buildAttributeHierarchy(response.all_attributes, `endpoint-${endpointIndex}-response-${statusCode}`, 2)
              };
              operationNode.children!.push(responseNode);
            }
          });
        }
      }

      // Only add operation/endpoint if it has children
      if (operationNode.children!.length > 0) {
        tree.push(operationNode);
      }
    });

    return tree;
  }, [endpoints, showRequest, showResponse, apiType, buildAttributeHierarchy]);

  // Filter tree based on search term
  const filteredTree = useMemo(() => {
    if (!searchTerm.trim()) return attributeTree;

    const filterNode = (node: AttributeNode): AttributeNode | null => {
      const matchesSearch = node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           node.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           node.type.toLowerCase().includes(searchTerm.toLowerCase());

      const filteredChildren = node.children?.map(filterNode).filter(Boolean) as AttributeNode[] || [];

      if (matchesSearch || filteredChildren.length > 0) {
        return {
          ...node,
          children: filteredChildren
        };
      }

      return null;
    };

    return attributeTree.map(filterNode).filter(Boolean) as AttributeNode[];
  }, [attributeTree, searchTerm]);

  // Toggle node expansion
  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  // Expand all nodes
  const expandAll = () => {
    const allPaths = new Set<string>();
    const collectPaths = (nodes: AttributeNode[]) => {
      nodes.forEach(node => {
        if (node.children && node.children.length > 0) {
          allPaths.add(node.path);
          collectPaths(node.children);
        }
      });
    };
    collectPaths(attributeTree);
    setExpandedNodes(allPaths);
  };

  // Collapse all nodes
  const collapseAll = () => {
    setExpandedNodes(new Set());
  };

  // Render a single node
  const renderNode = (node: AttributeNode) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedNodes.has(node.path);
    const indentClass = `ml-${node.level * 4}`;

    return (
      <div key={node.path} className={`${indentClass} py-1`}>
        <div className="flex items-center space-x-2 py-1 hover:bg-gray-50 rounded px-2">
          {hasChildren ? (
            <button
              onClick={() => toggleNode(node.path)}
              className="flex items-center justify-center w-4 h-4 text-gray-500 hover:text-gray-700"
            >
              {isExpanded ? (
                <ChevronDownIcon className="w-3 h-3" />
              ) : (
                <ChevronRightIcon className="w-3 h-3" />
              )}
            </button>
          ) : (
            <div className="w-4 h-4" />
          )}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className={`font-medium text-sm ${
                node.type === 'endpoint' ? 'text-blue-600' :
                node.type === 'operation' ? 'text-purple-600' :
                node.type === 'group' ? 'text-green-600' :
                'text-gray-900'
              }`}>
                {node.name}
              </span>
              <span className="px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                {node.type}
              </span>
              {node.required && (
                <span className="px-1.5 py-0.5 text-xs bg-red-100 text-red-600 rounded">
                  required
                </span>
              )}
            </div>
            {node.description && (
              <p className="text-xs text-gray-500 mt-0.5 truncate">
                {node.description}
              </p>
            )}
          </div>
        </div>
        
        {hasChildren && isExpanded && (
          <div className="ml-4">
            {node.children!.map(renderNode)}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-medium text-gray-900">{title}</h5>
        <div className="flex space-x-2">
          <button
            onClick={expandAll}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="text-xs text-gray-600 hover:text-gray-800"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
        </div>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
          placeholder="Search attributes..."
        />
      </div>

      {/* Attributes Tree */}
      <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
        {filteredTree.length > 0 ? (
          <div className="space-y-1">
            {filteredTree.map(renderNode)}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔍</div>
            <p className="text-sm">
              {searchTerm ? 'No attributes match your search' : 'No attributes found'}
            </p>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="text-xs text-gray-500">
        {searchTerm ? (
          <span>
            Showing {filteredTree.length} matching attribute(s) out of {attributeTree.length} total
          </span>
        ) : (
          <span>
            {attributeTree.length} endpoint(s) with attributes
          </span>
        )}
      </div>
    </div>
  );
};

export default AttributeHierarchyView;

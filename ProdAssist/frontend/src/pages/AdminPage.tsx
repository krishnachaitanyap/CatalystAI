import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  Avatar,
  Fade,
  Slide,
  Zoom,
  InputAdornment,
} from '@mui/material';
import {
  Add as AddIcon,
  Upload as UploadIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Link as LinkIcon,
  Code as CodeIcon,
  Cloud as CloudIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  Api as ApiIcon,
  Apps as AppsIcon,
  CloudQueue as CloudQueueIcon,
  Security as SecurityIcon,
  Analytics as AnalyticsIcon,
  Storage as StorageIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

import { useAPISpecStore } from '../hooks/useAPISpecStore';
import { APISpec, APISpecForm } from '../types';

const drawerWidth = 280;

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

const AdminPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [mcpDialogOpen, setMcpDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const {
    specs,
    isLoading: loading,
    error,
    loadSpecs,
    uploadFile,
  } = useAPISpecStore();

  const [uploadForm, setUploadForm] = useState({
    sealId: '',
    application: '',
    file: null as File | null,
  });

  const [mcpForm, setMcpForm] = useState({
    name: '',
    type: 'grafana',
    url: '',
    apiKey: '',
  });

  const navigationItems: NavigationItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'api-specs', label: 'API Specifications', icon: <ApiIcon />, badge: specs.length },
    { id: 'applications', label: 'Applications', icon: <AppsIcon /> },
    { id: 'mcp-connections', label: 'MCP Connections', icon: <CloudQueueIcon /> },
    { id: 'analytics', label: 'Analytics', icon: <AnalyticsIcon /> },
    { id: 'storage', label: 'Storage', icon: <StorageIcon /> },
    { id: 'security', label: 'Security', icon: <SecurityIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
  ];

  React.useEffect(() => {
    loadSpecs();
  }, [loadSpecs]);

  const handleFileUpload = async () => {
    if (!uploadForm.file || !uploadForm.sealId || !uploadForm.application) {
      return;
    }

    try {
      await uploadFile(uploadForm.file, uploadForm.sealId, uploadForm.application);
      setUploadDialogOpen(false);
      setUploadForm({ sealId: '', application: '', file: null });
      loadSpecs();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleMcpConnection = async () => {
    // TODO: Implement MCP server connection
    console.log('MCP Connection:', mcpForm);
    setMcpDialogOpen(false);
    setMcpForm({ name: '', type: 'grafana', url: '', apiKey: '' });
  };

  const getSpecStatusIcon = (spec: APISpec) => {
    switch (spec.status) {
      case 'active':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <CheckCircleIcon color="disabled" />;
    }
  };

  const getSpecTypeChip = (spec: APISpec) => {
    const isREST = spec.spec_type === 'REST' || spec.file_name?.includes('.json') || spec.file_name?.includes('.yaml');
    const isSOAP = spec.spec_type === 'SOAP' || spec.file_name?.includes('.wsdl') || spec.file_name?.includes('.xsd');
    
    if (isREST) {
      return <Chip label="REST" color="primary" size="small" />;
    } else if (isSOAP) {
      return <Chip label="SOAP" color="secondary" size="small" />;
    }
    return <Chip label={spec.spec_type || 'Unknown'} variant="outlined" size="small" />;
  };

  const filteredSpecs = specs.filter(spec => {
    const matchesSearch = spec.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          spec.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          spec.seal_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          spec.application?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = filterType === 'all' || 
                          (filterType === 'rest' && (spec.spec_type === 'REST' || spec.file_name?.includes('.json') || spec.file_name?.includes('.yaml'))) ||
                          (filterType === 'soap' && (spec.spec_type === 'SOAP' || spec.file_name?.includes('.wsdl') || spec.file_name?.includes('.xsd')));
    
    return matchesSearch && matchesFilter;
  });

  const renderSidebar = () => (
    <Drawer
      variant="persistent"
      anchor="left"
      open={sidebarOpen}
      sx={{
        width: sidebarOpen ? drawerWidth : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid rgba(0, 0, 0, 0.06)',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
        },
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Sidebar Header */}
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(0, 0, 0, 0.06)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary' }}>
              Admin Panel
            </Typography>
            <IconButton
              onClick={() => setSidebarOpen(false)}
              size="small"
              sx={{
                backgroundColor: 'rgba(0, 0, 0, 0.04)',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.08)',
                },
              }}
            >
              <ChevronLeftIcon />
            </IconButton>
          </Box>
          
          <Button
            fullWidth
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setUploadDialogOpen(true)}
            sx={{ 
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            Upload API Spec
          </Button>
        </Box>

        {/* Navigation */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 1 }}>
          <List>
            {navigationItems.map((item, index) => (
              <Slide direction="right" in timeout={200 + index * 50} key={item.id}>
                <ListItem disablePadding>
                  <ListItemButton
                    selected={activeSection === item.id}
                    onClick={() => setActiveSection(item.id)}
                    sx={{
                      borderRadius: 2,
                      mx: 1,
                      mb: 1,
                      py: 1.5,
                      px: 2,
                      '&.Mui-selected': {
                        background: 'linear-gradient(135deg, rgba(0, 122, 255, 0.12) 0%, rgba(88, 86, 214, 0.12) 100%)',
                        color: 'primary.main',
                        '&:hover': {
                          background: 'linear-gradient(135deg, rgba(0, 122, 255, 0.16) 0%, rgba(88, 86, 214, 0.16) 100%)',
                        },
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {item.badge ? (
                        <Badge badgeContent={item.badge} color="primary">
                          {item.icon}
                        </Badge>
                      ) : (
                        item.icon
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: activeSection === item.id ? 600 : 500,
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              </Slide>
            ))}
          </List>
        </Box>
      </Box>
    </Drawer>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Dashboard
            </Typography>
            
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={3}>
                <Card sx={{ p: 3, background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)', color: 'white' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h3" sx={{ fontWeight: 700 }}>
                        {specs.length}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        API Specifications
                      </Typography>
                    </Box>
                    <ApiIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card sx={{ p: 3, background: 'linear-gradient(135deg, #34C759 0%, #30D158 100%)', color: 'white' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h3" sx={{ fontWeight: 700 }}>
                        {specs.filter(s => s.status === 'active').length}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        Active APIs
                      </Typography>
                    </Box>
                    <CheckCircleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card sx={{ p: 3, background: 'linear-gradient(135deg, #FF9500 0%, #FF6B00 100%)', color: 'white' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h3" sx={{ fontWeight: 700 }}>
                        {specs.filter(s => s.spec_type === 'REST').length}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        REST APIs
                      </Typography>
                    </Box>
                    <CodeIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={3}>
                <Card sx={{ p: 3, background: 'linear-gradient(135deg, #AF52DE 0%, #8E44AD 100%)', color: 'white' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h3" sx={{ fontWeight: 700 }}>
                        {specs.filter(s => s.spec_type === 'SOAP').length}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        SOAP APIs
                      </Typography>
                    </Box>
                    <CloudIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </Card>
              </Grid>
            </Grid>
            
            <Card sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Activity monitoring and analytics coming soon.
              </Typography>
            </Card>
          </Box>
        );

      case 'api-specs':
        return (
          <Box sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
                API Specifications
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Tooltip title="Refresh">
                  <IconButton onClick={() => loadSpecs()}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setUploadDialogOpen(true)}
                >
                  Upload New
                </Button>
              </Box>
            </Box>
            
            {/* Search and Filter */}
            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
              <TextField
                placeholder="Search API specifications..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
                sx={{ flex: 1 }}
              />
              <TextField
                select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                sx={{ minWidth: 120 }}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="rest">REST</MenuItem>
                <MenuItem value="soap">SOAP</MenuItem>
              </TextField>
            </Box>
            
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            )}
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <Grid container spacing={3}>
              {filteredSpecs.map((spec, index) => (
                <Grid item xs={12} md={6} lg={4} key={spec.id}>
                  <Fade in timeout={300 + index * 100}>
                    <Card sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                      },
                    }}>
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                          <Typography variant="h6" noWrap sx={{ fontWeight: 600 }}>
                            {spec.name}
                          </Typography>
                          {getSpecStatusIcon(spec)}
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 40 }}>
                          {spec.description || 'No description available'}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                          {getSpecTypeChip(spec)}
                          <Chip label={`Seal: ${spec.seal_id}`} variant="outlined" size="small" />
                          <Chip label={`App: ${spec.application}`} variant="outlined" size="small" />
                        </Box>
                        
                        {spec.file_name && (
                          <Typography variant="caption" color="text.secondary">
                            File: {spec.file_name}
                          </Typography>
                        )}
                      </CardContent>
                      
                      <CardActions sx={{ p: 2, pt: 0 }}>
                        <Button size="small" startIcon={<VisibilityIcon />}>
                          View
                        </Button>
                        <Button size="small" startIcon={<EditIcon />}>
                          Edit
                        </Button>
                        <Button size="small" startIcon={<DownloadIcon />}>
                          Download
                        </Button>
                        <Box sx={{ flexGrow: 1 }} />
                        <IconButton size="small" color="error">
                          <DeleteIcon />
                        </IconButton>
                      </CardActions>
                    </Card>
                  </Fade>
                </Grid>
              ))}
            </Grid>
            
            {filteredSpecs.length === 0 && !loading && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                  No API specifications found
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Upload your first API specification to get started
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setUploadDialogOpen(true)}
                >
                  Upload API Spec
                </Button>
              </Box>
            )}
          </Box>
        );

      case 'applications':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Applications
            </Typography>
            <Card sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Application Management
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Organize and manage your applications. This feature will allow you to group API specifications by application and manage application-level settings.
              </Typography>
              <Button variant="outlined" startIcon={<AppsIcon />}>
                Coming Soon
              </Button>
            </Card>
          </Box>
        );

      case 'mcp-connections':
        return (
          <Box sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
                MCP Server Connections
              </Typography>
              <Button
                variant="contained"
                startIcon={<LinkIcon />}
                onClick={() => setMcpDialogOpen(true)}
              >
                Add Connection
              </Button>
            </Box>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card sx={{ 
                  height: '100%',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                  },
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                        <CloudIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>Grafana</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Connect to Grafana for monitoring and observability data. Get real-time metrics and dashboards.
                    </Typography>
                    <Button variant="outlined" size="small" fullWidth>
                      Configure
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card sx={{ 
                  height: '100%',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                  },
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                        <CodeIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>Dynatrace</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Connect to Dynatrace for application performance monitoring. Track performance metrics and alerts.
                    </Typography>
                    <Button variant="outlined" size="small" fullWidth>
                      Configure
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card sx={{ 
                  height: '100%',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                  },
                }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                        <SettingsIcon />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>Splunk</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      Connect to Splunk for log analysis and monitoring. Search and analyze application logs.
                    </Typography>
                    <Button variant="outlined" size="small" fullWidth>
                      Configure
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        );

      case 'analytics':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Analytics
            </Typography>
            <Card sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Usage Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Track API usage, performance metrics, and user behavior. Analytics dashboard coming soon.
              </Typography>
              <Button variant="outlined" startIcon={<AnalyticsIcon />}>
                Coming Soon
              </Button>
            </Card>
          </Box>
        );

      case 'storage':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Storage Management
            </Typography>
            <Card sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Vector Database
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Manage your vector database storage, chunking strategies, and search configurations.
              </Typography>
              <Button variant="outlined" startIcon={<StorageIcon />}>
                Coming Soon
              </Button>
            </Card>
          </Box>
        );

      case 'security':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Security
            </Typography>
            <Card sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Security Settings
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure authentication, authorization, and security policies for your API specifications.
              </Typography>
              <Button variant="outlined" startIcon={<SecurityIcon />}>
                Coming Soon
              </Button>
            </Card>
          </Box>
        );

      case 'settings':
        return (
          <Box sx={{ p: 4 }}>
            <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: 'text.primary' }}>
              Settings
            </Typography>
            <Card sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Application Settings
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure application-wide settings, preferences, and system configurations.
              </Typography>
              <Button variant="outlined" startIcon={<SettingsIcon />}>
                Coming Soon
              </Button>
            </Card>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex' }}>
      {/* Sidebar */}
      {renderSidebar()}

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderRadius: 0,
            borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            {!sidebarOpen && (
              <IconButton 
                onClick={() => setSidebarOpen(true)}
                sx={{
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.08)',
                  },
                }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 700,
                  fontSize: '1.25rem',
                }}
              >
                P
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
                ProdAssist Admin
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Back to Chat">
              <IconButton
                onClick={() => window.location.href = '/chat'}
                size="small"
              >
                <ChevronLeftIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>

        {/* Content Area */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            background: 'linear-gradient(135deg, #F2F2F7 0%, #E5E5EA 100%)',
          }}
        >
          {renderContent()}
        </Box>
      </Box>


      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload API Specification</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Seal ID"
              value={uploadForm.sealId}
              onChange={(e) => setUploadForm({ ...uploadForm, sealId: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Application"
              value={uploadForm.application}
              onChange={(e) => setUploadForm({ ...uploadForm, application: e.target.value })}
              sx={{ mb: 2 }}
            />
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadIcon />}
              fullWidth
              sx={{ mb: 2 }}
            >
              Choose File
              <input
                ref={fileInputRef}
                type="file"
                hidden
                accept=".json,.yaml,.yml,.wsdl,.xsd"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setUploadForm({ ...uploadForm, file });
                  }
                }}
              />
            </Button>
            {uploadForm.file && (
              <Typography variant="body2" color="text.secondary">
                Selected: {uploadForm.file.name}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!uploadForm.file || !uploadForm.sealId || !uploadForm.application}
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>

      {/* MCP Connection Dialog */}
      <Dialog open={mcpDialogOpen} onClose={() => setMcpDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add MCP Server Connection</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Connection Name"
              value={mcpForm.name}
              onChange={(e) => setMcpForm({ ...mcpForm, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              select
              label="Server Type"
              value={mcpForm.type}
              onChange={(e) => setMcpForm({ ...mcpForm, type: e.target.value })}
              sx={{ mb: 2 }}
            >
              <MenuItem value="grafana">Grafana</MenuItem>
              <MenuItem value="dynatrace">Dynatrace</MenuItem>
              <MenuItem value="splunk">Splunk</MenuItem>
            </TextField>
            <TextField
              fullWidth
              label="Server URL"
              value={mcpForm.url}
              onChange={(e) => setMcpForm({ ...mcpForm, url: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="API Key"
              type="password"
              value={mcpForm.apiKey}
              onChange={(e) => setMcpForm({ ...mcpForm, apiKey: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMcpDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleMcpConnection}
            variant="contained"
            disabled={!mcpForm.name || !mcpForm.url || !mcpForm.apiKey}
          >
            Connect
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPage;

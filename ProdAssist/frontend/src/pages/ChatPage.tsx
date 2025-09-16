import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemAvatar,
  Divider,
  Button,
  InputAdornment,
  Fade,
  Slide,
  Zoom,
} from '@mui/material';
import {
  Send as SendIcon,
  MoreVert as MoreVertIcon,
  AdminPanelSettings as AdminIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Menu as MenuIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  ChevronLeft as ChevronLeftIcon,
  AutoAwesome as SparklesIcon,
  Code as CodeIcon,
  Cloud as CloudIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { useChatStore } from '../hooks/useChatStore';
import { useAuthStore } from '../hooks/useAuthStore';
import { ChatMessage } from '../types';

const drawerWidth = 320;

const ChatPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingSession, setEditingSession] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    currentSession,
    sessions,
    messages,
    loadSessions,
    createSession,
    sendMessage,
    deleteSession,
    loadMessages,
  } = useChatStore();
  
  const { user } = useAuthStore();

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (currentSession) {
      loadMessages(currentSession.id);
    }
  }, [currentSession, loadMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !currentSession || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      await sendMessage(currentSession.id, userMessage, true);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = async () => {
    try {
      await createSession({ title: 'New Chat' });
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
  };

  const handleDeleteSession = async () => {
    if (!currentSession) return;
    
    try {
      await deleteSession(currentSession.id);
      setAnchorEl(null);
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleSessionClick = async (sessionId: number) => {
    try {
      await loadMessages(sessionId);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const handleEditSession = (sessionId: number, currentTitle: string) => {
    setEditingSession(sessionId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async () => {
    if (editingSession && editTitle.trim()) {
      // TODO: Implement session title update
      console.log('Update session title:', editingSession, editTitle);
      setEditingSession(null);
      setEditTitle('');
    }
  };

  const handleCancelEdit = () => {
    setEditingSession(null);
    setEditTitle('');
  };

  const filteredSessions = sessions.filter(session =>
    session.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    session.id.toString().includes(searchQuery)
  );

  const renderMessage = (message: ChatMessage, index: number) => {
    const isUser = message.role === 'user';
    
    return (
      <Fade in timeout={300} key={message.id}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: isUser ? 'flex-end' : 'flex-start',
            mb: 3,
            px: 3,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 2,
              maxWidth: '75%',
              flexDirection: isUser ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                background: isUser 
                  ? 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)'
                  : 'linear-gradient(135deg, #34C759 0%, #30D158 100%)',
                color: 'white',
                fontSize: '0.875rem',
                fontWeight: 600,
                boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
              }}
            >
              {isUser ? user?.username?.[0]?.toUpperCase() || 'U' : 'AI'}
            </Avatar>
            
            <Paper
              sx={{
                p: 2.5,
                background: isUser 
                  ? 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)'
                  : 'rgba(255, 255, 255, 0.95)',
                color: isUser ? 'white' : 'text.primary',
                borderRadius: 3,
                maxWidth: '100%',
                wordBreak: 'break-word',
                boxShadow: isUser 
                  ? '0px 8px 24px rgba(0, 122, 255, 0.3)'
                  : '0px 4px 20px rgba(0, 0, 0, 0.08)',
                backdropFilter: 'blur(20px)',
                border: isUser 
                  ? 'none'
                  : '1px solid rgba(255, 255, 255, 0.2)',
                position: 'relative',
                '&::before': isUser ? {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                  borderRadius: 3,
                  pointerEvents: 'none',
                } : {},
              }}
            >
              {isUser ? (
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', fontWeight: 400 }}>
                  {message.content}
                </Typography>
              ) : (
                <Box sx={{ '& *': { color: 'inherit !important' } }}>
                  <ReactMarkdown
                    components={{
                      code({ node, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        const inline = !match;
                        
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={tomorrow as any}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                            customStyle={{
                              borderRadius: 8,
                              margin: '8px 0',
                              fontSize: '0.875rem',
                            }}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code 
                            className={className} 
                            {...props}
                            style={{
                              backgroundColor: 'rgba(0, 0, 0, 0.05)',
                              padding: '2px 6px',
                              borderRadius: 4,
                              fontSize: '0.875rem',
                              fontFamily: 'SF Mono, Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
                            }}
                          >
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </Box>
              )}
            </Paper>
          </Box>
          
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              mt: 1,
              mx: 1,
              fontSize: '0.75rem',
              fontWeight: 500,
            }}
          >
            {new Date(message.created_at).toLocaleTimeString()}
          </Typography>
        </Box>
      </Fade>
    );
  };

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
          borderRight: '1px solid rgba(255, 255, 255, 0.2)',
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
              Chat History
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
            onClick={handleNewChat}
            sx={{ 
              mb: 3,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            New Chat
          </Button>
          
          <TextField
            fullWidth
            size="small"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                backgroundColor: 'rgba(0, 0, 0, 0.02)',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
                '&.Mui-focused': {
                  backgroundColor: 'rgba(255, 255, 255, 1)',
                },
              },
            }}
          />
        </Box>

        {/* Sessions List */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 1 }}>
          <List>
            {filteredSessions.map((session, index) => (
              <Slide direction="right" in timeout={200 + index * 50} key={session.id}>
                <ListItem disablePadding>
                  <ListItemButton
                    selected={currentSession?.id === session.id}
                    onClick={() => handleSessionClick(session.id)}
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
                    <ListItemAvatar>
                      <Avatar 
                        sx={{ 
                          width: 32, 
                          height: 32, 
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                        }}
                      >
                        {session.title?.[0]?.toUpperCase() || 'C'}
                      </Avatar>
                    </ListItemAvatar>
                    
                    {editingSession === session.id ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                        <TextField
                          size="small"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onClick={(e) => e.stopPropagation()}
                          sx={{ flex: 1 }}
                        />
                        <IconButton size="small" onClick={handleSaveEdit}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={handleCancelEdit}>
                          <CloseIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    ) : (
                      <>
                        <ListItemText
                          primary={session.title || `Chat ${session.id}`}
                          secondary={new Date(session.created_at).toLocaleDateString()}
                          primaryTypographyProps={{
                            fontSize: '0.875rem',
                            fontWeight: currentSession?.id === session.id ? 600 : 500,
                          }}
                          secondaryTypographyProps={{
                            fontSize: '0.75rem',
                            color: 'text.secondary',
                          }}
                        />
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditSession(session.id, session.title || `Chat ${session.id}`);
                          }}
                        >
                          <MoreVertIcon fontSize="small" />
                        </IconButton>
                      </>
                    )}
                  </ListItemButton>
                </ListItem>
              </Slide>
            ))}
          </List>
        </Box>
      </Box>
    </Drawer>
  );

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
                ProdAssist
              </Typography>
            </Box>
            {currentSession && (
              <Chip
                label={currentSession.title || `Chat ${currentSession.id}`}
                size="small"
                sx={{
                  backgroundColor: 'rgba(0, 122, 255, 0.1)',
                  color: 'primary.main',
                  fontWeight: 500,
                }}
              />
            )}
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {currentSession && (
              <>
                <Tooltip title="Chat Options">
                  <IconButton
                    onClick={(e) => setAnchorEl(e.currentTarget)}
                    size="small"
                  >
                    <MoreVertIcon />
                  </IconButton>
                </Tooltip>
                
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={() => setAnchorEl(null)}
                  PaperProps={{
                    sx: {
                      borderRadius: 2,
                      boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                    },
                  }}
                >
                  <MenuItem onClick={handleDeleteSession}>
                    <ListItemIcon>
                      <DeleteIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Delete Chat</ListItemText>
                  </MenuItem>
                </Menu>
              </>
            )}
            
            <Tooltip title="Admin Panel">
              <IconButton
                onClick={() => window.location.href = '/admin'}
                size="small"
              >
                <AdminIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>

        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            py: 2,
            background: 'linear-gradient(135deg, #F2F2F7 0%, #E5E5EA 100%)',
          }}
        >
          {messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                textAlign: 'center',
                px: 4,
              }}
            >
              <Zoom in timeout={500}>
                <Box
                  sx={{
                    width: 120,
                    height: 120,
                    borderRadius: 6,
                    background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 4,
                    boxShadow: '0px 20px 40px rgba(0, 122, 255, 0.3)',
                  }}
                >
                  <SparklesIcon sx={{ fontSize: 48, color: 'white' }} />
                </Box>
              </Zoom>
              
              <Typography variant="h3" sx={{ mb: 2, fontWeight: 700, color: 'text.primary' }}>
                Welcome to ProdAssist
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, color: 'text.secondary', fontWeight: 400 }}>
                Your AI-powered assistant for API specifications and development
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 600 }}>
                <Chip 
                  icon={<CodeIcon />}
                  label="Upload API specs" 
                  variant="outlined" 
                  sx={{ 
                    py: 2, 
                    px: 1,
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }} 
                />
                <Chip 
                  icon={<CloudIcon />}
                  label="Connect to monitoring tools" 
                  variant="outlined" 
                  sx={{ 
                    py: 2, 
                    px: 1,
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }} 
                />
                <Chip 
                  icon={<SettingsIcon />}
                  label="Get code examples" 
                  variant="outlined" 
                  sx={{ 
                    py: 2, 
                    px: 1,
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }} 
                />
                <Chip 
                  icon={<SparklesIcon />}
                  label="Debug API issues" 
                  variant="outlined" 
                  sx={{ 
                    py: 2, 
                    px: 1,
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }} 
                />
              </Box>
            </Box>
          ) : (
            <>
              {messages.map(renderMessage)}
              {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                  <CircularProgress 
                    size={32} 
                    sx={{ 
                      color: 'primary.main',
                    }} 
                  />
                </Box>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>

        {/* Input Area */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            borderRadius: 0,
            borderTop: '1px solid rgba(0, 0, 0, 0.06)',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(20px)',
          }}
        >
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end', maxWidth: 1200, mx: 'auto' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your APIs..."
              disabled={isLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  backgroundColor: 'rgba(0, 0, 0, 0.02)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                  '&.Mui-focused': {
                    backgroundColor: 'rgba(255, 255, 255, 1)',
                    boxShadow: '0px 0px 0px 3px rgba(0, 122, 255, 0.1)',
                  },
                },
              }}
            />
            <IconButton
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              sx={{
                width: 48,
                height: 48,
                background: input.trim() 
                  ? 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)'
                  : 'rgba(0, 0, 0, 0.04)',
                color: input.trim() ? 'white' : 'text.secondary',
                borderRadius: 3,
                '&:hover': {
                  background: input.trim() 
                    ? 'linear-gradient(135deg, #0056CC 0%, #3D3C9E 100%)'
                    : 'rgba(0, 0, 0, 0.08)',
                  transform: 'scale(1.05)',
                },
                '&:disabled': {
                  background: 'rgba(0, 0, 0, 0.04)',
                  color: 'text.disabled',
                  transform: 'none',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

export default ChatPage;
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Pages
import ChatPage from './pages/ChatPage';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';

// Components
import ProtectedRoute from './components/common/ProtectedRoute';
import AdminRoute from './components/common/AdminRoute';

// Hooks
import { useAuthStore } from './hooks/useAuthStore';

// Apple-inspired premium theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#007AFF', // Apple Blue
      light: '#4DA6FF',
      dark: '#0056CC',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#5856D6', // Apple Purple
      light: '#8B8AE5',
      dark: '#3D3C9E',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F2F2F7', // Apple Light Gray
      paper: '#FFFFFF',
    },
    surface: {
      main: '#FFFFFF',
      light: '#F8F9FA',
      dark: '#E5E5EA',
    },
    text: {
      primary: '#1D1D1F', // Apple Dark Gray
      secondary: '#86868B', // Apple Medium Gray
      disabled: '#C7C7CC',
    },
    grey: {
      50: '#F9F9F9',
      100: '#F2F2F7',
      200: '#E5E5EA',
      300: '#D1D1D6',
      400: '#C7C7CC',
      500: '#AEAEB2',
      600: '#8E8E93',
      700: '#636366',
      800: '#48484A',
      900: '#1D1D1F',
    },
    success: {
      main: '#34C759', // Apple Green
      light: '#5DD679',
      dark: '#28A745',
    },
    warning: {
      main: '#FF9500', // Apple Orange
      light: '#FFB84D',
      dark: '#E6850E',
    },
    error: {
      main: '#FF3B30', // Apple Red
      light: '#FF6B60',
      dark: '#E5342A',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"SF Pro Display"',
      '"SF Pro Text"',
      '"Helvetica Neue"',
      'Helvetica',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      letterSpacing: '0em',
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 600,
      letterSpacing: '0em',
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      letterSpacing: '0em',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      letterSpacing: '0em',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      letterSpacing: '0em',
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem',
      fontWeight: 400,
      letterSpacing: '0em',
      lineHeight: 1.4,
    },
    button: {
      fontSize: '1rem',
      fontWeight: 500,
      letterSpacing: '0em',
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 3px rgba(0, 0, 0, 0.05)',
    '0px 2px 6px rgba(0, 0, 0, 0.05)',
    '0px 4px 12px rgba(0, 0, 0, 0.05)',
    '0px 8px 24px rgba(0, 0, 0, 0.05)',
    '0px 12px 32px rgba(0, 0, 0, 0.05)',
    '0px 16px 40px rgba(0, 0, 0, 0.05)',
    '0px 20px 48px rgba(0, 0, 0, 0.05)',
    '0px 24px 56px rgba(0, 0, 0, 0.05)',
    '0px 28px 64px rgba(0, 0, 0, 0.05)',
    '0px 32px 72px rgba(0, 0, 0, 0.05)',
    '0px 36px 80px rgba(0, 0, 0, 0.05)',
    '0px 40px 88px rgba(0, 0, 0, 0.05)',
    '0px 44px 96px rgba(0, 0, 0, 0.05)',
    '0px 48px 104px rgba(0, 0, 0, 0.05)',
    '0px 52px 112px rgba(0, 0, 0, 0.05)',
    '0px 56px 120px rgba(0, 0, 0, 0.05)',
    '0px 60px 128px rgba(0, 0, 0, 0.05)',
    '0px 64px 136px rgba(0, 0, 0, 0.05)',
    '0px 68px 144px rgba(0, 0, 0, 0.05)',
    '0px 72px 152px rgba(0, 0, 0, 0.05)',
    '0px 76px 160px rgba(0, 0, 0, 0.05)',
    '0px 80px 168px rgba(0, 0, 0, 0.05)',
    '0px 84px 176px rgba(0, 0, 0, 0.05)',
    '0px 88px 184px rgba(0, 0, 0, 0.05)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          fontWeight: 500,
          textTransform: 'none',
          padding: '12px 24px',
          fontSize: '1rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
            transform: 'translateY(-1px)',
            transition: 'all 0.2s ease-in-out',
          },
          '&:active': {
            transform: 'translateY(0px)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #0056CC 0%, #3D3C9E 100%)',
          },
        },
        outlined: {
          borderWidth: '1.5px',
          '&:hover': {
            borderWidth: '1.5px',
            backgroundColor: 'rgba(0, 122, 255, 0.04)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(10px)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
            },
            '&.Mui-focused': {
              backgroundColor: 'rgba(255, 255, 255, 1)',
              boxShadow: '0px 0px 0px 3px rgba(0, 122, 255, 0.1)',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        elevation1: {
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.04), 0px 1px 3px rgba(0, 0, 0, 0.1)',
        },
        elevation2: {
          boxShadow: '0px 4px 16px rgba(0, 0, 0, 0.06), 0px 2px 6px rgba(0, 0, 0, 0.1)',
        },
        elevation3: {
          boxShadow: '0px 8px 24px rgba(0, 0, 0, 0.08), 0px 4px 12px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.04)',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.08)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
          fontSize: '0.875rem',
        },
      },
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          fontWeight: 600,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'rgba(0, 122, 255, 0.08)',
            transform: 'scale(1.05)',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRight: '1px solid rgba(255, 255, 255, 0.2)',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          margin: '2px 8px',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'rgba(0, 122, 255, 0.08)',
            transform: 'translateX(4px)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 122, 255, 0.12)',
            '&:hover': {
              backgroundColor: 'rgba(0, 122, 255, 0.16)',
            },
          },
        },
      },
    },
  },
});

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box 
          sx={{ 
            height: '100vh', 
            display: 'flex', 
            flexDirection: 'column',
            background: 'linear-gradient(135deg, #F2F2F7 0%, #E5E5EA 100%)',
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif',
          }}
        >
          <Routes>
            {/* Public Routes */}
            <Route 
              path="/login" 
              element={
                isAuthenticated ? <Navigate to="/chat" replace /> : <LoginPage />
              } 
            />
            
            {/* Protected Routes */}
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <ChatPage />
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminPage />
                </AdminRoute>
              }
            />
            
            {/* Default redirect */}
            <Route 
              path="/" 
              element={<Navigate to={isAuthenticated ? "/chat" : "/login"} replace />} 
            />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
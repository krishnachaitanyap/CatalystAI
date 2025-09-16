import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Container,
  Fade,
  Zoom,
} from '@mui/material';
import { 
  Login as LoginIcon, 
  PersonAdd as PersonAddIcon,
  Sparkles as SparklesIcon,
} from '@mui/icons-material';

import { useAuthStore } from '../hooks/useAuthStore';

const LoginPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login({
          username: formData.username,
          password: formData.password,
        });
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          return;
        }
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        });
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none',
        },
      }}
    >
      <Container maxWidth="sm">
        <Fade in timeout={800}>
          <Paper
            elevation={0}
            sx={{
              p: 6,
              borderRadius: 4,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              boxShadow: '0px 20px 40px rgba(0, 0, 0, 0.1)',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                pointerEvents: 'none',
              },
            }}
          >
            <Box sx={{ textAlign: 'center', mb: 5, position: 'relative', zIndex: 1 }}>
              <Zoom in timeout={1000}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: 4,
                    background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    boxShadow: '0px 12px 24px rgba(0, 122, 255, 0.3)',
                  }}
                >
                  <SparklesIcon sx={{ fontSize: 40, color: 'white' }} />
                </Box>
              </Zoom>
              
              <Typography 
                variant="h3" 
                sx={{ 
                  fontWeight: 700, 
                  mb: 1, 
                  background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                ProdAssist
              </Typography>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: 'text.secondary',
                  fontWeight: 400,
                }}
              >
                {isLogin ? 'Welcome back' : 'Create your account'}
              </Typography>
            </Box>

            {error && (
              <Fade in timeout={300}>
                <Box
                  sx={{
                    p: 2,
                    mb: 3,
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 59, 48, 0.1)',
                    border: '1px solid rgba(255, 59, 48, 0.2)',
                    color: 'error.main',
                    textAlign: 'center',
                    fontWeight: 500,
                  }}
                >
                  {error}
                </Box>
              </Fade>
            )}

            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                sx={{ mb: 3 }}
                InputProps={{
                  sx: {
                    borderRadius: 2,
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

              {!isLogin && (
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  sx={{ mb: 3 }}
                  InputProps={{
                    sx: {
                      borderRadius: 2,
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
              )}

              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                sx={{ mb: 3 }}
                InputProps={{
                  sx: {
                    borderRadius: 2,
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

              {!isLogin && (
                <TextField
                  fullWidth
                  label="Confirm Password"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  sx={{ mb: 4 }}
                  InputProps={{
                    sx: {
                      borderRadius: 2,
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
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : (isLogin ? <LoginIcon /> : <PersonAddIcon />)}
                sx={{
                  mb: 3,
                  py: 2,
                  borderRadius: 2,
                  fontSize: '1.125rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #007AFF 0%, #5856D6 100%)',
                  boxShadow: '0px 8px 24px rgba(0, 122, 255, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #0056CC 0%, #3D3C9E 100%)',
                    boxShadow: '0px 12px 32px rgba(0, 122, 255, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  '&:active': {
                    transform: 'translateY(0px)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
              </Button>

              <Button
                fullWidth
                variant="text"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setFormData({
                    username: '',
                    email: '',
                    password: '',
                    confirmPassword: '',
                  });
                }}
                sx={{
                  fontSize: '1rem',
                  fontWeight: 500,
                  color: 'text.secondary',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 122, 255, 0.04)',
                    color: 'primary.main',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                {isLogin
                  ? "Don't have an account? Sign up"
                  : 'Already have an account? Sign in'}
              </Button>
            </form>
          </Paper>
        </Fade>
      </Container>
    </Box>
  );
};

export default LoginPage;
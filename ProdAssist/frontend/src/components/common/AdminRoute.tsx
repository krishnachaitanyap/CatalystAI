import React from 'react';
import { Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';

import { useAuthStore } from '../../hooks/useAuthStore';

interface AdminRouteProps {
  children: React.ReactNode;
}

const AdminRoute: React.FC<AdminRouteProps> = ({ children }) => {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // For now, allow all authenticated users to access admin
  // In production, you might want to check for admin role
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default AdminRoute;

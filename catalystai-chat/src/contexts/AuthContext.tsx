import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { dataCollectorAPI, User, Application, APISpec } from '../services/dataCollectorAPI';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

interface AppContextType {
  applications: Application[];
  selectedApplication: Application | null;
  apiSpecs: APISpec[];
  isLoading: boolean;
  error: string | null;
  loadApplications: () => Promise<void>;
  selectApplication: (application: Application) => void;
  loadAPISpecs: (appId: number) => Promise<void>;
  createApplication: (app: { name: string; description?: string; sealid: string }) => Promise<void>;
  refreshData: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const login = (token: string) => {
    dataCollectorAPI.setAuthToken(token);
    localStorage.setItem('authToken', token);
    refreshUser();
  };

  const logout = () => {
    dataCollectorAPI.setAuthToken('');
    localStorage.removeItem('authToken');
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await dataCollectorAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to refresh user:', error);
      logout();
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('authToken');
      if (savedToken) {
        dataCollectorAPI.setAuthToken(savedToken);
        try {
          await refreshUser();
        } catch (error) {
          console.error('Failed to authenticate with saved token:', error);
          logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
  const [apiSpecs, setApiSpecs] = useState<APISpec[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadApplications = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await dataCollectorAPI.listApplications();
      setApplications(response.applications);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load applications');
      console.error('Failed to load applications:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectApplication = (application: Application) => {
    setSelectedApplication(application);
    loadAPISpecs(application.id);
  };

  const loadAPISpecs = async (appId: number) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await dataCollectorAPI.listAPISpecs(appId);
      setApiSpecs(response.api_specs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load API specs');
      console.error('Failed to load API specs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createApplication = async (appData: { name: string; description?: string; sealid: string }) => {
    try {
      setIsLoading(true);
      setError(null);
      const newApp = await dataCollectorAPI.createApplication(appData);
      setApplications(prev => [...prev, newApp]);
      return newApp;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create application');
      console.error('Failed to create application:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    await loadApplications();
    if (selectedApplication) {
      await loadAPISpecs(selectedApplication.id);
    }
  };

  const value: AppContextType = {
    applications,
    selectedApplication,
    apiSpecs,
    isLoading,
    error,
    loadApplications,
    selectApplication,
    loadAPISpecs,
    createApplication,
    refreshData,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

// Combined provider for easier use
export const CombinedProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <AuthProvider>
      <AppProvider>
        {children}
      </AppProvider>
    </AuthProvider>
  );
};

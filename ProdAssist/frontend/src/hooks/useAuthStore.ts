import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import apiService from '../services/api';
import { User, LoginForm, RegisterForm, AuthState } from '../types';
import toast from 'react-hot-toast';

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (credentials: LoginForm) => {
        set({ isLoading: true });
        try {
          const response = await apiService.login(credentials);
          
          // Store token
          localStorage.setItem('access_token', response.access_token);
          
          // Get user info
          const user = await apiService.getCurrentUser();
          
          set({
            user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          toast.success(`Welcome back, ${user.username}!`);
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData: RegisterForm) => {
        set({ isLoading: true });
        try {
          const user = await apiService.register(userData);
          
          set({
            user,
            isAuthenticated: false,
            isLoading: false,
          });
          
          toast.success('Account created successfully! Please log in.');
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
        
        toast.success('Logged out successfully');
      },

      updateUser: async (userData: Partial<User>) => {
        set({ isLoading: true });
        try {
          const updatedUser = await apiService.updateUser(userData);
          
          set({
            user: updatedUser,
            isLoading: false,
          });
          
          toast.success('Profile updated successfully');
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

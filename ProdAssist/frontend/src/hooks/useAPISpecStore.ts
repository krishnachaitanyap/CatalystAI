import { create } from 'zustand';
import apiService from '../services/api';
import { APISpec, APISpecForm, APISpecState } from '../types';
import toast from 'react-hot-toast';

export const useAPISpecStore = create<APISpecState>((set, get) => ({
  specs: [],
  currentSpec: null,
  isLoading: false,
  error: null,

  createSpec: async (data: APISpecForm) => {
    set({ isLoading: true });
    try {
      const spec = await apiService.createAPISpec(data);
      
      set((state) => ({
        specs: [spec, ...state.specs],
        isLoading: false,
      }));
      
      toast.success(`API specification "${spec.name}" created successfully`);
      return spec;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  loadSpecs: async () => {
    set({ isLoading: true });
    try {
      const specs = await apiService.getAPISpecs();
      
      set({
        specs,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  loadSpec: async (specId: number) => {
    set({ isLoading: true });
    try {
      const spec = await apiService.getAPISpec(specId);
      
      set({
        currentSpec: spec,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  updateSpec: async (specId: number, data: Partial<APISpecForm>) => {
    set({ isLoading: true });
    try {
      const updatedSpec = await apiService.updateAPISpec(specId, data);
      
      set((state) => ({
        specs: state.specs.map((spec) =>
          spec.id === specId ? updatedSpec : spec
        ),
        currentSpec: state.currentSpec?.id === specId ? updatedSpec : state.currentSpec,
        isLoading: false,
      }));
      
      toast.success(`API specification "${updatedSpec.name}" updated successfully`);
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  deleteSpec: async (specId: number) => {
    set({ isLoading: true });
    try {
      await apiService.deleteAPISpec(specId);
      
      set((state) => ({
        specs: state.specs.filter((spec) => spec.id !== specId),
        currentSpec: state.currentSpec?.id === specId ? null : state.currentSpec,
        isLoading: false,
      }));
      
      toast.success('API specification deleted successfully');
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  uploadFile: async (file: File, sealId: string, application: string) => {
    set({ isLoading: true });
    try {
      const response = await apiService.uploadFile(file, sealId, application);
      
      set({ isLoading: false });
      toast.success(`File "${response.filename}" uploaded successfully`);
      
      return response;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));

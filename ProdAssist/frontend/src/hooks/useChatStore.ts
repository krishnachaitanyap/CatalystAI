import { create } from 'zustand';
import apiService from '../services/api';
import { ChatSession, ChatMessage, ChatSessionForm, ChatState } from '../types';
import toast from 'react-hot-toast';

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,

  createSession: async (data: ChatSessionForm) => {
    set({ isLoading: true });
    try {
      const session = await apiService.createChatSession(data);
      
      set((state) => ({
        sessions: [session, ...state.sessions],
        currentSession: session,
        messages: [],
        isLoading: false,
      }));
      
      toast.success('New chat session created');
      return session;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  loadSession: async (sessionId: number) => {
    set({ isLoading: true });
    try {
      const history = await apiService.getChatHistory(sessionId);
      
      set({
        currentSession: history.session,
        messages: history.messages,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  sendMessage: async (sessionId: number, message: string, includeChainOfThought: boolean = true) => {
    set({ isLoading: true });
    try {
      const response = await apiService.sendMessage(
        sessionId,
        message,
        includeChainOfThought
      );
      
      set((state) => ({
        messages: [...state.messages, response],
        isLoading: false,
      }));
      
      // Update session in sessions list
      set((state) => ({
        sessions: state.sessions.map((session) =>
          session.id === sessionId
            ? { ...session, updated_at: new Date().toISOString() }
            : session
        ),
      }));
      
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  loadSessions: async () => {
    set({ isLoading: true });
    try {
      const sessions = await apiService.getChatSessions();
      
      set({
        sessions,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  loadMessages: async (sessionId: number) => {
    set({ isLoading: true });
    try {
      const messages = await apiService.getChatMessages(sessionId);
      set({ messages, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  deleteSession: async (sessionId: number) => {
    set({ isLoading: true });
    try {
      // Note: You'll need to add this method to your API service
      // await apiService.deleteChatSession(sessionId);
      
      set((state) => ({
        sessions: state.sessions.filter(s => s.id !== sessionId),
        currentSession: state.currentSession?.id === sessionId ? null : state.currentSession,
        messages: state.currentSession?.id === sessionId ? [] : state.messages,
        isLoading: false,
      }));
      
      toast.success('Chat session deleted');
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));

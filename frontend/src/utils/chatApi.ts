const API_BASE_URL = 'https://physical-ai-robotics-textbook-production.up.railway.app/api/v1';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Array<{ title: string; url: string }>;
  code_examples?: Array<{ code: string; language: string }>;
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
  conversation_id?: string;
  lesson_id?: string;
}

export interface ChatResponse {
  response: string;
  sources: Array<{ title: string; url: string }>;
  related_concepts?: string[];
  code_examples?: Array<{ code: string; language: string }>;
  suggestions?: string[];
  rag_used: boolean;
  ai_used: boolean;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  metadata: Record<string, any>;
}

export class ChatAPI {
  private static instance: ChatAPI;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = API_BASE_URL;
  }

  public static getInstance(): ChatAPI {
    if (!ChatAPI.instance) {
      ChatAPI.instance = new ChatAPI();
    }
    return ChatAPI.instance;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Handle expired token specifically
        if (response.status === 401) {
          // Clear expired token
          if (typeof window !== 'undefined') {
            localStorage.removeItem('authToken');
            localStorage.removeItem('authUser');
          }
          throw new Error('Your session has expired. Please sign in again to continue chatting.');
        }

        throw new Error(
          errorData.detail || `HTTP error! status: ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async getConversationHistory(
    conversationId: string,
    limit: number = 50
  ): Promise<ChatMessage[]> {
    try {
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {};

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${this.baseUrl}/chat/history/${conversationId}?limit=${limit}`,
        { headers }
      );

      if (!response.ok) {
        if (response.status === 404) {
          return [];
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      throw error;
    }
  }

  async listConversations(limit: number = 20): Promise<Conversation[]> {
    try {
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {};

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${this.baseUrl}/chat/conversations?limit=${limit}`,
        { headers }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing conversations:', error);
      throw error;
    }
  }

  async deleteConversation(conversationId: string): Promise<void> {
    try {
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {};

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${this.baseUrl}/chat/conversations/${conversationId}`,
        {
          method: 'DELETE',
          headers,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  async submitFeedback(
    conversationId: string,
    messageId: string,
    feedback: {
      rating: number;
      comment?: string;
      category?: string;
    }
  ): Promise<void> {
    try {
      const token = localStorage.getItem('authToken');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${this.baseUrl}/chat/feedback`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          conversation_id: conversationId,
          message_id: messageId,
          ...feedback,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }

  generateConversationId(): string {
    return 'conv-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  }
}

export const chatAPI = ChatAPI.getInstance();
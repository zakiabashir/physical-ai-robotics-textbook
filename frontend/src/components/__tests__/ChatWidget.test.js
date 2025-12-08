import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import ChatWidget from '../ChatWidget';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock window.location
delete window.location;
window.location = { pathname: '/docs/chapter-1/lesson-1' };

describe('ChatWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders chat toggle button when closed', () => {
    render(<ChatWidget />);
    const toggleButton = screen.getByText('Ask Book');
    expect(toggleButton).toBeInTheDocument();
  });

  test('opens chat widget when toggle is clicked', async () => {
    render(<ChatWidget />);
    const toggleButton = screen.getByText('Ask Book');

    fireEvent.click(toggleButton);

    await waitFor(() => {
      expect(screen.getByText(/AI Assistant/)).toBeInTheDocument();
      expect(screen.getByText(/Hello! I'm your Physical AI textbook assistant/)).toBeInTheDocument();
    });
  });

  test('sends message when send button is clicked', async () => {
    const mockResponse = {
      data: {
        message: 'Physical AI is the integration of AI with physical systems.',
        sources: [],
        related_concepts: ['embodiment'],
        code_examples: [],
        suggestions: ['Tell me more about embodiment'],
        can_explain_code: false,
        related_content: []
      }
    };

    mockedAxios.post.mockResolvedValue(mockResponse);

    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Type and send message
    const input = screen.getByPlaceholderText(/Ask me anything/);
    const sendButton = screen.getByText('➤');

    fireEvent.change(input, { target: { value: 'What is Physical AI?' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/chat/',
        expect.objectContaining({
          message: 'What is Physical AI?',
          context: expect.objectContaining({
            current_page: '/docs/chapter-1/lesson-1'
          })
        })
      );
    });

    await waitFor(() => {
      expect(screen.getByText('Physical AI is the integration of AI with physical systems.')).toBeInTheDocument();
    });
  });

  test('sends message when Enter key is pressed', async () => {
    const mockResponse = {
      data: {
        message: 'Test response',
        sources: [],
        related_concepts: [],
        code_examples: [],
        suggestions: [],
        can_explain_code: false,
        related_content: []
      }
    };

    mockedAxios.post.mockResolvedValue(mockResponse);

    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Type and press Enter
    const input = screen.getByPlaceholderText(/Ask me anything/);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 13, charCode: 13 });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled();
    });
  });

  test('does not send empty message', async () => {
    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Try to send empty message
    const sendButton = screen.getByText('➤');
    fireEvent.click(sendButton);

    expect(mockedAxios.post).not.toHaveBeenCalled();
  });

  test('displays suggestions from response', async () => {
    const mockResponse = {
      data: {
        message: 'Test response',
        sources: [],
        related_concepts: [],
        code_examples: [],
        suggestions: ['Learn about ROS 2', 'Explore Gazebo'],
        can_explain_code: false,
        related_content: []
      }
    };

    mockedAxios.post.mockResolvedValue(mockResponse);

    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Send a message
    const input = screen.getByPlaceholderText(/Ask me anything/);
    fireEvent.change(input, { target: { value: 'Tell me more' } });
    fireEvent.click(screen.getByText('➤'));

    await waitFor(() => {
      expect(screen.getByText('Learn about ROS 2')).toBeInTheDocument();
      expect(screen.getByText('Explore Gazebo')).toBeInTheDocument();
    });
  });

  test('handles suggestion clicks', async () => {
    const mockResponse = {
      data: {
        message: 'ROS 2 is a robotics middleware...',
        sources: [],
        related_concepts: [],
        code_examples: [],
        suggestions: [],
        can_explain_code: false,
        related_content: []
      }
    };

    mockedAxios.post.mockResolvedValue(mockResponse);

    render(<ChatWidget />);

    // Open chat and get welcome message with suggestions
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByText('Explain ROS 2 fundamentals')).toBeInTheDocument();
    });

    // Click on suggestion
    fireEvent.click(screen.getByText('Explain ROS 2 fundamentals'));

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/chat/',
        expect.objectContaining({
          message: 'Explain ROS 2 fundamentals'
        })
      );
    });
  });

  test('handles API errors gracefully', async () => {
    mockedAxios.post.mockRejectedValue(new Error('Network error'));

    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Send a message
    const input = screen.getByPlaceholderText(/Ask me anything/);
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByText('➤'));

    await waitFor(() => {
      expect(screen.getByText(/I'm having trouble connecting/)).toBeInTheDocument();
    });
  });

  test('can minimize and close chat', async () => {
    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByText(/AI Assistant/)).toBeInTheDocument();
    });

    // Minimize
    const minimizeButton = screen.getByText('▼');
    fireEvent.click(minimizeButton);

    // Chat should still be open but minimized
    expect(screen.getByText(/AI Assistant/)).toBeInTheDocument();

    // Close
    const closeButton = screen.getByText('✕');
    fireEvent.click(closeButton);

    // Chat should be closed
    await waitFor(() => {
      expect(screen.queryByText(/AI Assistant/)).not.toBeInTheDocument();
    });
  });

  test('displays typing indicator while loading', async () => {
    mockedAxios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<ChatWidget />);

    // Open chat
    fireEvent.click(screen.getByText('Ask Book'));

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything/)).toBeInTheDocument();
    });

    // Send a message
    const input = screen.getByPlaceholderText(/Ask me anything/);
    fireEvent.change(input, { target: { value: 'Test' } });
    fireEvent.click(screen.getByText('➤'));

    // Should show typing indicator
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });
});
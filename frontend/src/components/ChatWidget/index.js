import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../../utils/chatApi';
import FeedbackComponent from './FeedbackComponent';
import { useAuth } from '../../context/AuthContext';
import './styles.css';

const ChatWidget = ({ isOpen: externalIsOpen, onToggle }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user, token } = useAuth();

  // Use external state if provided
  const isWidgetOpen = externalIsOpen !== undefined ? externalIsOpen : isOpen;
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isWidgetOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isWidgetOpen, isMinimized]);

  // Initialize welcome message when opened first time
  useEffect(() => {
    if (isWidgetOpen && messages.length === 0) {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: "Hello! I'm your Physical AI & Humanoid Robotics textbook assistant. What would you like to learn about today?",
        timestamp: new Date(),
      }]);
    }
  }, [isWidgetOpen]);

  const toggleChat = () => {
    if (externalIsOpen !== undefined) {
      // Use external toggle
      onToggle();
    } else {
      // Use internal toggle
      setIsOpen(!isOpen);
    }
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleClose = () => {
    if (externalIsOpen !== undefined) {
      onToggle();
    } else {
      setIsOpen(false);
    }
  };

  const sendMessage = async (messageText = inputValue) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setSuggestions([]);

    try {
      // Get current page context
      const currentPath = window.location.pathname;
      const context = {
        current_page: currentPath,
        lesson_id: currentPath.match(/lesson-(\d+)/)?.[1],
        chapter_id: currentPath.match(/chapter-(\d+)/)?.[1]
      };

      const response = await chatAPI.sendMessage({
        message: messageText,
        context: context
      });

      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        sources: response.sources || [],
        codeExamples: response.code_examples || [],
        suggestions: response.suggestions || [],
        relatedConcepts: response.related_concepts || []
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSuggestions(response.suggestions || []);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const formatMessage = (message) => {
    // Basic markdown to HTML conversion
    let formatted = message.content;

    // Code blocks
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g,
      '<pre><code class="language-$1">$2</code></pre>');

    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic text
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
  };

  const formatSources = (sources) => {
    if (!sources || sources.length === 0) return null;

    return (
      <div className="chat-sources">
        <h4>📚 Sources:</h4>
        <ul>
          {sources.map((source, index) => (
            <li key={index}>
              <strong>{source.title || source.source}</strong>
              {source.url && (
                <a href={source.url} target="_blank" rel="noopener noreferrer" className="source-link">
                  🔗
                </a>
              )}
              <div className="source-score">Relevance: {Math.round(source.score * 100)}%</div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <>
      {/* Only show toggle button if not controlled externally */}
      {externalIsOpen === undefined && (
        <button
          id="chat-toggle"
          onClick={toggleChat}
          style={{ display: isOpen ? 'none' : 'block' }}
        >
          Ask Book
        </button>
      )}

      <div className={`chat-widget ${isWidgetOpen ? 'open' : ''} ${isMinimized ? 'minimized' : ''}`}>
        <div className="chat-header" onClick={handleMinimize}>
          <h3>
            <span role="img" aria-label="robot">🤖</span> AI Assistant
          </h3>
          <div className="chat-controls" onClick={(e) => e.stopPropagation()}>
            <button className="chat-control-btn" onClick={handleMinimize}>
              {isMinimized ? '▲' : '▼'}
            </button>
            <button className="chat-control-btn" onClick={handleClose}>
              ✕
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="chat-messages">
              {messages.map((message) => (
                <div key={message.id} className={`chat-message ${message.role}`}>
                  <div className="chat-avatar">
                    {message.role === 'user' ? (
                      <span role="img" aria-label="user">👤</span>
                    ) : (
                      <span role="img" aria-label="robot">🤖</span>
                    )}
                  </div>
                  <div className="chat-bubble">
                    <div
                      dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
                    />
                    {formatSources(message.sources)}
                    {message.relatedConcepts && message.relatedConcepts.length > 0 && (
                      <div className="related-concepts">
                        <h4>🔗 Related Concepts:</h4>
                        <div className="concept-tags">
                          {message.relatedConcepts.map((concept, index) => (
                            <span key={index} className="concept-tag">
                              {concept}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="chat-suggestions">
                        {message.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            className="suggestion-chip"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                    {message.role === 'assistant' && !message.feedbackGiven && (
                      <FeedbackComponent
                        messageId={message.id}
                        onFeedbackSubmit={(feedback) => {
                          // Mark message as having feedback
                          setMessages(prev => prev.map(msg =>
                            msg.id === message.id
                              ? { ...msg, feedbackGiven: true, feedback }
                              : msg
                          ));
                        }}
                      />
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="chat-message assistant">
                  <div className="chat-avatar">
                    <span role="img" aria-label="robot">🤖</span>
                  </div>
                  <div className="chat-bubble">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {!isLoading && suggestions.length > 0 && (
              <div className="chat-suggestions" style={{ padding: '0 20px' }}>
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}

            <div className="chat-input">
              <textarea
                ref={inputRef}
                className="chat-input-field"
                placeholder="Ask me anything about Physical AI..."
                value={inputValue}
                onChange={(e) => {
                  setInputValue(e.target.value);
                  // Auto-resize textarea
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px';
                }}
                onKeyDown={handleKeyPress}
                disabled={isLoading}
                rows={1}
              />
              <button
                className="chat-send-btn"
                onClick={() => sendMessage()}
                disabled={!inputValue.trim() || isLoading}
              >
                <span>➤</span>
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
};

export default ChatWidget;
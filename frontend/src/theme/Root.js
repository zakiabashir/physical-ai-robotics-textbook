import React, { useState, useEffect } from 'react';
import ChatWidget from '@site/src/components/ChatWidget';
import { AuthProvider, useAuth } from '@site/src/context/AuthContext';
import AuthModal from '@site/src/components/Auth/AuthModal';

function RootContent({ children }) {
  const { isAuthenticated, user } = useAuth();
  const [showChat, setShowChat] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const toggleChat = () => {
    if (!isAuthenticated) {
      setAuthMode('login');
      setShowAuthModal(true);
      return;
    }
    console.log('Chat toggle clicked, current state:', showChat);
    setShowChat(!showChat);
  };

  const handleAuthSuccess = () => {
    // Open chat after successful authentication
    setShowChat(true);
  };

  useEffect(() => {
    console.log('Chat state changed:', showChat);
  }, [showChat]);

  // Add CSS animation
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      .chat-wrapper {
        animation: slideIn 0.3s ease-out;
      }
    `;
    document.head.appendChild(style);

    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <>
      {children}

      {/* Chat Icon Button */}
      <button
        onClick={toggleChat}
        style={{
          position: 'fixed',
          right: '20px',
          bottom: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: showChat ? '#667eea' : '#2563eb',
          border: 'none',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)';
        }}
        title={isAuthenticated ? `Ask Book - ${user.username}` : "Ask Book - Sign in to use"}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          style={{ color: 'white' }}
        >
          <path
            d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
          <path
            d="M8 10h.01M12 10h.01M16 10h.01"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </button>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        initialMode={authMode}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Chat Widget - only show when icon is clicked */}
      {showChat && (
        <div
          className="chat-wrapper"
          style={{
            position: 'fixed',
            right: '90px',
            bottom: '20px',
            zIndex: 9998
          }}
        >
          <ChatWidget
            isOpen={showChat}
            onToggle={toggleChat}
          />
        </div>
      )}
    </>
  );
}

export default function Root({ children }) {
  return (
    <AuthProvider>
      <RootContent>{children}</RootContent>
    </AuthProvider>
  );
}
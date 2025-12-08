import React from 'react';
import ChatAssistant from '@site/src/components/ChatAssistant';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatAssistant />
    </>
  );
}
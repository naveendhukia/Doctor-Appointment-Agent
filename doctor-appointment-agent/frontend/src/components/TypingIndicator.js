import React from 'react';
import './TypingIndicator.css';

const TypingIndicator = () => {
  return (
    <div className="message-wrapper assistant">
      <div className="avatar assistant-avatar">🤖</div>
      <div className="typing-bubble">
        <div className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span className="typing-text">Agent is thinking...</span>
      </div>
    </div>
  );
};

export default TypingIndicator;
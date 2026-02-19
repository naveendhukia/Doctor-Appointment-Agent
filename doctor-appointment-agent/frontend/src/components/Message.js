import React from 'react';
import './Message.css';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.isError;

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatContent = (content) => {
    // Convert newlines to line breaks
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="avatar assistant-avatar">🤖</div>
      )}

      {/* Message Bubble */}
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'} ${isError ? 'error-bubble' : ''}`}>
        <div className="message-content">
          {formatContent(message.content)}
        </div>

        {/* Appointment Confirmation Badge */}
        {message.appointment_id && (
          <div className="appointment-badge">
            ✅ Appointment #{message.appointment_id} Confirmed!
          </div>
        )}

        <div className="message-time">
          {formatTime(message.timestamp)}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="avatar user-avatar">👤</div>
      )}
    </div>
  );
};

export default Message;
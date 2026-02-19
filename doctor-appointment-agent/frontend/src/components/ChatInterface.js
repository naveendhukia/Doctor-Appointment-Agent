import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import Message from './Message';
import TypingIndicator from './TypingIndicator';
import './ChatInterface.css';

const API_URL = 'http://localhost:8002/api';

const SUGGESTED_PROMPTS = [
  "Check Dr. Ahuja's availability tomorrow morning",
  "Book appointment with Dr. Sharma on Friday",
  "What slots does Dr. Ahuja have this week?",
  "I need to see a cardiologist",
  "How many appointments do I have today?",
  "Generate summary report for yesterday"
];

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      role: 'assistant',
      content: "Hello! 👋 I'm your medical appointment scheduling assistant. I can help you:\n\n• Check doctor availability\n• Book appointments\n• Find the right specialist\n\nHow can I help you today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (messageText) => {
    const text = messageText || input.trim();
    if (!text || isLoading) return;

    // Add user message
    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: text,
        session_id: sessionId
      });

      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        appointment_id: response.data.appointment_id
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please make sure the backend server is running on port 8002.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestedPrompt = (prompt) => {
    sendMessage(prompt);
  };

  const clearChat = async () => {
    try {
      await axios.delete(`${API_URL}/session/${sessionId}`);
    } catch (error) {
      console.error('Error clearing session:', error);
    }

    setMessages([{
      id: uuidv4(),
      role: 'assistant',
      content: "Chat cleared! How can I help you with your appointment today?",
      timestamp: new Date()
    }]);
  };

  return (
    <div className="chat-wrapper">
      {/* Header */}
      <div className="chat-header">
        <div className="header-left">
          <div className="header-icon">🏥</div>
          <div className="header-info">
            <h1>Doctor Appointment Agent</h1>
            <span className="status-badge">
              <span className="status-dot"></span>
              AI Agent Online
            </span>
          </div>
        </div>
        <div className="header-actions">
          <button 
            className="report-btn" 
            onClick={() => sendMessage("Generate a full summary report")}
            title="Get summary report"
        >
            📊 Report
            </button>
        <button className="clear-btn" onClick={clearChat} title="Clear conversation">
          🗑️ Clear Chat
        </button>
      </div>
    </div>

      {/* Doctors Info Bar */}
      <div className="doctors-bar">
        <span className="doctors-label">Available Doctors:</span>
        <span className="doctor-chip cardiology">
          👨‍⚕️ Dr. Ahuja — Cardiology
        </span>
        <span className="doctor-chip pediatrics">
          👩‍⚕️ Dr. Sharma — Pediatrics
        </span>
      </div>

      {/* Messages Area */}
      <div className="messages-area">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts - show only at start */}
      {messages.length <= 1 && !isLoading && (
        <div className="suggested-prompts">
          <p className="prompts-label">Try asking:</p>
          <div className="prompts-grid">
            {SUGGESTED_PROMPTS.map((prompt, index) => (
              <button
                key={index}
                className="prompt-chip"
                onClick={() => handleSuggestedPrompt(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="input-area">
        <form onSubmit={handleSubmit} className="input-form">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (e.g., 'Check Dr. Ahuja's availability tomorrow morning')"
            disabled={isLoading}
            rows={1}
            className="message-input"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="send-btn"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </form>
        <p className="input-hint">Press Enter to send • Shift+Enter for new line</p>
      </div>
    </div>
  );
};

export default ChatInterface;
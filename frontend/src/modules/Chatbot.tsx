import axios from 'axios';
import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatResponse {
  response: string;
  timestamp: string;
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant powered by LangChain and LlamaIndex. How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Get auth token from localStorage - check both formats for compatibility
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    setAuthToken(token);
    
    // Ensure both token formats are available
    if (token) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('token', token);
      loadChatHistory();
    }
  }, []);

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

        const response = await fetch('http://164.92.184.138:8000/chat/history', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.history && data.history.length > 0) {
          const historyMessages: Message[] = data.history.map((item: any, index: number) => ({
            id: `history-${index}`,
            text: item.content,
            sender: item.role === 'user' ? 'user' : 'bot',
            timestamp: new Date()
          }));
          
          setMessages(prev => [prev[0], ...historyMessages]);
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessageToAPI = async (message: string): Promise<string> => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return 'Please log in to use the chatbot.';
      }

      const response = await fetch('http://164.92.184.138:8000/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          return 'Your session has expired. Please log in again.';
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error sending message to API:', error);
      return 'Sorry, I encountered an error while processing your message. Please try again.';
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    if (!authToken) {
      alert('Please log in to use the chatbot.');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputText;
    setInputText('');
    setIsLoading(true);

    try {
      const botResponseText = await sendMessageToAPI(currentInput);
      
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponseText,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      console.log('File selected:', file.name);
    }
    axios.post('http://164.92.184.138:8000/chat/upload', {
      file: file
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await fetch('http://164.92.184.138:8000/chat/clear', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Error clearing chat history:', error);
    }

    setMessages([
      {
        id: '1',
        text: 'Hello! I\'m your AI assistant powered by LangChain and LlamaIndex. How can I help you today?',
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
  };

  const handleBackToTodos = () => {
    navigate('/todos');
  };

  const TypingIndicator = () => (
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
    </div>
  );

  if (!authToken) {
    return (
      <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white shadow-xl rounded-lg overflow-hidden">
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
              🤖
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">AI Assistant</h3>
            <p className="text-gray-600 mb-4">Please log in to start chatting with the AI assistant.</p>
            <button
              onClick={() => window.location.href = '/login'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white shadow-xl rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={handleBackToTodos}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors duration-200 mr-2"
            title="Back to Todos"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-2xl">
            🤖
          </div>
          <div>
            <h3 className="font-semibold text-lg">AI Assistant</h3>
            <span className="text-blue-100 text-sm flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              Powered by LangChain & LlamaIndex
            </span>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors duration-200"
          title="Clear chat"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 shadow-md rounded-bl-none border'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">{message.text}</div>
              <div
                className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-lg bg-white text-gray-800 shadow-md rounded-bl-none border">
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-4">
        <div className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your documents..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={1}
              disabled={isLoading}
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <input type="file" onChange={handleFileUpload} placeholder='Upload a file'/>
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              !inputText.trim() || isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95 shadow-md hover:shadow-lg'
            }`}
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;

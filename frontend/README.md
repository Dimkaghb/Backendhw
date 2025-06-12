# React Todo App with AI Chatbot

A modern React application with todo management and AI-powered chatbot integration.

## Features

### 🔐 Authentication
- User registration and login
- JWT token-based authentication
- Protected routes

### ✅ Todo Management
- Create, read, update, and delete todos
- Mark todos as completed
- Real-time updates

### 🤖 AI Chatbot Integration
- **NEW**: AI-powered chatbot accessible from the todos page
- Powered by LangChain and LlamaIndex
- Document search and question answering
- Chat history persistence
- Seamless navigation between todos and chatbot

## How to Use the Chatbot

1. **Login** to your account
2. Navigate to the **Todos** page
3. Click the **🤖 Chat Assistant** button in the top-right corner
4. Start chatting with the AI assistant
5. Use the **back arrow** to return to your todos

## Navigation Flow

```
Login → Todos ↔ Chatbot
```

- **Todos Page**: Manage your tasks + access chatbot
- **Chatbot Page**: AI assistant + return to todos
- **Authentication**: Required for both features

## Technical Features

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Tailwind CSS for styling
- Axios for API calls
- Protected routes with authentication

### Backend Integration
- FastAPI backend with JWT authentication
- LangChain + LlamaIndex AI agents
- Document search capabilities
- Chat history management
- MongoDB/in-memory storage

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Ensure backend is running**:
   - Backend should be running on `http://localhost:8000`
   - Frontend will be on `http://localhost:3000`

## User Experience

- **Seamless Integration**: Switch between todos and chatbot without losing authentication
- **Persistent Sessions**: Stay logged in across both features
- **Modern UI**: Clean, responsive design with smooth transitions
- **Real-time Chat**: Instant responses from AI assistant

## Authentication Flow

The app maintains authentication state across both todos and chatbot:
- Login stores JWT token in localStorage
- Both `token` and `access_token` formats supported for compatibility
- Protected routes ensure secure access
- Logout clears all tokens and redirects to login

Enjoy managing your todos and chatting with your AI assistant! 🚀

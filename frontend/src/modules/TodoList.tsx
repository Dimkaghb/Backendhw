import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Todo {
  id: number;
  name: string;
  is_completed: boolean;
}

const TodoList = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/auth');
        return;
      }

      await axios.post('http://localhost:8000/logout', null, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Clear the token from localStorage
      localStorage.removeItem('token');
      // Also clear access_token for chatbot compatibility
      localStorage.removeItem('access_token');
      // Redirect to login page
      navigate('/auth');
    } catch (err) {
      console.error('Logout failed:', err);
      // Even if the server request fails, clear the token and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('access_token');
      navigate('/auth');
    }
  };

  const handleChatbotNavigation = () => {
    // Ensure both token formats are available for compatibility
    const token = localStorage.getItem('token');
    if (token) {
      localStorage.setItem('access_token', token);
    }
    navigate('/chatbot');
  };

  const fetchTodos = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/auth');
        return;
      }

      const response = await axios.get('http://localhost:8000/todos', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setTodos(response.data);
    } catch (err: any) {
      if (err.response && err.response.status === 401) {
        // Token is invalid or expired
        localStorage.removeItem('token');
        navigate('/auth');
        return;
      }
      setError('Failed to load todos');
    }
  };

  useEffect(() => {
    fetchTodos();
  }, [navigate]);

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodo.trim()) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/todos',
        {
          name: newTodo,
          is_completed: false
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const addedTodo = response.data;
      setTodos([...todos, addedTodo]);
      setNewTodo('');
    } catch (err) {
      setError('Failed to add todo');
    }
  };

  const toggleTodo = async (todo: Todo) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `http://localhost:8000/todos/${todo.id}`,
        {
          ...todo,
          is_completed: !todo.is_completed
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const updatedTodo = response.data;
      setTodos(todos.map(t => t.id === todo.id ? updatedTodo : t));
    } catch (err) {
      setError('Failed to update todo');
    }
  };

  const deleteTodo = async (id: number) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/todos/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setTodos(todos.filter(todo => todo.id !== id));
    } catch (err) {
      setError('Failed to delete todo');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Todo List</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={handleChatbotNavigation}
            style={{
              padding: '8px 16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}
          >
            🤖 Chat Assistant
          </button>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <form onSubmit={handleAddTodo} style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={newTodo}
          onChange={(e) => setNewTodo(e.target.value)}
          placeholder="Add new todo"
          style={{
            padding: '8px',
            marginRight: '10px',
            width: '70%'
          }}
        />
        <button
          type="submit"
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add Todo
        </button>
      </form>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {todos.map(todo => (
          <li
            key={todo.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '10px',
              marginBottom: '10px',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px'
            }}
          >
            <input
              type="checkbox"
              checked={todo.is_completed}
              onChange={() => toggleTodo(todo)}
              style={{ marginRight: '10px' }}
            />
            <span
              style={{
                flex: 1,
                textDecoration: todo.is_completed ? 'line-through' : 'none'
              }}
            >
              {todo.name}
            </span>
            <button
              onClick={() => deleteTodo(todo.id)}
              style={{
                padding: '4px 8px',
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TodoList; 
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import config from '../../config';

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const endpoint = isLogin ? `${config.apiBaseUrl}/login` : `${config.apiBaseUrl}/signup`;
      const response = await axios.post(endpoint, { username, password }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = response.data;

      if (isLogin) {
        // Store the JWT token in localStorage in both formats for compatibility
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('access_token', data.access_token);
        // Navigate to the todos page after successful login
        navigate('/todos');
      } else {
        alert('Signup successful! Please login.');
        setIsLogin(true);
      }
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred');
      }
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h2>{isLogin ? 'Login' : 'Sign Up'}</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          />
        </div>
        <button 
          type="submit"
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {isLogin ? 'Login' : 'Sign Up'}
        </button>
      </form>
      <p style={{ marginTop: '15px', textAlign: 'center' }}>
        {isLogin ? "Don't have an account? " : "Already have an account? "}
        <button
          onClick={() => setIsLogin(!isLogin)}
          style={{
            background: 'none',
            border: 'none',
            color: '#007bff',
            cursor: 'pointer',
            padding: 0
          }}
        >
          {isLogin ? 'Sign Up' : 'Login'}
        </button>
      </p>
    </div>
  );
};

export default Auth;
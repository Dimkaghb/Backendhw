import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './modules/Auth';
import ProtectedRoute from './modules/ProtectedRoute';
import TodoList from './modules/TodoList'; // You'll need to create this component
import './App.css'

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route
          path="/todos"
          element={
            <ProtectedRoute>
              <TodoList />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/auth" replace />} />
      </Routes>
    </Router>
  );
};

export default App;

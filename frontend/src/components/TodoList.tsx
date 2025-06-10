import React, { useState, useEffect } from 'react';
import axios from 'axios';
import type { Todo } from '../types/todo';
import TodoItem from './Todo';

const API_URL = 'http://localhost:8000';

const TodoList: React.FC = () => {
    const [todos, setTodos] = useState<Todo[]>([]);
    const [newTodo, setNewTodo] = useState('');

    useEffect(() => {
        fetchTodos();
    }, []);

    const fetchTodos = async () => {
        try {
            const response = await axios.get(`${API_URL}/todos`);
            setTodos(response.data);
        } catch (error) {
            console.error('Error fetching todos:', error);
        }
    };

    const createTodo = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTodo.trim()) return;

        try {
            const response = await axios.post(`${API_URL}/todos`, {
                name: newTodo,
                is_completed: false
            });
            setTodos([...todos, response.data]);
            setNewTodo('');
        } catch (error) {
            console.error('Error creating todo:', error);
        }
    };

    const toggleTodo = async (id: number, isCompleted: boolean) => {
        try {
            const todo = todos.find(t => t.id === id);
            if (!todo) return;

            const response = await axios.put(`${API_URL}/todos/${id}`, {
                ...todo,
                is_completed: isCompleted
            });
            setTodos(todos.map(t => t.id === id ? response.data : t));
        } catch (error) {
            console.error('Error updating todo:', error);
        }
    };

    const deleteTodo = async (id: number) => {
        try {
            await axios.delete(`${API_URL}/todos/${id}`);
            setTodos(todos.filter(t => t.id !== id));
        } catch (error) {
            console.error('Error deleting todo:', error);
        }
    };

    return (
        <div className="todo-container">
            <h1>Todo List</h1>
            <form onSubmit={createTodo} className="todo-form">
                <input
                    type="text"
                    value={newTodo}
                    onChange={(e) => setNewTodo(e.target.value)}
                    placeholder="Add a new todo..."
                    className="todo-input"
                />
                <button type="submit" className="add-btn">Add Todo</button>
            </form>
            <div className="todo-list">
                {todos.map(todo => (
                    <TodoItem
                        key={todo.id}
                        todo={todo}
                        onToggle={toggleTodo}
                        onDelete={deleteTodo}
                    />
                ))}
            </div>
        </div>
    );
};

export default TodoList; 
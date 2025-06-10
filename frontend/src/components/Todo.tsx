import React from 'react';
import type { Todo } from '../types/todo';

interface TodoItemProps {
    todo: Todo;
    onToggle: (id: number, isCompleted: boolean) => void;
    onDelete: (id: number) => void;
}

const TodoItem: React.FC<TodoItemProps> = ({ todo, onToggle, onDelete }) => {
    return (
        <div className={`todo-item ${todo.is_completed ? 'completed' : ''}`}>
            <input
                type="checkbox"
                checked={todo.is_completed}
                onChange={() => onToggle(todo.id, !todo.is_completed)}
            />
            <span>{todo.name}</span>
            <button 
                className="delete-btn"
                onClick={() => onDelete(todo.id)}
            >
                Delete
            </button>
        </div>
    );
};

export default TodoItem; 
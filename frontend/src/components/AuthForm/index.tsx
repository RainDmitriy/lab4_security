import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthDispatch } from '../../contexts/AuthContext';

const AuthForm: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const dispatch = useAuthDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const token = data.access_token;
        localStorage.setItem('access_token', token);

        const payload = JSON.parse(atob(token.split('.')[1]));
        dispatch({
          type: 'LOGIN',
          payload: {
            id: payload.user_id,
            login: payload.login,
            role: payload.role,
            is_author_verified: payload.is_author_verified,
          },
        });
        navigate('/');
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Ошибка авторизации');
      }
    } catch (err) {
      setError('Ошибка сети');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto', padding: '1rem', border: '1px solid #ccc' }}>
      <h2>Вход</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Login:</label>
          <input
            type="login"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Пароль:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Войти</button>
      </form>
    </div>
  );
};

export default AuthForm;
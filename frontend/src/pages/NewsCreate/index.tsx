import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthState } from '../../contexts/AuthContext';
import styles from './NewsCreate.module.css';

const CreateNews: React.FC = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [coverUrl, setCoverUrl] = useState('');
  const [error, setError] = useState('');
  const { user } = useAuthState();
  const navigate = useNavigate();

  const canCreate = user && (user.is_author_verified || user.role === 'admin');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canCreate) {
      setError('У вас нет прав для создания новости.');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/news`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          title,
          content: { body: content },
          cover_url: coverUrl || null,
        }),
      });

      if (response.ok) {
        navigate('/');
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Ошибка при создании новости');
      }
    } catch (err) {
      setError('Ошибка сети');
    }
  };

  if (!user) {
    return <p>Требуется авторизация</p>;
  }

  if (!canCreate) {
    return <p>У вас нет прав для создания новости.</p>;
  }

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.formTitle}>Создать новость</h2>
        {error && <p className={styles.error}>{error}</p>}
        <div className={styles.formGroup}>
          <label>Заголовок:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className={styles.formGroup}>
          <label>Контент:</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            style={{ minHeight: '100px' }}
          />
        </div>
        <div className={styles.formGroup}>
          <label>Ссылка на обложку (опционально):</label>
          <input
            type="text"
            value={coverUrl}
            onChange={(e) => setCoverUrl(e.target.value)}
          />
        </div>
        <button type="submit" className={styles.submitButton}>Создать</button>
      </form>
    </div>
  );
};

export default CreateNews;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthState } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import styles from './NewsEdit.module.css';

const EditNews: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [coverUrl, setCoverUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuthState();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await apiClient.get(`/news/${id}`);
        const news = res.data;
        setTitle(news.title);
        if (typeof news.content === 'object' && news.content.body) {
          setContent(news.content.body);
        } else if (typeof news.content === 'string') {
          setContent(news.content);
        } else {
          setContent(JSON.stringify(news.content));
        }
        setCoverUrl(news.cover_url || '');
      } catch (err) {
        console.error('Ошибка при загрузке новости', err);
        setError('Не удалось загрузить новость');
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, [id]);

  const canEdit = user && (user.id === parseInt(id!) || user.role === 'admin');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit) {
      setError('У вас нет прав для редактирования этой новости.');
      return;
    }

    try {
      const response = await apiClient.put(`/news/${id}`, {
        title,
        content: { body: content },
        cover_url: coverUrl || null,
      });

      if (response.status === 200) {
        navigate(`/news/${id}`);
      } else {
        setError('Ошибка при обновлении новости');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сети');
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!canEdit) return <p>У вас нет прав для редактирования этой новости.</p>;

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.formTitle}>Редактировать новость</h2>
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
        <button type="submit" className={styles.submitButton}>Сохранить</button>
      </form>
    </div>
  );
};

export default EditNews;
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';
import type { News, Comment } from '../../types';
import CommentItem from '../../components/CommentItem';
import CommentForm from '../../components/CommentForm';
import { useAuthState } from '../../contexts/AuthContext';
import { useNewsStore } from '../../store/newsStore';
import styles from './NewsDetail.module.css';

const NewsDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [news, setNews] = useState<News | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuthState();
  const { authorsMap, fetchAuthorName } = useNewsStore();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const res = await apiClient.get(`/news/${id}`);
        setNews(res.data);
        const comRes = await apiClient.get(`/comments?news_id=${id}`);
        setComments(comRes.data);
      } catch (err) {
        console.error('Ошибка при загрузке новости', err);
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, [id, navigate]);

  // Подгружаем имя автора новости
  useEffect(() => {
    if (news && !authorsMap[news.author_id]) {
      fetchAuthorName(news.author_id);
    }
  }, [news, authorsMap, fetchAuthorName]);

  const handleDeleteComment = async (commentId: number) => {
    try {
      await apiClient.delete(`/comments/${commentId}`);
      setComments(comments.filter(c => c.id !== commentId));
    } catch (err) {
      console.error('Ошибка при удалении комментария', err);
    }
  };

  const handleUpdateComment = (commentId: number, newText: string) => {
    setComments(comments.map(c => c.id === commentId ? { ...c, text: newText } : c));
  };

  const handleAddComment = () => {
    if (id) {
      apiClient.get(`/comments?news_id=${id}`).then(res => setComments(res.data));
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (!news) return <p>Новость не найдена</p>;

  const canEdit = user && (news.author_id === user.id || user.role === 'admin');
  const authorName = authorsMap[news.author_id] || 'Загрузка...';

  // Распаковываем content
  const renderContent = (content: any) => {
    if (typeof content === 'string') {
      return content;
    }
    if (typeof content === 'object' && content.body) {
      return content.body;
    }
    return JSON.stringify(content);
  };

  return (
    <div className={styles.newsDetail}>
      <h1 className={styles.newsTitle}>{news.title}</h1>
      <div className={styles.newsMeta}>
        <span>Автор: {authorName}</span>
        <span>Дата: {new Date(news.published_at).toLocaleString()}</span>
      </div>
      {news.cover_url && (
      <div style={{ marginBottom: '1rem' }}>
        <img
          src={news.cover_url}
          alt="Обложка"
          style={{
            width: '100%',
            height: 'auto',
            borderRadius: '8px',
            objectFit: 'cover',
            border: '1px solid var(--border-color)'
          }}
          onError={(e) => {
            e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y5ZjlmOSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxNiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgZmlsbD0iIzAwMCI+Tm8gaW1hZ2U8L3RleHQ+PC9zdmc+';
            e.currentTarget.style.backgroundColor = '#f0f0f0';
            e.currentTarget.style.padding = '1rem';
            e.currentTarget.style.textAlign = 'center';
            e.currentTarget.alt = 'Изображение не доступно';
          }}
        />
      </div>
    )}
      <div className={styles.newsContent} dangerouslySetInnerHTML={{ __html: renderContent(news.content) }} />
      {canEdit && (
        <button onClick={() => navigate(`/edit-news/${id}`)} className={styles.editButton}>
          Редактировать
        </button>
      )}

      <div className={styles.divider}></div>

      <div className={styles.commentsSection}>
        <h2 className={styles.commentsTitle}>Комментарии</h2>
        {user && <CommentForm newsId={news.id} onAdd={handleAddComment} />}
        <div className={styles.commentList}>
          {comments.map((c) => (
            <CommentItem
              key={c.id}
              comment={c}
              userId={user?.id || 0}
              role={user?.role || 'user'}
              onDelete={handleDeleteComment}
              onUpdate={handleUpdateComment}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default NewsDetail;
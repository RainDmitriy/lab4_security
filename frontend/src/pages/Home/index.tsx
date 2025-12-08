import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NewsCard from '../../components/NewsCard';
import { useAuthState } from '../../contexts/AuthContext';
import { useNewsStore } from '../../store/newsStore';
import styles from './Home.module.css';

const NewsListSkeleton: React.FC = () => (
  <div className={styles.newsListSkeleton}>
    {Array.from({ length: 5 }).map((_, i) => (
      <div key={i} className={styles.skeletonCard}>
        <div className={styles.skeletonTitle}></div>
        <div className={styles.skeletonText}></div>
        <div className={styles.skeletonText}></div>
        <div className={styles.skeletonText}></div>
      </div>
    ))}
  </div>
);

const Home: React.FC = () => {
  const { user } = useAuthState();
  const navigate = useNavigate();

  const {
    filteredNews,
    loading,
    error,
    setSearchQuery,
    setAuthorFilter,
    setDateFrom,
    setDateTo,
    fetchNews
  } = useNewsStore();

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  if (error) return <p style={{ color: 'red' }}>Ошибка: {error}</p>;

  return (
    <div className={styles.container}>
      <div style={{ padding: '1rem' }}>
        <div className={styles.formGroup}>
          <input
            type="text"
            placeholder="Поиск по заголовкам..."
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem' }}
          />
        </div>
        <div className={styles.formGroup}>
          <input
            type="text"
            placeholder="Фильтр по автору..."
            onChange={(e) => setAuthorFilter(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem' }}
          />
        </div>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <input
              type="date"
              onChange={(e) => setDateFrom(e.target.value)}
              placeholder="От"
              style={{ padding: '0.5rem' }}
            />
          </div>
          <div className={styles.formGroup} style={{ flex: 1 }}>
            <input
              type="date"
              onChange={(e) => setDateTo(e.target.value)}
              placeholder="До"
              style={{ padding: '0.5rem' }}
            />
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', margin: '1rem' }}>
        {user && (user.is_author_verified || user.role === 'admin') && (
          <button onClick={() => navigate('/create-news')} className={styles.btnGradient}>
            Создать новость
          </button>
        )}
      </div>

      {loading ? (
        <NewsListSkeleton />
      ) : filteredNews.length === 0 ? (
        <p style={{ textAlign: 'center', padding: '2rem', color: '#577FCD' }}>Новостей не найдено.</p>
      ) : (
        filteredNews.map((n) => (
          <NewsCard key={n.id} news={n} />
        ))
      )}
    </div>
  );
};

export default Home;

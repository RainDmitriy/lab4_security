import type { News } from '../../types';
import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { useNewsStore } from '../../store/newsStore';
import styles from './NewsCard.module.css';

const NewsCardSkeleton: React.FC = () => (
  <div className={styles.skeletonCard}>
    <div className={styles.skeletonTitle}></div>
    <div className={styles.skeletonText}></div>
    <div className={styles.skeletonText}></div>
    <div className={styles.skeletonText}></div>
  </div>
);

const NewsCard: React.FC<{ news: News }> = ({ news }) => {
  const { authorsMap, fetchAuthorName } = useNewsStore();

  const isAuthorLoaded = authorsMap[news.author_id] !== undefined;
  const authorName = authorsMap[news.author_id] || 'Загрузка...';

  useEffect(() => {
    if (!isAuthorLoaded) {
      fetchAuthorName(news.author_id);
    }
  }, [news.author_id, isAuthorLoaded, fetchAuthorName]);

  const renderContent = (content: any) => {
    if (typeof content === 'string') return content;
    if (typeof content === 'object' && content.body) return content.body;
    return JSON.stringify(content);
  };

  if (!isAuthorLoaded) {
    return <NewsCardSkeleton />;
  }

  return (
    <div className={styles.card}>
      {news.cover_url && (
        <img
          src={news.cover_url}
          alt="Обложка"
          style={{
            width: '100%',
            height: 'auto',
            borderRadius: '8px',
            marginBottom: '1rem'
          }}
        />
      )}
      <h3 style={{ marginBottom: '0.5rem', color: 'var(--primary-dark)' }}>
        <Link to={`/news/${news.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
          {news.title}
        </Link>
      </h3>
      <p style={{ marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
        Автор: {authorName}
      </p>
      <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
        Дата: {new Date(news.published_at).toLocaleString()}
      </p>
      <div
        dangerouslySetInnerHTML={{ __html: renderContent(news.content) }}
        style={{ color: 'var(--text-primary)' }}
      />
    </div>
  );
};

export default NewsCard;
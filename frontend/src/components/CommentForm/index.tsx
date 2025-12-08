import React, { useState } from 'react';
import apiClient from '../../api/client';

interface Props {
  newsId: number;
  onAdd: () => void;
}

const CommentForm: React.FC<Props> = ({ newsId, onAdd }) => {
  const [text, setText] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Отправляем только text и news_id. author_id подставляется на бэкенде из токена.
      await apiClient.post('/comments', { text, news_id: newsId });
      setText('');
      onAdd();
    } catch (err) {
      console.error('Ошибка при добавлении комментария', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ margin: '1rem 0' }}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Написать комментарий..."
        required
      />
      <button type="submit">Отправить</button>
    </form>
  );
};

export default CommentForm;
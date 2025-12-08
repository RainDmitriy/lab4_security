import React, { useState } from 'react';
import type { Comment } from '../../types';
import { useNewsStore } from '../../store/newsStore';
import apiClient from '../../api/client';
import styles from './CommentItem.module.css';

interface Props {
  comment: Comment;
  userId: number;
  role: string;
  onDelete: (id: number) => void;
  onUpdate: (id: number, text: string) => void; // ✅ Новый проп
}

const CommentItem: React.FC<Props> = ({ comment, userId, role, onDelete, onUpdate }) => {
  const { authorsMap, fetchAuthorName } = useNewsStore();

  const authorName = authorsMap[comment.author_id] || 'Загрузка...';

  if (!authorsMap[comment.author_id]) {
    fetchAuthorName(comment.author_id);
  }

  const canEdit = comment.author_id === userId || role === 'admin';
  const canDelete = comment.author_id === userId || role === 'admin';

  // ✅ Состояния для редактирования
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(comment.text);

  const handleEdit = () => {
    setIsEditing(true);
    setEditText(comment.text);
  };

  const handleSave = async () => {
    try {
      await apiClient.put(`/comments/${comment.id}`, { text: editText });
      onUpdate(comment.id, editText); // ✅ Обновляем в родителе
      setIsEditing(false);
    } catch (err) {
      console.error('Ошибка при сохранении комментария', err);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditText(comment.text);
  };

  return (
    <div className={styles.commentItem}>
      {isEditing ? (
        <>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className={styles.editInput}
          />
          <div className={styles.editButtons}>
            <button onClick={handleSave} className={styles.saveButton}>
              Сохранить
            </button>
            <button onClick={handleCancel} className={styles.cancelButton}>
              Отмена
            </button>
          </div>
        </>
      ) : (
        <>
          <p className={styles.commentText}>{comment.text}</p>
          <div className={styles.commentAuthor}>Автор: {authorName}</div>
          <div className={styles.commentDate}>{new Date(comment.published_at).toLocaleString()}</div>
        </>
      )}
      <div>
        {canEdit && !isEditing && (
          <button onClick={handleEdit} style={{ marginRight: '0.5rem' }}>
            Редактировать
          </button>
        )}
        {canDelete && !isEditing && (
          <button onClick={() => onDelete(comment.id)} className={styles.deleteButton}>
            Удалить
          </button>
        )}
      </div>
    </div>
  );
};

export default CommentItem;
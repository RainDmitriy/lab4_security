import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthState, useAuthDispatch } from '../../contexts/AuthContext';
import styles from './Navbar.module.css';

const Navbar: React.FC = () => {
  const { user } = useAuthState();
  const dispatch = useAuthDispatch();

  const logout = () => {
    localStorage.removeItem('access_token');
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <nav className={styles.navbar}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span className={styles.snowflake}>❄️</span>
        <h2>
          <Link to="/" style={{ textDecoration: 'none', color: 'var(--primary-deepest)' }}>
            News App
          </Link>
        </h2>
      </div>
      <div className={styles.userActions}>
        {user ? (
          <div className={styles.userActions}>
            <span>Привет, {user.login}!</span>
            <button onClick={logout}>Выйти</button>
          </div>
        ) : (
          <div className={styles.userActions}>
            <Link to="/login">Войти</Link>
            <Link to="/register">Регистрация</Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
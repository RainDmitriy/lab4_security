import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Register.module.css';

const Register: React.FC = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const eyeRef = useRef<HTMLDivElement>(null);

  // === Логин ===
  const [loginValid, setLoginValid] = useState(false);

  const validateLogin = (value: string) => {
    const regex = /^[a-zA-Z0-9._-]{3,32}$/;
    setLoginValid(regex.test(value));
  };

  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLogin(value);
    validateLogin(value);
  };

  // === Пароль ===
  const [lengthValid, setLengthValid] = useState(false);
  const [upperValid, setUpperValid] = useState(false);
  const [lowerValid, setLowerValid] = useState(false);
  const [digitValid, setDigitValid] = useState(false);
  const [specialValid, setSpecialValid] = useState(false);

  const validatePassword = (pwd: string) => {
    setLengthValid(pwd.length >= 8);
    setUpperValid(/[A-Z]/.test(pwd));
    setLowerValid(/[a-z]/.test(pwd));
    setDigitValid(/\d/.test(pwd));
    setSpecialValid(/[!@#$%^&*(),.?":{}|<>]/.test(pwd));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const pwd = e.target.value;
    setPassword(pwd);
    validatePassword(pwd);
  };

  // === Анимация глаза ===
  useEffect(() => {
    if (eyeRef.current && password) {
      eyeRef.current.style.transform = 'scale(1.1)';
      setTimeout(() => {
        if (eyeRef.current) eyeRef.current.style.transform = 'scale(1)';
      }, 100);
    }
  }, [password]);

  // === Отправка формы ===
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!loginValid) {
      setError('Логин не соответствует требованиям');
      return;
    }

    if (!lengthValid || !upperValid || !lowerValid || !digitValid || !specialValid) {
      setError('Пароль не соответствует требованиям');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password }),
      });

      if (response.ok) {
        alert('Регистрация успешна! Пожалуйста, войдите в систему.');
        navigate('/login');
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Ошибка регистрации');
      }
    } catch {
      setError('Ошибка сети');
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.formTitle}>Регистрация</h2>
        {error && <p className={styles.error}>{error}</p>}

        {/* ===== ЛОГИН ===== */}
        <div className={styles.formGroup}>
          <label>Логин:</label>
          <input
            type="text"
            value={login}
            onChange={handleLoginChange}
            required
            placeholder="Введите логин"
          />
          <div className={styles.passwordRequirements}>
            <div className={`${styles.requirement} ${loginValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{loginValid ? '✓' : '✗'}</span>
              Логин: 3-32 символа, латиница, цифры, ., _, -
            </div>
          </div>
        </div>

        {/* ===== ПАРОЛЬ ===== */}
        <div className={styles.formGroup}>
          <label>Пароль:</label>
          <div className={styles.passwordInputWrapper}>
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={handlePasswordChange}
            required
            placeholder="Введите пароль"
            className={styles.passwordInput}
          />
          <div
            onClick={() => setShowPassword(!showPassword)}
            className={`${styles.eyeIcon} ${password ? styles.visible : ''}`}
          >
            {showPassword ? '👁️' : '🙈'}
          </div>
        </div>
          <div className={styles.passwordRequirements}>
            <div className={`${styles.requirement} ${lengthValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{lengthValid ? '✓' : '✗'}</span>
              ≥ 8 символов
            </div>
            <div className={`${styles.requirement} ${upperValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{upperValid ? '✓' : '✗'}</span>
              1 заглавная буква
            </div>
            <div className={`${styles.requirement} ${lowerValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{lowerValid ? '✓' : '✗'}</span>
              1 строчная буква
            </div>
            <div className={`${styles.requirement} ${digitValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{digitValid ? '✓' : '✗'}</span>
              1 цифра
            </div>
            <div className={`${styles.requirement} ${specialValid ? styles.valid : ''}`}>
              <span className={styles.requirementIcon}>{specialValid ? '✓' : '✗'}</span>
              1 спецсимвол
            </div>
          </div>
        </div>

        <button type="submit" className={styles.submitButton}>Зарегистрироваться</button>
        <div className={styles.linkContainer}>
          Уже есть аккаунт? <a href="/login">Войти</a>
        </div>
      </form>
    </div>
  );
};

export default Register;

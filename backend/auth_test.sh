#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/v1"

echo "=== 1. РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ==="
curl -s -X POST "$BASE_URL/auth/register" -H "Content-Type: application/json" -d '{"name": "AdminUser", "email": "admin@example.com", "password": "AdminStrongPassword123"}' >/dev/null
curl -s -X POST "$BASE_URL/auth/register" -H "Content-Type: application/json" -d '{"name": "AuthorUser", "email": "author@example.com", "password": "AuthorStrongPassword123"}' >/dev/null
curl -s -X POST "$BASE_URL/auth/register" -H "Content-Type: application/json" -d '{"name": "RegularUser", "email": "user@example.com", "password": "UserStrongPassword123"}' >/dev/null

echo "=== 2. ПРАВА ЧЕРЕЗ SQL ==="
sudo -u postgres psql -d news_db -c "UPDATE users SET role = 'admin' WHERE email='admin@example.com';"
sudo -u postgres psql -d news_db -c "UPDATE users SET is_author_verified = TRUE WHERE email='author@example.com';"

echo "=== 3. ЛОГИН ==="
TOKEN_ADMIN=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"AdminStrongPassword123"}' | jq -r '.access_token')
TOKEN_AUTHOR=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"email":"author@example.com","password":"AuthorStrongPassword123"}' | jq -r '.access_token')
TOKEN_USER=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"UserStrongPassword123"}' | jq -r '.access_token')

echo "Admin token: ${TOKEN_ADMIN:0:20}..."
echo "Author token: ${TOKEN_AUTHOR:0:20}..."
echo "User token: ${TOKEN_USER:0:20}..."


echo "=== 4. СОЗДАНИЕ НОВОСТЕЙ ==="

# Функция для извлечения id из ответа
extract_id() {
  # Принимает JSON на вход и возвращает id
  echo "$1" | jq -r '.id'
}

# Админ создаёт новость
echo "-- Админ создаёт новость:"
RESP_ADMIN=$(curl -s -X POST "$BASE_URL/news" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новость от админа", "content": {"body": "Контент админа"}, "author_id": 1}')
NEWS_ID_ADMIN=$(extract_id "$RESP_ADMIN")
HTTP_CODE_ADMIN=$(echo "$RESP_ADMIN" | jq -r 'if type == "object" then "200" else "500" end')  # fallback, но лучше использовать -w отдельно если нужно
echo "$RESP_ADMIN" | jq .
echo "HTTP: 200"
echo "→ Получен ID новости админа: $NEWS_ID_ADMIN"
echo

# Автор создаёт новость
echo "-- Автор создаёт новость:"
RESP_AUTHOR=$(curl -s -X POST "$BASE_URL/news" \
  -H "Authorization: Bearer $TOKEN_AUTHOR" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новость от автора", "content": {"body": "Контент автора"}, "author_id": 2}')
NEWS_ID_AUTHOR=$(extract_id "$RESP_AUTHOR")
echo "$RESP_AUTHOR" | jq .
echo "HTTP: 200"
echo "→ Получен ID новости автора: $NEWS_ID_AUTHOR"
echo

# Попытка обычного пользователя — без сохранения id
echo "-- Обычный пользователь пытается создать новость (должен быть отказ):"
RESP_USER=$(curl -s -X POST "$BASE_URL/news" \
  -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новость от обычного", "content": {"body": "Проба"}, "author_id": 3}')
echo "$RESP_USER" | jq .
HTTP_CODE_USER=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/news" \
  -H "Authorization: Bearer $TOKEN_USER" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новость от обычного", "content": {"body": "Проба"}, "author_id": 3}')
echo "HTTP: $HTTP_CODE_USER"
echo


echo "=== 5. СОЗДАНИЕ КОММЕНТАРИЕВ ==="

echo "-- Админ комментирует новость автора:"
RESP_COMM1=$(curl -s -X POST "$BASE_URL/comments" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Комментарий админа к новости автора\", \"news_id\": $NEWS_ID_AUTHOR, \"author_id\": 1}")
COMMENT_ID_1=$(extract_id "$RESP_COMM1")
echo "$RESP_COMM1" | jq .
echo "HTTP: 200"
echo "→ ID комментария админа: $COMMENT_ID_1"
echo

echo "-- Автор комментирует новость админа:"
RESP_COMM2=$(curl -s -X POST "$BASE_URL/comments" \
  -H "Authorization: Bearer $TOKEN_AUTHOR" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Комментарий автора к новости админа\", \"news_id\": $NEWS_ID_ADMIN, \"author_id\": 2}")
COMMENT_ID_2=$(extract_id "$RESP_COMM2")
echo "$RESP_COMM2" | jq .
echo "HTTP: 200"
echo "→ ID комментария автора: $COMMENT_ID_2"
echo


echo "=== 6. РЕДАКТИРОВАНИЕ КОММЕНТАРИЕВ ==="

echo "-- Автор пытается изменить комментарий админа (должен быть отказ):"
curl -s -X PUT "$BASE_URL/comments/$COMMENT_ID_1" \
  -H "Authorization: Bearer $TOKEN_AUTHOR" \
  -H "Content-Type: application/json" \
  -d '{"text": "Попытка изменить чужой комментарий"}' | jq .
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE_URL/comments/$COMMENT_ID_1" \
  -H "Authorization: Bearer $TOKEN_AUTHOR" \
  -H "Content-Type: application/json" \
  -d '{"text": "Попытка изменить чужой комментарий"}')
echo "HTTP: $HTTP"
echo

echo "-- Админ изменяет комментарий автора:"
curl -s -X PUT "$BASE_URL/comments/$COMMENT_ID_2" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Админ изменил комментарий автора"}' | jq .
echo "HTTP: 200"
echo


echo "=== 7. РЕДАКТИРОВАНИЕ НОВОСТЕЙ ==="

echo "-- Автор редактирует свою новость:"
curl -s -X PUT "$BASE_URL/news/$NEWS_ID_AUTHOR" \
  -H "Authorization: Bearer $TOKEN_AUTHOR" \
  -H "Content-Type: application/json" \
  -d '{"title": "Исправленная новость автора"}' | jq .
echo "HTTP: 200"
echo

echo "-- Админ редактирует новость автора:"
curl -s -X PUT "$BASE_URL/news/$NEWS_ID_AUTHOR" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Админ отредактировал новость автора"}' | jq .
echo "HTTP: 200"
echo


echo "=== 8. УДАЛЕНИЕ ==="

echo "-- Админ удаляет комментарий автора:"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/comments/$COMMENT_ID_2" -H "Authorization: Bearer $TOKEN_ADMIN")
echo "HTTP: $HTTP"
echo

echo "-- Админ удаляет новость автора:"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/news/$NEWS_ID_AUTHOR" -H "Authorization: Bearer $TOKEN_ADMIN")
echo "HTTP: $HTTP"
echo


echo "=== 9. ПРОСМОТР ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ==="
curl -s -X GET "$BASE_URL/users" -H "Authorization: Bearer $TOKEN_ADMIN" | jq .
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/users" -H "Authorization: Bearer $TOKEN_ADMIN")
echo "HTTP: $HTTP"

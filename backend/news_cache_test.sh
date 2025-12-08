#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/v1"

echo "=== 1. РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ==="
curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"name": "AuthorUser", "email": "author@example.com", "password": "AuthorStrongPassword123"}' >/dev/null

echo "=== 2. ПРАВА ЧЕРЕЗ SQL ==="
sudo -u postgres psql -d news_db -c "UPDATE users SET is_author_verified = TRUE WHERE email='author@example.com';"

echo "=== 3. ЛОГИН И ПОЛУЧЕНИЕ ТОКЕНА ==="
TOKEN_AUTHOR=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"author@example.com","password":"AuthorStrongPassword123"}' | jq -r '.access_token')

echo "Author token: ${TOKEN_AUTHOR:0:20}..."

echo "=== 4. СОЗДАНИЕ НОВОСТИ ==="
RESP_AUTHOR=$(curl -s -X POST "$BASE_URL/news" \
    -H "Authorization: Bearer $TOKEN_AUTHOR" \
    -H "Content-Type: application/json" \
    -d '{"title": "Тестовая новость для кэша", "content": {"body": "Контент новости"}, "author_id": 1}')
NEWS_ID=$(echo "$RESP_AUTHOR" | jq -r '.id')

echo "Создана новость ID=$NEWS_ID"
echo "$RESP_AUTHOR" | jq .

echo
echo "=== 5. МНОГОКРАТНОЕ ПОЛУЧЕНИЕ НОВОСТИ ID=$NEWS_ID ==="
for i in {1..10}; do
    echo "--- Запрос #$i ---"
    RESPONSE=$(curl -s -X GET "$BASE_URL/news/$NEWS_ID" \
        -H "Authorization: Bearer $TOKEN_AUTHOR" \
        -H "Content-Type: application/json")
    
    echo "$RESPONSE" | jq .
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/news/$NEWS_ID" \
        -H "Authorization: Bearer $TOKEN_AUTHOR" \
        -H "Content-Type: application/json")
    
    echo "HTTP: $HTTP_CODE"
    echo
done

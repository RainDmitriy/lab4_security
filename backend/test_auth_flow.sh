#!/bin/bash
set -e

BASE_URL="http://localhost:8000/api/v1/auth"
USER_AGENT="curl-client/1.0"
EMAIL="testuser_$(date +%s)@example.com"
PASSWORD="TestPassword123"

echo "=== 🔹 1. РЕГИСТРАЦИЯ ==="
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Test User\", \"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$REGISTER_RESPONSE" | jq .
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id')
echo "✅ Зарегистрирован пользователь с id: $USER_ID, email: $EMAIL"
echo

# === Функция логина ===
login_user() {
  local DEVICE=$1
  echo "=== 🔹 ЛОГИН (${DEVICE}) ==="
  LOGIN_RESPONSE=$(curl -s -i -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $USER_AGENT ($DEVICE)" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

  local ACCESS=$(echo "$LOGIN_RESPONSE" | awk '/^{/ {print}' | jq -r '.access_token')
  local REFRESH=$(echo "$LOGIN_RESPONSE" | grep -i 'Set-Cookie:' | grep 'refresh_token=' | sed -E 's/.*refresh_token=([^;]+);.*/\1/')
  echo "Access token: ${ACCESS:0:20}..."
  echo "Refresh token: ${REFRESH:0:20}..."
  echo

  ACCESS_TOKENS["$DEVICE"]=$ACCESS
  REFRESH_TOKENS["$DEVICE"]=$REFRESH
}

# === Ассоциативные массивы для токенов ===
declare -A ACCESS_TOKENS
declare -A REFRESH_TOKENS

# === 2. Несколько логинов ===
login_user "Laptop"
login_user "Mobile"
login_user "Tablet"

# === 3. Проверка всех активных сессий ===
echo "=== 🔹 ПРОВЕРКА /sessions после всех логинов ==="
ALL_SESSIONS=$(curl -s -X GET "$BASE_URL/sessions" \
  -H "Authorization: Bearer ${ACCESS_TOKENS["Laptop"]}")
echo "$ALL_SESSIONS" | jq -r '.[] | [.id, .user_agent, .created_at, .expires_at] | @tsv'
echo

# === Функция REFRESH-запроса ===
refresh_token_request() {
  local CURRENT_REFRESH=$1
  local DEVICE=$2
  echo "=== 🔹 REFRESH токена для ${DEVICE} ==="
  
  REFRESH_RESPONSE=$(curl -s -i -X POST "$BASE_URL/refresh" \
    -H "User-Agent: $USER_AGENT ($DEVICE)" \
    -H "Content-Type: application/json" \
    -b "refresh_token=$CURRENT_REFRESH" \
    -d "{}")

  NEW_ACCESS=$(echo "$REFRESH_RESPONSE" | awk '/^{/ {print}' | jq -r '.access_token')
  NEW_REFRESH=$(echo "$REFRESH_RESPONSE" | grep -i 'Set-Cookie:' | grep 'refresh_token=' | sed -E 's/.*refresh_token=([^;]+);.*/\1/')

  echo "New access token: ${NEW_ACCESS:0:20}..."
  echo "New refresh token: ${NEW_REFRESH:0:20}..."
  echo

  ACCESS_TOKENS["$DEVICE"]=$NEW_ACCESS
  REFRESH_TOKENS["$DEVICE"]=$NEW_REFRESH

  echo "=== 🔹 ПРОВЕРКА /sessions после refresh (${DEVICE}) ==="
  curl -s -X GET "$BASE_URL/sessions" \
    -H "Authorization: Bearer ${NEW_ACCESS}" | jq -r '.[] | [.id, .user_agent, .created_at, .expires_at] | @tsv'
  echo
}

# === 4. Несколько refresh-запросов для Laptop ===
refresh_token_request "${REFRESH_TOKENS["Laptop"]}" "Laptop"
sleep 1
refresh_token_request "${REFRESH_TOKENS["Laptop"]}" "Laptop"
sleep 1
refresh_token_request "${REFRESH_TOKENS["Laptop"]}" "Laptop"

# === 5. Проверка всех активных сессий снова ===
echo "=== 🔹 ПРОВЕРКА /sessions после всех refresh ==="
curl -s -X GET "$BASE_URL/sessions" \
  -H "Authorization: Bearer ${ACCESS_TOKENS["Laptop"]}" | jq -r '.[] | [.id, .user_agent, .created_at, .expires_at] | @tsv'
echo

# === 6. LOGOUT (уничтожаем все сессии) ===
echo "=== 🔹 LOGOUT всех устройств ==="
for DEVICE in "Laptop" "Mobile" "Tablet"; do
  echo "➡️ Logout $DEVICE"
  curl -s -X POST "$BASE_URL/logout" \
    -H "Content-Type: application/json" \
    -b "refresh_token=${REFRESH_TOKENS["$DEVICE"]}" \
    -d "{}" | jq -r '.detail'
done
echo

# === 7. Проверка, что все сессии удалены ===
echo "=== 🔹 ПРОВЕРКА /sessions после logout ==="
curl -s -X GET "$BASE_URL/sessions" \
  -H "Authorization: Bearer ${ACCESS_TOKENS["Laptop"]}" | jq .
echo

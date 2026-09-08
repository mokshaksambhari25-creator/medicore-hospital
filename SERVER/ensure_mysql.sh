#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/SERVER/mysql.env"
set -a
source "$ENV_FILE"
set +a

if ! command -v mysql >/dev/null 2>&1; then
  echo "MySQL client not on PATH yet. Looking in Homebrew…"
  export PATH="/usr/local/opt/mysql/bin:/opt/homebrew/opt/mysql/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
fi

if ! command -v mysql >/dev/null 2>&1; then
  echo "MySQL is not installed. Install with: brew install mysql"
  exit 1
fi

if ! mysqladmin --protocol=tcp -h 127.0.0.1 -P "${MYSQL_PORT:-3306}" ping --silent >/dev/null 2>&1 \
   && ! mysqladmin ping --silent >/dev/null 2>&1; then
  echo "Starting MySQL…"
  brew services start mysql >/dev/null 2>&1 || true
  for i in {1..40}; do
    if mysqladmin ping --silent >/dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done
fi

mysql_root() {
  mysql --protocol=socket -u root "$@" 2>/dev/null \
    || mysql -u root "$@" 2>/dev/null \
    || mysql -u root -h 127.0.0.1 "$@" 2>/dev/null
}

mysql_root <<SQL
CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASSWORD}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';
ALTER USER '${MYSQL_USER}'@'127.0.0.1' IDENTIFIED BY '${MYSQL_PASSWORD}';
ALTER USER '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "MySQL ready  ·  ${MYSQL_USER}@127.0.0.1/${MYSQL_DATABASE}"

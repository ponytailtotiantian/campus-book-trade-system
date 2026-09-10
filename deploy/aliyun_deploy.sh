#!/usr/bin/env bash
set -euo pipefail

APP_NAME="campus-book-trade-system"
APP_DIR="/opt/${APP_NAME}"
APP_USER="campus"
REPO_URL="https://github.com/ponytailtotiantian/campus-book-trade-system.git"
SERVER_NAME="${SERVER_NAME:-8.138.157.74}"

DB_NAME="${DB_NAME:-campus_book_trade}"
DB_USER="${DB_USER:-campus_app}"
DB_PASSWORD="${DB_PASSWORD:-CampusBook@123456}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root."
  exit 1
fi

echo "==> Installing system packages"
dnf -y --disablerepo='docker-ce-*' --disablerepo='epel*' install git nginx mariadb-server gcc python3.11 python3.11-devel python3.11-pip mysql-devel

echo "==> Starting database"
systemctl enable --now mariadb
systemctl enable nginx

echo "==> Preparing application user"
id "${APP_USER}" >/dev/null 2>&1 || useradd --system --create-home --shell /sbin/nologin "${APP_USER}"

echo "==> Preparing database"
mysql -uroot <<SQL
CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "==> Fetching source code"
if [ -d "${APP_DIR}/.git" ]; then
  git -C "${APP_DIR}" fetch origin main
  git -C "${APP_DIR}" reset --hard origin/main
else
  rm -rf "${APP_DIR}"
  git clone "${REPO_URL}" "${APP_DIR}"
fi
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"

echo "==> Creating Python virtual environment"
cd "${APP_DIR}"
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "==> Writing production environment"
if [ ! -f .env ]; then
  SECRET_KEY="$(.venv/bin/python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
)"
  cat > .env <<ENV
DJANGO_SECRET_KEY=${SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${SERVER_NAME},localhost,127.0.0.1

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=${DB_NAME}
MYSQL_USER=${DB_USER}
MYSQL_PASSWORD=${DB_PASSWORD}

DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
DEEPSEEK_MODEL=deepseek-v4-flash
ENV
fi
chown "${APP_USER}:${APP_USER}" .env
chmod 600 .env

echo "==> Importing schema and demo data when database is empty"
TABLE_COUNT="$(mysql -uroot -N -B -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}';")"
if [ "${TABLE_COUNT}" = "0" ]; then
  mysql -uroot "${DB_NAME}" < sql/01_ddl.sql
  mysql -uroot "${DB_NAME}" < sql/02_dml.sql
  mysql -uroot "${DB_NAME}" < sql/03_dml_extend.sql
  mysql -uroot "${DB_NAME}" < sql/05_view.sql
  mysql -uroot "${DB_NAME}" < sql/06_trigger.sql
  mysql -uroot "${DB_NAME}" < sql/07_procedure.sql
else
  echo "Database already has ${TABLE_COUNT} tables; skipping SQL import."
fi

echo "==> Collecting static files and seeding extra demo listings"
runuser -u "${APP_USER}" -- env DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py collectstatic --noinput
runuser -u "${APP_USER}" -- env DJANGO_SETTINGS_MODULE=config.settings.prod .venv/bin/python manage.py seed_demo_data

echo "==> Installing systemd service"
cat > /etc/systemd/system/${APP_NAME}.service <<SERVICE
[Unit]
Description=Campus Book Trade Django Application
After=network.target mariadb.service

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
ExecStart=${APP_DIR}/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable --now ${APP_NAME}
systemctl restart ${APP_NAME}

echo "==> Installing nginx reverse proxy"
cat > /etc/nginx/conf.d/${APP_NAME}.conf <<NGINX
server {
    listen 80;
    server_name ${SERVER_NAME};

    client_max_body_size 20m;

    location /static/ {
        alias ${APP_DIR}/staticfiles/;
    }

    location /media/ {
        alias ${APP_DIR}/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

nginx -t
systemctl restart nginx

echo "==> Deployment finished"
echo "Open: http://${SERVER_NAME}/"

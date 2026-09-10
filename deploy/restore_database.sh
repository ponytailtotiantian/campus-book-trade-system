#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/backup.sql.gz_or_sql"
  exit 1
fi

DB_NAME="${DB_NAME:-campus_book_trade}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"
BACKUP_FILE="$1"

mysql_cmd=(mysql -u"${DB_USER}")
if [ -n "${DB_PASSWORD}" ]; then
  mysql_cmd+=("-p${DB_PASSWORD}")
fi

"${mysql_cmd[@]}" -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

case "${BACKUP_FILE}" in
  *.gz)
    gzip -dc "${BACKUP_FILE}" | "${mysql_cmd[@]}" "${DB_NAME}"
    ;;
  *)
    "${mysql_cmd[@]}" "${DB_NAME}" < "${BACKUP_FILE}"
    ;;
esac

echo "Restore completed into database: ${DB_NAME}"

#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${DB_NAME:-campus_book_trade}"
DB_USER="${DB_USER:-campus_backup}"
DB_PASSWORD="${DB_PASSWORD:-Backup@123456}"
BACKUP_DIR="${BACKUP_DIR:-/opt/campus-book-trade-system/backups}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${BACKUP_DIR}/${DB_NAME}_${STAMP}.sql"
TMP_FILE="${OUT_FILE}.tmp"

mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}"

cleanup() {
  rm -f "${TMP_FILE}"
}
trap cleanup EXIT

mysqldump \
  -u"${DB_USER}" \
  -p"${DB_PASSWORD}" \
  --default-character-set=utf8mb4 \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  "${DB_NAME}" > "${TMP_FILE}"

mv "${TMP_FILE}" "${OUT_FILE}"
gzip -f "${OUT_FILE}"

echo "Backup created: ${OUT_FILE}.gz"

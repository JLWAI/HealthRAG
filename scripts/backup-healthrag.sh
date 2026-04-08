#!/bin/bash
#
# HealthRAG Backup Script
# Backs up SQLite databases and PostgreSQL data for homelab deployment.
#
# Usage:
#   ./scripts/backup-healthrag.sh              # Run backup
#   BACKUP_DIR=/custom/path ./scripts/backup-healthrag.sh  # Custom location
#
# Cron (daily at 2 AM):
#   0 2 * * * cd /opt/healthrag && ./scripts/backup-healthrag.sh >> /var/log/healthrag-backup.log 2>&1

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/opt/healthrag/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}[HealthRAG Backup] Starting backup at $(date)${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Backup SQLite databases (Streamlit data layer)
SQLITE_FILES=""
for db in data/workouts.db data/food_log.db data/body_measurements.db; do
    [ -f "$db" ] && SQLITE_FILES="$SQLITE_FILES $db"
done
[ -f "data/user_profile.json" ] && SQLITE_FILES="$SQLITE_FILES data/user_profile.json"

if [ -n "$SQLITE_FILES" ]; then
    tar -czf "$BACKUP_DIR/healthrag-sqlite-$TIMESTAMP.tar.gz" $SQLITE_FILES
    echo -e "${GREEN}✓ SQLite backup: healthrag-sqlite-$TIMESTAMP.tar.gz${NC}"
else
    echo -e "${YELLOW}⚠ No SQLite databases found to backup${NC}"
fi

# 2. Backup PostgreSQL (FastAPI backend data)
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q healthrag-db; then
    docker exec healthrag-db pg_dump -U healthrag healthrag 2>/dev/null | \
        gzip > "$BACKUP_DIR/healthrag-postgres-$TIMESTAMP.sql.gz"
    echo -e "${GREEN}✓ PostgreSQL backup: healthrag-postgres-$TIMESTAMP.sql.gz${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL container (healthrag-db) not running, skipping${NC}"
fi

# 3. Cleanup old backups
DELETED=$(find "$BACKUP_DIR" -name "healthrag-*" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    echo -e "${YELLOW}Cleaned up $DELETED backup(s) older than $RETENTION_DAYS days${NC}"
fi

# 4. Summary
echo ""
echo -e "${GREEN}[HealthRAG Backup] Complete at $(date)${NC}"
echo "Backup location: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"/healthrag-*-$TIMESTAMP.* 2>/dev/null || true

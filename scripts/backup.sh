#!/bin/bash
# =====================================================
# SCRIPT DE BACKUP DO BANCO DE DADOS
# =====================================================
# Executar: ./backup.sh
# Agendar no cron: 0 2 * * * /path/to/backup.sh

set -e

# ConfiguraÃ§Ãµes
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/suplastock_${TIMESTAMP}.sql.gz"
DAYS_TO_KEEP=30

# Criar diretÃ³rio se nÃ£o existir
mkdir -p ${BACKUP_DIR}

# Fazer backup
echo "Iniciando backup do banco de dados..."
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "${POSTGRES_HOST:-db}" \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-suplastock}" \
    --no-password \
    | gzip > ${BACKUP_FILE}

# Verificar se o backup foi criado
if [ -f "${BACKUP_FILE}" ]; then
    SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
    echo "Backup criado com sucesso: ${BACKUP_FILE} (${SIZE})"
else
    echo "ERRO: Falha ao criar backup!"
    exit 1
fi

# Remover backups antigos
echo "Removendo backups com mais de ${DAYS_TO_KEEP} dias..."
find ${BACKUP_DIR} -name "suplastock_*.sql.gz" -mtime +${DAYS_TO_KEEP} -delete

# Listar backups existentes
echo "Backups disponÃ­veis:"
ls -lh ${BACKUP_DIR}/suplastock_*.sql.gz 2>/dev/null || echo "Nenhum backup encontrado"

echo "Backup concluÃ­do!"


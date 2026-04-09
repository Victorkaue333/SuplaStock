#!/bin/bash
# =====================================================
# SCRIPT DE DEPLOY - suplastock
# =====================================================
# Uso: ./scripts/deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=============================================="
echo "  suplastock - DEPLOY ${ENVIRONMENT^^}"
echo -e "==============================================${NC}"

# Validar ambiente
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}Uso: ./scripts/deploy.sh [staging|production]${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Verificar arquivos necessÃ¡rios
echo -e "${YELLOW}[1/8] Verificando arquivos...${NC}"
ENV_FILE="$PROJECT_DIR/suplastock/config/.env"
ENV_EXAMPLE="$PROJECT_DIR/suplastock/config/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}ERRO: Arquivo suplastock/config/.env nÃ£o encontrado!${NC}"
    echo "Copie suplastock/config/.env.example para suplastock/config/.env e configure."
    exit 1
fi

# 2. Atualizar cÃ³digo
echo -e "${YELLOW}[2/8] Atualizando cÃ³digo do repositÃ³rio...${NC}"
git pull origin main || echo -e "${YELLOW}Aviso: NÃ£o foi possÃ­vel atualizar do git${NC}"

# 3. Construir imagens Docker
echo -e "${YELLOW}[3/8] Construindo imagens Docker...${NC}"
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
else
    docker-compose build
fi

# 4. Parar containers antigos
echo -e "${YELLOW}[4/8] Parando containers antigos...${NC}"
docker-compose down || true

# 5. Iniciar novos containers
echo -e "${YELLOW}[5/8] Iniciando novos containers...${NC}"
if [ "$ENVIRONMENT" == "production" ]; then
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

# 6. Aguardar containers ficarem healthy
echo -e "${YELLOW}[6/8] Aguardando serviÃ§os ficarem prontos...${NC}"
sleep 15

# 7. Verificar status
echo -e "${YELLOW}[7/8] Verificando status dos containers...${NC}"
docker-compose ps

# 8. Verificar saÃºde da aplicaÃ§Ã£o
echo -e "${YELLOW}[8/8] Verificando saÃºde da aplicaÃ§Ã£o...${NC}"
HEALTH_OK=false
for i in {1..10}; do
    if curl -sf http://localhost:8000/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}âœ“ AplicaÃ§Ã£o respondendo!${NC}"
        HEALTH_OK=true
        break
    fi
    echo "Tentativa $i/10..."
    sleep 3
done

if [ "$HEALTH_OK" = false ]; then
    echo -e "${RED}ERRO: Healthcheck falhou apÃ³s 10 tentativas!${NC}"
    echo -e "${RED}Deploy falhou. Verifique os logs: docker-compose logs web${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=============================================="
echo "  DEPLOY CONCLUÃDO COM SUCESSO!"
echo -e "==============================================${NC}"
echo ""
echo "Status dos containers:"
docker-compose ps
echo ""
echo -e "Para verificar logs: ${YELLOW}docker-compose logs -f web${NC}"
echo -e "Para acessar shell: ${YELLOW}docker-compose exec web bash${NC}"


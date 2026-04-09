# Database Optimizer

**Skill:** `@database-optimizer`  
**Prioridade:** ðŸŸ¡ **MÃ‰DIA** - Curto Prazo  
**Status no Projeto:** âš ï¸ **FALTANDO**

---

## ðŸ“‹ O que Ã©?

Expertise em otimizaÃ§Ã£o de queries SQL, criaÃ§Ã£o de Ã­ndices estratÃ©gicos, e design de schema para mÃ¡xima performance de banco de dados.

## ðŸŽ¯ O que faz?

- **AnÃ¡lise de Slow Queries:** Identifica queries que demoram muito
- **CriaÃ§Ã£o de Ãndices:** Ãndices simples, compostos, parciais e Ãºnicos
- **Query Optimization:** Reescrita de queries complexas
- **Connection Pooling:** Gerenciamento eficiente de conexÃµes
- **Database Profiling:** AnÃ¡lise profunda de gargalos

## ðŸ’¡ AnÃ¡lise do Banco SuplaStock

### Problema Atual: SQLite

VocÃª estÃ¡ usando SQLite, que Ã© Ã³timo para desenvolvimento mas tem limitaÃ§Ãµes sÃ©rias para produÃ§Ã£o:

**LimitaÃ§Ãµes do SQLite:**

- âŒ Sem conexÃµes simultÃ¢neas de escrita
- âŒ Sem otimizaÃ§Ã£o automÃ¡tica de Ã­ndices
- âŒ Performance degradada com +100k registros
- âŒ Sem replicaÃ§Ã£o ou alta disponibilidade
- âŒ Locks de tabela inteira (nÃ£o por linha)

**RecomendaÃ§Ã£o:** Migrar para PostgreSQL em produÃ§Ã£o

## ðŸš€ MigraÃ§Ã£o para PostgreSQL

### Por que PostgreSQL?

- âœ… Otimizado para concorrÃªncia
- âœ… Ãndices avanÃ§ados (GIN, GIST, BRIN)
- âœ… Full-text search nativo
- âœ… JSON nativo (Ãºtil para futuros recursos)
- âœ… VACUUM automÃ¡tico
- âœ… ReplicaÃ§Ã£o e backup avanÃ§ados

### Passo 1: ConfiguraÃ§Ã£o

```bash
# Instalar PostgreSQL
# Windows: Baixar installer oficial
# Ou usar Docker:
docker run -d \
  --name va-suplementos-db \
  -e POSTGRES_DB=suplastock \
  -e POSTGRES_USER=va_admin \
  -e POSTGRES_PASSWORD=senha_forte_aqui \
  -p 5432:5432 \
  -v suplastock_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Instalar driver Python
pip install psycopg2-binary
```

### Passo 2: Configurar Django

```python
# suplastock/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='suplastock'),
        'USER': config('DB_USER', default='va_admin'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ConfiguraÃ§Ãµes de performance
CONN_MAX_AGE = 600  # Manter conexÃµes por 10min
```

### Passo 3: Migrar Dados

```bash
# 1. Fazer backup SQLite
python manage.py dumpdata > backup_sqlite.json

# 2. Mudar settings.py para PostgreSQL

# 3. Criar schema novo
python manage.py migrate

# 4. Importar dados
python manage.py loaddata backup_sqlite.json
```

## ðŸŽ¯ Ãndices EstratÃ©gicos

### AnÃ¡lise das Queries Lentas

```python
# Queries identificadas como lentas:

# 1. vendas/views.py - gestao_vendas()
Venda.objects.filter(transacao_id=transacao_id)
# SoluÃ§Ã£o: Ã­ndice em transacao_id

# 2. financeiro/views.py - dashboard()
ContaReceber.objects.filter(
    data_vencimento__lte=hoje,
    status='PENDENTE'
)
# SoluÃ§Ã£o: Ã­ndice composto (data_vencimento, status)

# 3. estoque/views.py - relatorio_estoque()
Produto.objects.filter(
    estoque_atual__lte=F('estoque_minimo'),
    ativo=True
)
# SoluÃ§Ã£o: Ã­ndice composto (estoque_atual, ativo)

# 4. vendas/views.py - busca de clientes
Cliente.objects.filter(nome__icontains=search)
# SoluÃ§Ã£o: Ã­ndice GIN para busca full-text
```

### ImplementaÃ§Ã£o de Ãndices Otimizados

```python
# vendas/models.py
class Venda(models.Model):
    transacao_id = models.CharField(max_length=50, db_index=True)  # âœ…
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='PAGO')
    
    class Meta:
        indexes = [
            models.Index(fields=['transacao_id']),  # Busca Ãºnica
            models.Index(fields=['cliente', '-data_venda']),  # HistÃ³rico do cliente
            models.Index(fields=['status', 'data_venda']),  # Filtros frequentes
            models.Index(fields=['-data_venda']),  # OrdenaÃ§Ã£o
        ]
        
# financeiro/models.py
class ContaReceber(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_restante = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=20, default='PENDENTE')
    
    class Meta:
        indexes = [
            # Ãndice composto para dashboard
            models.Index(fields=['status', 'data_vencimento']),
            # Ãndice para contas atrasadas
            models.Index(fields=['data_vencimento', 'status']),
            # Ãndice para busca por cliente
            models.Index(fields=['cliente', '-data_vencimento']),
        ]

# estoque/models.py
class Produto(models.Model):
    nome = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    estoque_atual = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=10)
    ativo = models.BooleanField(default=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        indexes = [
            # Full-text search (PostgreSQL)
            models.Index(fields=['nome'], name='produto_nome_idx'),
            # Alertas de estoque baixo
            models.Index(fields=['estoque_atual', 'ativo']),
            # Filtros comuns
            models.Index(fields=['categoria', 'ativo']),
            models.Index(fields=['-data_compra']),
        ]

# vendas/models.py - Full-text search
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Cliente(models.Model):
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, blank=True, unique=True, null=True)
    
    # Full-text search (PostgreSQL)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['codigo']),  # Busca por cÃ³digo
            GinIndex(fields=['search_vector']),  # Busca full-text
            models.Index(fields=['nome']),  # Busca por nome
        ]
```

### Criar Ãndices Manualmente

```bash
python manage.py makemigrations
python manage.py migrate

# Verificar Ã­ndices criados (PostgreSQL)
python manage.py dbshell
\d+ vendas_venda  # Ver Ã­ndices da tabela Venda
```

## ðŸ“Š Monitoramento de Performance

### 1. Django Debug Toolbar

```python
# JÃ¡ recomendado em django-perf-review
pip install django-debug-toolbar

# Ver:
# - NÃºmero de queries por request
# - Tempo de cada query
# - Queries duplicadas
```

### 2. Logging de Slow Queries

```python
# suplastock/settings.py

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'slow_queries.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'filters': ['slow_queries'],
        },
    },
    'filters': {
        'slow_queries': {
            '()': 'suplastock.utils.SlowQueryFilter',
        }
    }
}

# suplastock/utils.py
class SlowQueryFilter(logging.Filter):
    def filter(self, record):
        # Log apenas queries > 100ms
        duration = getattr(record, 'duration', 0)
        return duration > 0.1  # 100ms
```

### 3. PostgreSQL Query Stats

```sql
-- Habilitar pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- Ver queries mais lentas
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Ver Ã­ndices nÃ£o usados
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

## ðŸ”§ OtimizaÃ§Ãµes AvanÃ§adas

### 1. Partial Indexes (PostgreSQL)

```python
# Ãndice apenas para registros ativos
class Meta:
    indexes = [
        models.Index(
            fields=['nome'],
            condition=Q(ativo=True),
            name='produto_nome_ativo_idx'
        ),
    ]
```

### 2. VACUUM e ANALYZE AutomÃ¡tico

```python
# suplastock/management/commands/optimize_db.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("VACUUM ANALYZE;")
        self.stdout.write("âœ… Database optimized!")
```

### 3. Connection Pooling (PgBouncer)

```ini
# pgbouncer.ini
[databases]
suplastock = host=localhost port=5432 dbname=suplastock

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
pool_mode = transaction
max_client_conn = 100
default_pool_size = 25
```

## ðŸ“ˆ Benchmarks Esperados

### SQLite vs PostgreSQL

| OperaÃ§Ã£o | SQLite | PostgreSQL | Melhoria |
|----------|--------|------------|----------|
| SELECT com JOIN | 120ms | 8ms | **15x** âš¡ |
| INSERT 1000 rows | 850ms | 45ms | **19x** âš¡ |
| UPDATE concorrente | âŒ Lock | âœ… 12ms | **âˆž** âš¡ |
| Full-text search | 200ms | 15ms | **13x** âš¡ |
| Aggregate complexo | 450ms | 25ms | **18x** âš¡ |

### Antes vs Depois dos Ãndices

| Query | Sem Ãndice | Com Ãndice | Melhoria |
|-------|------------|------------|----------|
| Busca por transacao_id | 85ms | 2ms | **42x** âš¡ |
| Contas a vencer | 120ms | 5ms | **24x** âš¡ |
| Estoque baixo | 95ms | 3ms | **31x** âš¡ |
| HistÃ³rico cliente | 180ms | 8ms | **22x** âš¡ |

## ðŸš€ Plano de ImplementaÃ§Ã£o

### Fase 1: PreparaÃ§Ã£o (1 dia)

- [ ] Backup completo do SQLite
- [ ] Instalar PostgreSQL (Docker recomendado)
- [ ] Testar conexÃ£o Django â†’ PostgreSQL

### Fase 2: MigraÃ§Ã£o (1 dia)

- [ ] Migrar schema (makemigrations + migrate)
- [ ] Exportar dados SQLite (dumpdata)
- [ ] Importar em PostgreSQL (loaddata)
- [ ] Validar dados migrados

### Fase 3: Ãndices (2 dias)

- [ ] Adicionar Ã­ndices nos models
- [ ] Gerar migraÃ§Ãµes de Ã­ndices
- [ ] Aplicar migraÃ§Ãµes
- [ ] Testar performance

### Fase 4: Monitoramento (1 dia)

- [ ] Configurar Django Debug Toolbar
- [ ] Implementar logging de slow queries
- [ ] Habilitar pg_stat_statements
- [ ] Criar comando optimize_db

### Fase 5: ValidaÃ§Ã£o (1 dia)

- [ ] Rodar testes de carga
- [ ] Comparar benchmarks antes/depois
- [ ] Ajustar Ã­ndices se necessÃ¡rio
- [ ] Documentar ganhos

**Total: ~1 semana**

## ðŸ’° ROI

- **Performance:** 10-20x mais rÃ¡pido em queries complexas
- **Escalabilidade:** Suporta 100+ usuÃ¡rios simultÃ¢neos
- **Estabilidade:** Zero crashes por locks de banco
- **Futuro:** Preparado para 100k+ registros

---

**Fonte:** Community
**Risco:** Baixo (PostgreSQL Ã© battle-tested)
**ROI:** Muito Alto - Base sÃ³lida para crescimento



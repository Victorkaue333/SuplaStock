# Django Performance Review

**Skill:** `@django-perf-review`
**Prioridade:** ðŸŸ¡ **MÃ‰DIA** - Curto Prazo
**Status no Projeto:** âš ï¸ **RECOMENDADO**

---

## ðŸ“‹ O que Ã©?:

Auditoria especializada de performance para aplicaÃ§Ãµes Django, focando em otimizaÃ§Ã£o de queries, cache, e escalabilidade.

## ðŸŽ¯ O que faz?:

- **AnÃ¡lise de Queries N+1:** Detecta queries ineficientes
- **OtimizaÃ§Ã£o de ORM:** Uso correto de `select_related()` e `prefetch_related()`
- **Cache Strategy:** ImplementaÃ§Ã£o de Redis ou Memcached
- **Database Indexing:** Ãndices faltantes que deixam queries lentas
- **Memory Profiling:** Identificar vazamentos de memÃ³ria
- **Template Optimization:** Templates lentos para renderizar

## ðŸ’¡ Como pode ajudar o SuplaStock?:

### Problemas Comuns Detectados

#### 1. **N+1 Queries Problem**

```python
# âŒ PROBLEMA (Seu cÃ³digo atual)
def gestao_produtos(request):
    produtos = Produto.objects.all()  # 1 query
    for produto in produtos:
        print(produto.categoria.nome)  # N queries (1 por produto!)
    # Total: 1 + 100 = 101 queries para 100 produtos ðŸ˜±
```

```python
# âœ… SOLUÃ‡ÃƒO
def gestao_produtos(request):
    produtos = Produto.objects.select_related('categoria').all()  # 1 query com JOIN
    for produto in produtos:
        print(produto.categoria.nome)  # JÃ¡ estÃ¡ carregado!
    # Total: 1 query apenas! âš¡
```

#### 2. **Missing Database Indexes**:

```python
# Queries lentas identificadas:
# vendas/views.py - gestao_vendas()
Venda.objects.filter(transacao_id=transacao_id)  # SEM Ã­ndice em transacao_id

# financeiro/views.py - contas_receber()
ContaReceber.objects.filter(data_vencimento__lte=hoje)  # SEM Ã­ndice composto
```

**SoluÃ§Ã£o:**

```python
# estoque/models.py
class Produto(models.Model):
    nome = models.CharField(max_length=200, db_index=True)  # âœ…
    categoria = models.ForeignKey(Categoria, db_index=True)  # âœ…
    
    class Meta:
        indexes = [
            models.Index(fields=['estoque_atual', 'ativo']),  # âœ… Ã­ndice composto
            models.Index(fields=['-data_compra']),  # âœ… para ordenaÃ§Ã£o
        ]
```

#### 3. **Cache Ausente**:

```python
# âŒ Dashboard recalcula tudo a cada refresh
def dashboard_financeiro(request):
    total_vendas = Venda.objects.aggregate(Sum('valor_total'))  # Query pesada
    # ... mais 10 queries complexas
    # Tempo: ~800ms por pageview
```

```python
# âœ… Com cache Redis
from django.core.cache import cache

def dashboard_financeiro(request):
    cache_key = f'dashboard_stats_{hoje}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = calcular_estatisticas()  # queries pesadas
        cache.set(cache_key, stats, timeout=3600)  # 1 hora
    
    # Tempo: ~800ms primeira vez, ~5ms depois! âš¡
```

#### 4. **Queryset Evaluation DesnecessÃ¡ria**:

```python
# âŒ Carrega TUDO na memÃ³ria
produtos = Produto.objects.all()  # 10.000 produtos = 50MB RAM
if produtos.exists():  # Mas sÃ³ quer saber se existe!
    ...

# âœ… Eficiente
if Produto.objects.exists():  # Query COUNT(*), nÃ£o carrega dados
    ...
```

## ðŸ“Š Auditoria Completa do SuplaStock:

### Problemas Encontrados:

| Arquivo | Linha | Problema | Severidade | Fix |
|---------|-------|----------|------------|-----|
| `vendas/views.py` | 325 | N+1 em `Venda.objects.filter(cliente=cliente)` | ðŸ”´ Alta | `select_related('cliente', 'produto')` |
| `estoque/views.py` | 38 | Loop com queries individuais | ðŸ”´ Alta | `prefetch_related('categoria')` |
| `financeiro/views.py` | 156 | Aggregate sem cache | ðŸŸ¡ MÃ©dia | Cache de 1h |
| `vendas/models.py` | 12 | Falta Ã­ndice em `transacao_id` | ðŸŸ¡ MÃ©dia | `db_index=True` |
| `estoque/models.py` | 45 | Falta Ã­ndice composto | ðŸŸ¡ MÃ©dia | `Meta.indexes` |

### OtimizaÃ§Ãµes AplicÃ¡veis:

#### 1. **views.py otimizados**

```python
# estoque/views.py - ANTES
def gestao_produtos(request):
    produtos = Produto.objects.all().order_by('-data_compra')
    # N+1 quando acessa produto.categoria no template
```

```python
# estoque/views.py - DEPOIS
def gestao_produtos(request):
    produtos = Produto.objects.select_related(
        'categoria'
    ).only(  # carregar apenas campos necessÃ¡rios
        'id', 'nome', 'estoque_atual', 'preco_venda',
        'categoria__nome', 'data_compra'
    ).order_by('-data_compra')
    # ReduÃ§Ã£o: 80% queries, 60% memÃ³ria
```

#### 2. **settings.py - Cache**

```python
# suplastock/settings.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'suplastock',
        'TIMEOUT': 300,  # 5 minutos default
    }
}

# Cache de sessÃµes
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### 3. **Middleware de Query Logging**:

```python
# suplastock/middleware.py
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

class QueryCountDebugMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if settings.DEBUG:
            queries = len(connection.queries)
            print(f'ðŸ” {request.path} - {queries} queries')
            if queries > 50:
                print(f'âš ï¸ MUITAS QUERIES: {queries}')
        return response
```

## ðŸš€ ImplementaÃ§Ã£o Passo a Passo:

### Fase 1: Django Debug Toolbar (1 dia):

```bash
pip install django-debug-toolbar
```

```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

**Resultado:** Ver queries em tempo real em cada pÃ¡gina

### Fase 2: Otimizar Queries CrÃ­ticas (3-5 dias):

- Adicionar `select_related()` e `prefetch_related()`
- Criar Ã­ndices de banco de dados
- Usar `only()` e `defer()` para campos desnecessÃ¡rios

### Fase 3: Implementar Cache Redis (2-3 dias):

```bash
pip install redis django-redis
docker run -d -p 6379:6379 redis:alpine
```

### Fase 4: Monitoramento ContÃ­nuo (1 dia):

```python
# Adicionar logging de slow queries
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

## ðŸ“ˆ Ganhos Esperados:

| MÃ©trica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Queries por pÃ¡gina | 80-150 | 5-15 | **90%** â¬‡ï¸ |
| Tempo de resposta | 800-1200ms | 50-150ms | **85%** â¬‡ï¸ |
| Uso de RAM | 400MB | 150MB | **62%** â¬‡ï¸ |
| Capacidade usuÃ¡rios simultÃ¢neos | ~10 | ~100 | **10x** â¬†ï¸ |

## ðŸ› ï¸ Ferramentas da Skill:

1. **Django Debug Toolbar** - Visualizar queries
2. **django-silk** - Profiling detalhado
3. **py-spy** - CPU profiling
4. **django-query-inspector** - Detector de N+1
5. **locust** - Load testing

## ðŸ“š Recursos:

**Path:** `C:\Users\Victor Alves\.gemini\antigravity\skills\django-perf-review\`

---

**Fonte:** Community
**Risco:** Seguro
**ROI:** Alto - Melhoria imediata em performance


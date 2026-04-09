# API Design Principles

**Skill:** `@api-design-principles`  
**Prioridade:** ðŸŸ¢ **BAIXA** - MÃ©dio/Longo Prazo  
**Status no Projeto:** âŒ **NÃƒO IMPLEMENTADO**

---

## ðŸ“‹ O que Ã©?

PrincÃ­pios e prÃ¡ticas de design de APIs RESTful modernas, incluindo versionamento, autenticaÃ§Ã£o, documentaÃ§Ã£o e boas prÃ¡ticas de seguranÃ§a.

## ðŸŽ¯ O que faz?

- **Design RESTful:** Endpoints consistentes e intuitivos
- **AutenticaÃ§Ã£o/AutorizaÃ§Ã£o:** JWT, OAuth2, API Keys
- **Versionamento:** EstratÃ©gias de versionamento de API
- **DocumentaÃ§Ã£o AutomÃ¡tica:** OpenAPI/Swagger
- **Rate Limiting:** ProteÃ§Ã£o contra abuso
- **CORS:** ConfiguraÃ§Ã£o correta para frontend separado

## ðŸ’¡ Por que o SuplaStock precisa de API?

### CenÃ¡rios Futuros

#### 1. **App Mobile** ðŸ“±

```
SuplaStock Mobile App (React Native / Flutter)
â†“
REST API (Django REST Framework)
â†“
Banco de Dados PostgreSQL
```

**Funcionalidades:**

- Consultar estoque em tempo real
- Registrar vendas pelo celular
- Notificar contas a receber
- Dashboard mobile

#### 2. **Sistema de PDV FÃ­sico** ðŸ’»

```
Tablet na loja (webapp offline-first)
â†“
API para sincronizaÃ§Ã£o
â†“
Sistema central
```

#### 3. **IntegraÃ§Ãµes Externas** ðŸ”—

- IntegraÃ§Ã£o com delivery (iFood, etc)
- Marketplace (Mercado Livre, B2W)
- Gateway de pagamento (Stripe, PagSeguro)
- Sistema de nota fiscal eletrÃ´nica

#### 4. **Painel do Cliente** ðŸ‘¤

```
Portal do Cliente (React/Vue)
â†“
API pÃºblica documentada
â†“
HistÃ³rico de compras, faturas, pagamentos
```

## ðŸš€ ImplementaÃ§Ã£o com Django REST Framework

### InstalaÃ§Ã£o

```bash
pip install djangorestframework
pip install djangorestframework-simplejwt  # JWT auth
pip install drf-spectacular  # OpenAPI docs
pip install django-cors-headers  # CORS
pip install django-ratelimit  # Rate limiting
```

### ConfiguraÃ§Ã£o Base

```python
# suplastock/settings.py

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Antes do CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    # ... resto
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS (para frontend separado)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev
    "http://localhost:5173",  # Vite dev
    "https://vasuplementos.com.br",  # Production
]

# OpenAPI/Swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'SuplaStock API',
    'DESCRIPTION': 'API de gestÃ£o de vendas e estoque',
    'VERSION': '1.0.0',
}
```

### Estrutura de API

```
suplastock/
â”œâ”€â”€ api/                          # Novo app para API
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ urls.py                   # URLs da API
â”‚   â”œâ”€â”€ permissions.py            # PermissÃµes customizadas
â”‚   â”œâ”€â”€ throttles.py              # Rate limiting customizado
â”‚   â”œâ”€â”€ v1/                       # API v1
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ serializers/          # Serializers por mÃ³dulo
â”‚   â”‚   â”‚   â”œâ”€â”€ produtos.py
â”‚   â”‚   â”‚   â”œâ”€â”€ vendas.py
â”‚   â”‚   â”‚   â”œâ”€â”€ clientes.py
â”‚   â”‚   â”‚   â””â”€â”€ financeiro.py
â”‚   â”‚   â””â”€â”€ views/                # ViewSets
â”‚   â”‚       â”œâ”€â”€ produtos.py
â”‚   â”‚       â”œâ”€â”€ vendas.py
â”‚   â”‚       â”œâ”€â”€ clientes.py
â”‚   â”‚       â””â”€â”€ financeiro.py
â”‚   â””â”€â”€ v2/                       # API v2 (futuro)
```

### Exemplo: API de Produtos

```python
# api/v1/serializers/produtos.py
from rest_framework import serializers
from estoque.models import Produto, Categoria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao']

class ProdutoListSerializer(serializers.ModelSerializer):
    """Serializer para listagem (menos campos)"""
    categoria = serializers.StringRelatedField()
    
    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'categoria', 'preco_venda',
            'estoque_atual', 'ativo'
        ]

class ProdutoDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes (todos os campos)"""
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    margem_lucro_percentual = serializers.SerializerMethodField()
    status_estoque = serializers.SerializerMethodField()
    
    class Meta:
        model = Produto
        fields = '__all__'
    
    def get_margem_lucro_percentual(self, obj):
        if obj.preco_custo_unitario > 0:
            return ((obj.preco_venda - obj.preco_custo_unitario) / 
                    obj.preco_custo_unitario * 100)
        return 0
    
    def get_status_estoque(self, obj):
        if obj.estoque_atual == 0:
            return 'ESGOTADO'
        elif obj.estoque_atual <= obj.estoque_minimo:
            return 'BAIXO'
        return 'OK'

# api/v1/views/produtos.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from estoque.models import Produto
from ..serializers.produtos import ProdutoListSerializer, ProdutoDetailSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de produtos
    
    list: Listar todos os produtos
    retrieve: Detalhes de um produto
    create: Criar novo produto
    update: Atualizar produto
    partial_update: Atualizar parcialmente
    destroy: Deletar produto
    """
    queryset = Produto.objects.select_related('categoria')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'ativo', 'fornecedor']
    search_fields = ['nome', 'marca', 'fornecedor']
    ordering_fields = ['nome', 'preco_venda', 'estoque_atual', 'data_compra']
    ordering = ['-data_compra']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProdutoListSerializer
        return ProdutoDetailSerializer
    
    @action(detail=False, methods=['get'])
    def estoque_baixo(self, request):
        """Endpoint customizado: produtos com estoque baixo"""
        produtos = self.get_queryset().filter(
            estoque_atual__lte=models.F('estoque_minimo'),
            ativo=True
        )
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        """Top 10 produtos mais vendidos"""
        from django.db.models import Sum, Count
        produtos = self.get_queryset().annotate(
            total_vendido=Count('venda')
        ).order_by('-total_vendido')[:10]
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ajustar_estoque(self, request, pk=None):
        """Ajustar estoque manualmente"""
        produto = self.get_object()
        quantidade = request.data.get('quantidade')
        
        if quantidade is None:
            return Response(
                {'error': 'Campo quantidade Ã© obrigatÃ³rio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        produto.estoque_atual = quantidade
        produto.save()
        
        return Response({
            'message': 'Estoque atualizado',
            'estoque_atual': produto.estoque_atual
        })
```

### URLs da API

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .v1.views import produtos, vendas, clientes, financeiro

router = DefaultRouter()
router.register(r'produtos', produtos.ProdutoViewSet)
router.register(r'categorias', produtos.CategoriaViewSet)
router.register(r'vendas', vendas.VendaViewSet)
router.register(r'clientes', clientes.ClienteViewSet)
router.register(r'contas-receber', financeiro.ContaReceberViewSet)

urlpatterns = [
    # AutenticaÃ§Ã£o JWT
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API v1
    path('v1/', include(router.urls)),
    
    # DocumentaÃ§Ã£o OpenAPI/Swagger
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]

# suplastock/urls.py
urlpatterns = [
    # ... rotas existentes
    path('api/', include('api.urls')),
]
```

### PermissÃµes Customizadas

```python
# api/permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admins: leitura e escrita
    Outros: apenas leitura
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Apenas dono do objeto ou admin pode editar
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.usuario == request.user
```

## ðŸ“ DocumentaÃ§Ã£o AutomÃ¡tica

Acesse: `http://localhost:8000/api/docs/`

**Swagger UI** interativo com:

- Lista de todos os endpoints
- ParÃ¢metros e Request body
- Respostas de exemplo
- Tester integrado

Exemplo de requisiÃ§Ã£o documentada:

```yaml
openapi: 3.0.0
paths:
  /api/v1/produtos/:
    get:
      summary: Listar produtos
      parameters:
        - name: categoria
          in: query
          schema:
            type: integer
        - name: search
          in: query
          schema:
            type: string
      responses:
        200:
          description: Lista de produtos
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Produto'
```

## ðŸ” AutenticaÃ§Ã£o JWT

### Como usar (frontend):

```javascript
// 1. Login
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'senha' })
});

const { access, refresh } = await response.json();
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// 2. Fazer requisiÃ§Ãµes autenticadas
const produtos = await fetch('/api/v1/produtos/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

// 3. Refresh token (quando access expira)
const refreshResponse = await fetch('/api/auth/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
});

const { access: newAccess } = await refreshResponse.json();
localStorage.setItem('access_token', newAccess);
```

## ðŸ“ˆ Exemplos de Uso

### Mobile App (React Native)

```javascript
// produto.service.js
const API_URL = 'https://api.vasuplementos.com.br';

export const ProdutoService = {
  async listar(categoria = null) {
    const url = categoria 
      ? `${API_URL}/api/v1/produtos/?categoria=${categoria}`
      : `${API_URL}/api/v1/produtos/`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    return response.json();
  },
  
  async buscar(termo) {
    const response = await fetch(
      `${API_URL}/api/v1/produtos/?search=${termo}`,
      { headers: { 'Authorization': `Bearer ${getToken()}` }}
    );
    return response.json();
  },
  
  async estoqueBaixo() {
    const response = await fetch(
      `${API_URL}/api/v1/produtos/estoque_baixo/`,
      { headers: { 'Authorization': `Bearer ${getToken()}` }}
    );
    return response.json();
  }
};
```

### Painel Web (Vue.js)

```vue
<template>
  <div>
    <h1>Produtos</h1>
    <input v-model="search" @input="buscarProdutos" placeholder="Buscar...">
    
    <div v-for="produto in produtos" :key="produto.id">
      <h3>{{ produto.nome }}</h3>
      <p>R$ {{ produto.preco_venda }}</p>
      <p>Estoque: {{ produto.estoque_atual }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

export default {
  setup() {
    const produtos = ref([]);
    const search = ref('');
    
    const buscarProdutos = async () => {
      const params = search.value ? { search: search.value } : {};
      const response = await api.get('/produtos/', { params });
      produtos.value = response.data.results;
    };
    
    onMounted(() => buscarProdutos());
    
    return { produtos, search, buscarProdutos };
  }
};
</script>
```

## ðŸš€ Roadmap

### Fase 1: Base (1 semana)

- [ ] Instalar DRF e dependÃªncias
- [ ] Configurar autenticaÃ§Ã£o JWT
- [ ] Criar estrutura de API (api/ app)
- [ ] DocumentaÃ§Ã£o Swagger

### Fase 2: Endpoints Core (2 semanas)

- [ ] API de Produtos (CRUD completo)
- [ ] API de Categorias
- [ ] API de Vendas
- [ ] API de Clientes

### Fase 3: Endpoints AvanÃ§ados (1 semana)

- [ ] API Financeiro (Contas a Receber/Pagar)
- [ ] Dashboard stats
- [ ] RelatÃ³rios em CSV/Excel via API

### Fase 4: App Mobile (4-6 semanas)

- [ ] React Native / Flutter app
- [ ] Login/Auth
- [ ] Listagem e busca de produtos
- [ ] Registrar vendas
- [ ] Dashboard mobile

**Total: 2-3 meses**

## ðŸ’° ROI

- **Flexibilidade:** Qualquer frontend pode consumir
- **Mobile First:** App nativo possÃ­vel
- **IntegraÃ§Ãµes:** FÃ¡cil conectar com sistemas externos
- **Escalabilidade:** Frontend e backend independentes
- **Futuro-proof:** Arquitetura moderna

---

**Fonte:** Community
**Risco:** Baixo
**ROI:** Alto (habilita futuras expansÃµes)



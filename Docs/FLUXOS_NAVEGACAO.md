# ðŸ—ºï¸ Mapa de Fluxos de NavegaÃ§Ã£o - SuplaStock

## ðŸ“‘ Ãndice:

- [Fluxo de AutenticaÃ§Ã£o](#fluxo-de-autenticaÃ§Ã£o)
- [Fluxo de Vendas](#fluxo-de-vendas)
- [Fluxo de GestÃ£o de Estoque](#fluxo-de-gestÃ£o-de-estoque)
- [Fluxo de GestÃ£o de Clientes](#fluxo-de-gestÃ£o-de-clientes)
- [Fluxo Financeiro](#fluxo-financeiro)
- [Fluxo de RelatÃ³rios](#fluxo-de-relatÃ³rios)
- [Fluxo Administrativo](#fluxo-administrativo)

---

## ðŸ” Fluxo de AutenticaÃ§Ã£o

### Login e Acesso:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE AUTENTICAÃ‡ÃƒO                                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Login (/login/)
   â”œâ”€â†’ Credenciais Corretas â†’ Home (Acesso RÃ¡pido)
   â”‚                             â””â”€â†’ Dashboard principal
   â”‚
   â”œâ”€â†’ Credenciais Incorretas â†’ Mensagem de erro
   â”‚                              â””â”€â†’ Tenta novamente (max 5x)
   â”‚
   â”œâ”€â†’ Esqueci minha senha â†’ Recuperar Senha (/auth/recuperar-senha/)
   â”‚                           â”œâ”€â†’ Informa email
   â”‚                           â”œâ”€â†’ Recebe token por email
   â”‚                           â””â”€â†’ Resetar Senha (/auth/resetar-senha/<token>/)
   â”‚                                â”œâ”€â†’ Define nova senha
   â”‚                                â””â”€â†’ Redireciona para Login
   â”‚
   â””â”€â†’ ApÃ³s Login Bem-sucedido:
        â”œâ”€â†’ Perfil (/auth/perfil/)
        â”‚    â”œâ”€â†’ Editar dados
        â”‚    â”œâ”€â†’ Alterar senha (/auth/alterar-senha/)
        â”‚    â””â”€â†’ Ver histÃ³rico de acessos
        â”‚
        â””â”€â†’ Auditoria (/auth/auditoria/) [ADMIN ONLY]
             â”œâ”€â†’ Criar usuÃ¡rios
             â”œâ”€â†’ Editar usuÃ¡rios
             â”œâ”€â†’ Resetar senha de usuÃ¡rios
             â””â”€â†’ Deletar usuÃ¡rios
```

---

## ðŸ›’ Fluxo de Vendas

### Venda Completa (Ã€ Vista):

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE VENDA Ã€ VISTA                                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ Registrar Venda (/vendas/registrar/)
   â”‚
   â”œâ”€â†’ PASSO 1: Selecionar Cliente
   â”‚    â”œâ”€â†’ Buscar cliente existente (autocomplete)
   â”‚    â”œâ”€â†’ Consumidor Final (sem cadastro)
   â”‚    â””â”€â†’ Cadastrar novo cliente â†’ FormulÃ¡rio rÃ¡pido
   â”‚
   â”œâ”€â†’ PASSO 2: Montar Carrinho
   â”‚    â”œâ”€â†’ Buscar produto (autocomplete)
   â”‚    â”œâ”€â†’ Validar estoque disponÃ­vel
   â”‚    â”œâ”€â†’ Definir quantidade
   â”‚    â”œâ”€â†’ Adicionar ao carrinho
   â”‚    â”œâ”€â†’ Repetir para mais produtos
   â”‚    â””â”€â†’ Ver total parcial
   â”‚
   â”œâ”€â†’ PASSO 3: Finalizar Pagamento
   â”‚    â”œâ”€â†’ Revisar carrinho
   â”‚    â”œâ”€â†’ Aplicar desconto (opcional)
   â”‚    â”œâ”€â†’ Selecionar forma de pagamento:
   â”‚    â”‚    â”œâ”€â†’ Dinheiro (calcula troco)
   â”‚    â”‚    â”œâ”€â†’ CartÃ£o DÃ©bito/CrÃ©dito
   â”‚    â”‚    â”œâ”€â†’ PIX
   â”‚    â”‚    â””â”€â†’ Fiado â†’ Cria Conta a Receber
   â”‚    â””â”€â†’ Adicionar observaÃ§Ãµes
   â”‚
   â”œâ”€â†’ PASSO 4: Confirmar Venda
   â”‚    â”œâ”€â†’ Processar venda
   â”‚    â”œâ”€â†’ Atualizar estoque automaticamente
   â”‚    â”œâ”€â†’ Registrar no fluxo de caixa (se Ã  vista)
   â”‚    â””â”€â†’ Venda concluÃ­da com sucesso
   â”‚
   â””â”€â†’ PÃ“S-VENDA:
        â”œâ”€â†’ Emitir Nota Fiscal (/notas-fiscais/emitir/)
        â”‚    â”œâ”€â†’ PDF gerado automaticamente
        â”‚    â””â”€â†’ Download/ImpressÃ£o
        â”‚
        â”œâ”€â†’ Nova Venda (recomeÃ§ar fluxo)
        â””â”€â†’ Ver venda registrada â†’ GestÃ£o de Vendas
```

### Venda Fiada (Gera Conta a Receber):

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE VENDA FIADA                                         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ Contas a Receber (/contas-receber/)
   â”‚
   â””â”€â†’ Nova Venda Fiada (/contas-receber/nova-fiada/)
        â”‚
        â”œâ”€â†’ STEP 1: Selecionar Cliente
        â”‚    â”œâ”€â†’ Buscar cliente
        â”‚    â”œâ”€â†’ Ver dÃ­vidas existentes (alerta se vencidas)
        â”‚    â””â”€â†’ Verificar limite de crÃ©dito
        â”‚
        â”œâ”€â†’ STEP 2: Adicionar Produtos ao Carrinho
        â”‚    â”œâ”€â†’ Buscar produtos (autocomplete)
        â”‚    â”œâ”€â†’ Validar estoque
        â”‚    â”œâ”€â†’ Montar carrinho completo
        â”‚    â””â”€â†’ Calcular total
        â”‚
        â”œâ”€â†’ STEP 3: Definir CondiÃ§Ãµes
        â”‚    â”œâ”€â†’ Data de vencimento (padrÃ£o: 30 dias)
        â”‚    â”œâ”€â†’ Aplicar desconto (opcional)
        â”‚    â””â”€â†’ ObservaÃ§Ãµes
        â”‚
        â”œâ”€â†’ STEP 4: Confirmar
        â”‚    â”œâ”€â†’ Criar venda fiada
        â”‚    â”œâ”€â†’ Atualizar estoque
        â”‚    â”œâ”€â†’ Criar conta a receber vinculada
        â”‚    â””â”€â†’ Status: Pendente
        â”‚
        â””â”€â†’ Conta criada com sucesso
             â””â”€â†’ Ver em Contas a Receber
```

### GestÃ£o de Vendas:

```
Home â†’ GestÃ£o de Vendas (/vendas/)
   â”œâ”€â†’ Visualizar histÃ³rico completo
   â”œâ”€â†’ Filtrar vendas (perÃ­odo, cliente, status)
   â”œâ”€â†’ Ver detalhes da venda â†’ Modal com informaÃ§Ãµes completas
   â”œâ”€â†’ Editar transaÃ§Ã£o (/vendas/editar_transacao/<id>/)
   â”‚    â”œâ”€â†’ Modificar itens
   â”‚    â”œâ”€â†’ Alterar quantidades
   â”‚    â””â”€â†’ Recalcular totais e estoque
   â”œâ”€â†’ Deletar venda [ADMIN] â†’ Confirmar â†’ Estorna estoque
   â”œâ”€â†’ Emitir/Reimprimir Nota Fiscal
   â””â”€â†’ Exportar relatÃ³rio
        â”œâ”€â†’ PDF (vendas do perÃ­odo)
        â””â”€â†’ Excel (anÃ¡lise detalhada)
```

---

## ðŸ“¦ Fluxo de GestÃ£o de Estoque

### Gerenciamento de Produtos:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE GESTÃƒO DE ESTOQUE                                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ GestÃ£o de Produtos (/produtos/)
   â”‚
   â”œâ”€â†’ Visualizar catÃ¡logo completo
   â”‚    â”œâ”€â†’ Filtrar por categoria
   â”‚    â”œâ”€â†’ Filtrar por fornecedor
   â”‚    â”œâ”€â†’ Filtrar por status (Normal/Baixo/Zerado)
   â”‚    â””â”€â†’ Buscar por nome
   â”‚
   â”œâ”€â†’ Cadastrar Novo Produto (/produtos/cadastrar/)
   â”‚    â”œâ”€â†’ Preencher formulÃ¡rio:
   â”‚    â”‚    â”œâ”€â†’ Nome, categoria, fornecedor
   â”‚    â”‚    â”œâ”€â†’ Custo e preÃ§o (margem calculada auto)
   â”‚    â”‚    â”œâ”€â†’ Estoque inicial e mÃ­nimo
   â”‚    â”‚    â”œâ”€â†’ Validade, imagem, descriÃ§Ã£o
   â”‚    â”‚    â””â”€â†’ Salvar
   â”‚    â””â”€â†’ Produto cadastrado â†’ Volta para listagem
   â”‚
   â”œâ”€â†’ Editar Produto (/produtos/editar/<id>/)
   â”‚    â”œâ”€â†’ Modificar qualquer campo
   â”‚    â”œâ”€â†’ Atualizar imagem
   â”‚    â”œâ”€â†’ Ajustar estoque
   â”‚    â””â”€â†’ Salvar alteraÃ§Ãµes
   â”‚
   â”œâ”€â†’ Ver Detalhes do Produto
   â”‚    â”œâ”€â†’ InformaÃ§Ãµes completas
   â”‚    â”œâ”€â†’ HistÃ³rico de movimentaÃ§Ãµes
   â”‚    â””â”€â†’ Vendas relacionadas
   â”‚
   â”œâ”€â†’ Deletar Produto [ADMIN]
   â”‚    â”œâ”€â†’ Verificar dependÃªncias
   â”‚    â””â”€â†’ Confirmar exclusÃ£o
   â”‚
   â”œâ”€â†’ RelatÃ³rio de Estoque (/relatorios/estoque/)
   â”‚    â”œâ”€â†’ AnÃ¡lise completa do estoque
   â”‚    â”œâ”€â†’ Produtos em alerta (baixo/zerado/validade)
   â”‚    â”œâ”€â†’ Valor total em estoque
   â”‚    â”œâ”€â†’ SugestÃµes de reposiÃ§Ã£o
   â”‚    â””â”€â†’ Exportar (PDF/Excel)
   â”‚
   â””â”€â†’ ExportaÃ§Ãµes
        â”œâ”€â†’ PDF (/export/estoque/pdf/) â†’ RelatÃ³rio formatado
        â””â”€â†’ Excel (/export/estoque/excel/) â†’ Planilha completa
```

---

## ðŸ‘¥ Fluxo de GestÃ£o de Clientes

### CRUD de Clientes:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE GESTÃƒO DE CLIENTES                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ GestÃ£o de Clientes (/clientes/)
   â”‚
   â”œâ”€â†’ Listar todos os clientes
   â”‚    â”œâ”€â†’ Buscar por nome/CPF
   â”‚    â”œâ”€â†’ Filtrar por status
   â”‚    â””â”€â†’ Ordenar por compras/nome
   â”‚
   â”œâ”€â†’ Cadastrar Cliente (/clientes/cadastrar/)
   â”‚    â”œâ”€â†’ Dados pessoais (nome, CPF, telefone)
   â”‚    â”œâ”€â†’ EndereÃ§o completo
   â”‚    â”œâ”€â†’ Email e data de nascimento
   â”‚    â””â”€â†’ Salvar â†’ Cliente criado
   â”‚
   â”œâ”€â†’ Editar Cliente (/clientes/editar/<id>/)
   â”‚    â”œâ”€â†’ Atualizar dados
   â”‚    â””â”€â†’ Salvar alteraÃ§Ãµes
   â”‚
   â”œâ”€â†’ Ver Detalhes do Cliente (/clientes/detalhes/<id>/)
   â”‚    â”œâ”€â†’ Dados cadastrais completos
   â”‚    â”œâ”€â†’ HistÃ³rico de compras
   â”‚    â”œâ”€â†’ Total gasto e ticket mÃ©dio
   â”‚    â”œâ”€â†’ Contas a receber pendentes
   â”‚    â”œâ”€â†’ Produto favorito
   â”‚    â””â”€â†’ AÃ§Ãµes:
   â”‚         â”œâ”€â†’ Nova Venda
   â”‚         â”œâ”€â†’ Ver Contas a Receber
   â”‚         â””â”€â†’ Tela de CobranÃ§a
   â”‚
   â”œâ”€â†’ Deletar Cliente [ADMIN]
   â”‚    â”œâ”€â†’ Verificar vendas/contas vinculadas
   â”‚    â””â”€â†’ Confirmar exclusÃ£o
   â”‚
   â”œâ”€â†’ Tela de CobranÃ§a (/cobranca/<cliente_id>/)
   â”‚    â”œâ”€â†’ Ver todas as dÃ­vidas do cliente
   â”‚    â””â”€â†’ Registrar pagamento
   â”‚
   â”œâ”€â†’ RelatÃ³rio de Clientes (/relatorios/clientes/)
   â”‚    â”œâ”€â†’ Ranking de compradores
   â”‚    â”œâ”€â†’ AnÃ¡lise de comportamento
   â”‚    â””â”€â†’ Clientes inativos
   â”‚
   â””â”€â†’ Exportar (/export/clientes/excel/)
        â””â”€â†’ Planilha com ranking e anÃ¡lises
```

---

## ðŸ’° Fluxo Financeiro:

### Dashboard e AnÃ¡lises:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO FINANCEIRO COMPLETO                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ Dashboard Financeiro (/financeiro/)
   â”‚
   â”œâ”€â†’ Visualizar KPIs
   â”‚    â”œâ”€â†’ Faturamento total
   â”‚    â”œâ”€â†’ Lucro bruto e margem
   â”‚    â”œâ”€â†’ Ticket mÃ©dio
   â”‚    â””â”€â†’ Contas a receber
   â”‚
   â”œâ”€â†’ Analisar GrÃ¡ficos
   â”‚    â”œâ”€â†’ EvoluÃ§Ã£o de vendas
   â”‚    â”œâ”€â†’ Fluxo de caixa (entradas vs saÃ­das)
   â”‚    â”œâ”€â†’ Produtos mais vendidos
   â”‚    â”œâ”€â†’ Vendas por categoria
   â”‚    â””â”€â†’ Formas de pagamento
   â”‚
   â”œâ”€â†’ Selecionar PerÃ­odo
   â”‚    â”œâ”€â†’ Hoje/Semana/MÃªs/Ano
   â”‚    â””â”€â†’ Personalizado (data inÃ­cio/fim)
   â”‚
   â”œâ”€â†’ Comparar PerÃ­odos
   â”‚    â””â”€â†’ Ver crescimento/queda %
   â”‚
   â”œâ”€â†’ Acessar MÃ³dulos Financeiros:
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Fluxo de Caixa (/relatorios/fluxo-caixa/)
   â”‚    â”‚    â”œâ”€â†’ Ver movimentaÃ§Ãµes (entradas/saÃ­das)
   â”‚    â”‚    â”œâ”€â†’ LanÃ§ar movimentaÃ§Ã£o manual
   â”‚    â”‚    â”œâ”€â†’ Filtrar por perÃ­odo/tipo
   â”‚    â”‚    â””â”€â†’ Exportar (PDF/Excel)
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Contas a Receber (/contas-receber/)
   â”‚    â”‚    â”œâ”€â†’ Ver todas as contas pendentes
   â”‚    â”‚    â”œâ”€â†’ Filtrar por status/cliente
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Nova Conta Avulsa (/contas-receber/nova/)
   â”‚    â”‚    â”‚    â”œâ”€â†’ Cliente, valor, vencimento
   â”‚    â”‚    â”‚    â””â”€â†’ Salvar â†’ Status: Pendente
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Nova Venda Fiada (/contas-receber/nova-fiada/)
   â”‚    â”‚    â”‚    â””â”€â†’ [Ver fluxo de venda fiada acima]
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Registrar Recebimento (/contas-receber/receber/<id>/)
   â”‚    â”‚    â”‚    â”œâ”€â†’ Valor, forma de pagamento, data
   â”‚    â”‚    â”‚    â”œâ”€â†’ Parcial â†’ MantÃ©m status Pendente
   â”‚    â”‚    â”‚    â””â”€â†’ Total â†’ Status: Pago
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Ver Detalhes (/contas-receber/detalhe/<id>/)
   â”‚    â”‚    â”‚    â”œâ”€â†’ InformaÃ§Ãµes completas
   â”‚    â”‚    â”‚    â”œâ”€â†’ HistÃ³rico de pagamentos
   â”‚    â”‚    â”‚    â””â”€â†’ Dados do cliente
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Editar Conta (/contas-receber/editar/<id>/)
   â”‚    â”‚    â”‚    â””â”€â†’ Modificar valor, vencimento, descriÃ§Ã£o
   â”‚    â”‚    â”‚
   â”‚    â”‚    â”œâ”€â†’ Cancelar Conta (/contas-receber/cancelar/<id>/)
   â”‚    â”‚    â”‚    â”œâ”€â†’ Motivo do cancelamento
   â”‚    â”‚    â”‚    â””â”€â†’ Status: Cancelado
   â”‚    â”‚    â”‚
   â”‚    â”‚    â””â”€â†’ Exportar (/contas-receber/exportar/)
   â”‚    â”‚         â”œâ”€â†’ PDF (relatÃ³rio formatado)
   â”‚    â”‚         â””â”€â†’ Excel (planilha detalhada)
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Tela de CobranÃ§a (/cobranca/)
   â”‚    â”‚    â”œâ”€â†’ Ver clientes com dÃ­vidas
   â”‚    â”‚    â”œâ”€â†’ Selecionar cliente
   â”‚    â”‚    â”œâ”€â†’ Ver dÃ­vidas detalhadas
   â”‚    â”‚    â”œâ”€â†’ Registrar pagamento rÃ¡pido
   â”‚    â”‚    â””â”€â†’ Exportar lista de devedores
   â”‚    â”‚
   â”‚    â”œâ”€â†’ RelatÃ³rios Gerenciais (/financeiro/relatorios/)
   â”‚    â”‚    â”œâ”€â†’ AnÃ¡lises financeiras consolidadas
   â”‚    â”‚    â”œâ”€â†’ ProjeÃ§Ãµes
   â”‚    â”‚    â””â”€â†’ Comparativos
   â”‚    â”‚
   â”‚    â”œâ”€â†’ InadimplÃªncia (/financeiro/inadimplencia/)
   â”‚    â”‚    â”œâ”€â†’ Contas vencidas
   â”‚    â”‚    â”œâ”€â†’ Taxa de inadimplÃªncia
   â”‚    â”‚    â””â”€â†’ AÃ§Ãµes de cobranÃ§a
   â”‚    â”‚
   â”‚    â””â”€â†’ Alertas (/financeiro/alertas/)
   â”‚         â”œâ”€â†’ Vencimentos prÃ³ximos
   â”‚         â”œâ”€â†’ Estoque baixo
   â”‚         â””â”€â†’ Produtos sem movimento
   â”‚
   â””â”€â†’ Exportar Dashboard (/financeiro/exportar/)
        â””â”€â†’ PDF completo com grÃ¡ficos
```

---

## ðŸ“Š Fluxo de RelatÃ³rios:

### Central de RelatÃ³rios:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO DE RELATÃ“RIOS                                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ RelatÃ³rios (/relatorios/)
   â”‚
   â”œâ”€â†’ Resumo Operacional (/dashboard/)
   â”‚    â”œâ”€â†’ KPIs do dia/mÃªs
   â”‚    â”œâ”€â†’ Vendas recentes
   â”‚    â”œâ”€â†’ Alertas de estoque
   â”‚    â””â”€â†’ Exportar resumo (PDF/Excel)
   â”‚
   â”œâ”€â†’ RelatÃ³rios de Vendas
   â”‚    â”œâ”€â†’ Vendas por perÃ­odo
   â”‚    â”œâ”€â†’ Vendas por cliente
   â”‚    â”œâ”€â†’ Vendas por produto
   â”‚    â”œâ”€â†’ Vendas por forma de pagamento
   â”‚    â””â”€â†’ Exportar (PDF/Excel)
   â”‚
   â”œâ”€â†’ RelatÃ³rio de Estoque (/relatorios/estoque/)
   â”‚    â””â”€â†’ [Ver fluxo de estoque acima]
   â”‚
   â”œâ”€â†’ RelatÃ³rio de Clientes (/relatorios/clientes/)
   â”‚    â”œâ”€â†’ Ranking de compradores
   â”‚    â”œâ”€â†’ Ticket mÃ©dio por cliente
   â”‚    â”œâ”€â†’ FrequÃªncia de compras
   â”‚    â””â”€â†’ Exportar Excel
   â”‚
   â”œâ”€â†’ Fluxo de Caixa (/relatorios/fluxo-caixa/)
   â”‚    â””â”€â†’ [Ver fluxo financeiro acima]
   â”‚
   â””â”€â†’ RelatÃ³rios Financeiros
        â”œâ”€â†’ Dashboard Financeiro
        â”œâ”€â†’ Contas a Receber
        â””â”€â†’ AnÃ¡lise de Lucratividade
```

---

## ðŸ‘¨â€ðŸ’¼ Fluxo Administrativo:

### GestÃ£o do Sistema (Admin Only):

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ FLUXO ADMINISTRATIVO                                         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Home â†’ [Admin Menu]
   â”‚
   â”œâ”€â†’ Auditoria de UsuÃ¡rios (/auth/auditoria/)
   â”‚    â”œâ”€â†’ Listar usuÃ¡rios
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Criar UsuÃ¡rio (/auth/auditoria/usuarios/criar/)
   â”‚    â”‚    â”œâ”€â†’ Nome, email, papel, senha
   â”‚    â”‚    â””â”€â†’ Email de boas-vindas enviado
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Editar UsuÃ¡rio (/auth/auditoria/usuarios/<id>/atualizar/)
   â”‚    â”‚    â”œâ”€â†’ Modificar dados
   â”‚    â”‚    â””â”€â†’ Alterar papel/status
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Resetar Senha (/auth/auditoria/usuarios/<id>/resetar-senha/)
   â”‚    â”‚    â”œâ”€â†’ Gerar nova senha temporÃ¡ria
   â”‚    â”‚    â””â”€â†’ Enviar por email
   â”‚    â”‚
   â”‚    â”œâ”€â†’ Deletar UsuÃ¡rio (/auth/auditoria/usuarios/<id>/deletar/)
   â”‚    â”‚    â”œâ”€â†’ Validar (nÃ£o pode ser Ãºltimo admin)
   â”‚    â”‚    â””â”€â†’ Confirmar exclusÃ£o
   â”‚    â”‚
   â”‚    â””â”€â†’ Ver Logs de Auditoria
   â”‚         â””â”€â†’ HistÃ³rico de aÃ§Ãµes administrativas
   â”‚
   â”œâ”€â†’ Admin Django (/admin/)
   â”‚    â”œâ”€â†’ Gerenciar modelos
   â”‚    â”œâ”€â†’ Ver logs do Django
   â”‚    â””â”€â†’ ConfiguraÃ§Ãµes avanÃ§adas
   â”‚
   â””â”€â†’ ConfiguraÃ§Ãµes do Sistema
        â”œâ”€â†’ Categorias de produtos
        â”œâ”€â†’ Fornecedores
        â”œâ”€â†’ Formas de pagamento
        â””â”€â†’ ParÃ¢metros gerais
```

---

## ðŸŽ¯ Fluxos de Casos de Uso EspecÃ­ficos:


### Caso 1: Cliente liga para comprar e pagar depois:

```
1. Login â†’ Home
2. Contas a Receber â†’ Nova Venda Fiada
3. Buscar Cliente â†’ Verificar se tem dÃ­vidas vencidas
4. Adicionar produtos ao carrinho
5. Definir vencimento (ex: 30 dias)
6. Confirmar â†’ Venda fiada criada + Conta a receber gerada
7. Estoque atualizado automaticamente
```

### Caso 2: Cliente vem pagar dÃ­vida antiga:

```
1. Login â†’ Home
2. Tela de CobranÃ§a
3. Buscar Cliente
4. Ver todas as dÃ­vidas do cliente
5. Registrar Pagamento â†’ Valor, forma
6. Se pagar tudo â†’ Status: Pago
7. Se pagar parcial â†’ Status: Pendente (saldo atualizado)
8. Entrada registrada no Fluxo de Caixa
```

### Caso 3: Produto estÃ¡ acabando - precisa repor:

```
1. Login â†’ Home
2. GestÃ£o de Produtos ou RelatÃ³rio de Estoque
3. Ver produtos com estoque baixo (badge amarelo/vermelho)
4. Identificar fornecedor
5. Gerar lista de reposiÃ§Ã£o (exportar)
6. ApÃ³s compra: Editar Produto â†’ Atualizar estoque
```

### Caso 4: Fechar caixa do dia:

```
1. Login â†’ Home
2. Dashboard/Resumo Operacional
3. Ver vendas do dia
4. Fluxo de Caixa â†’ Ver entradas e saÃ­das
5. Conferir formas de pagamento
6. Exportar relatÃ³rio do dia (PDF)
```

### Caso 5: AnÃ¡lise mensal para decisÃµes:

```
1. Login â†’ Home
2. Dashboard Financeiro
3. Selecionar perÃ­odo: MÃªs atual
4. Analisar:
   - Faturamento vs mÃªs anterior
   - Produtos mais vendidos
   - Margem de lucro
   - Contas a receber pendentes
5. RelatÃ³rios Gerenciais â†’ AnÃ¡lises detalhadas
6. Exportar dashboard completo
```

---

## ðŸ”„ IntegraÃ§Ãµes Entre MÃ³dulos

### Como os mÃ³dulos se conectam:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   VENDAS     â”‚â”€â”€â”
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
                  â”œâ”€â”€â†’ Atualiza ESTOQUE
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   ESTOQUE    â”‚â†â”€â”¤
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
                  â”œâ”€â”€â†’ Registra em FINANCEIRO
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚    (Fluxo Caixa/Contas Receber)
â”‚  FINANCEIRO  â”‚â†â”€â”¤
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
                  â”œâ”€â”€â†’ Vincula CLIENTE
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   CLIENTES   â”‚â†â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚
       â””â”€â”€â†’ Alimenta DASHBOARD e RELATÃ“RIOS
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚  DASHBOARD   â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸ“± NavegaÃ§Ã£o RÃ¡pida (Atalhos)

### Menu Principal (Home):

```
Home (Acesso RÃ¡pido)
 â”œâ”€ Dashboard                    [/dashboard/]
 â”œâ”€ Nova Venda                   [/vendas/registrar/]
 â”œâ”€ GestÃ£o de Produtos           [/produtos/]
 â”œâ”€ GestÃ£o de Clientes           [/clientes/]
 â”œâ”€ Contas a Receber             [/contas-receber/]
 â”œâ”€ Dashboard Financeiro         [/financeiro/]
 â”œâ”€ RelatÃ³rios                   [/relatorios/]
 â”œâ”€ Perfil                       [/auth/perfil/]
 â””â”€ Auditoria [ADMIN]            [/auth/auditoria/]
```

---

## ðŸ“ Legenda de SÃ­mbolos

- `â†’` NavegaÃ§Ã£o direta
- `â”œâ”€â†’` OpÃ§Ã£o de navegaÃ§Ã£o
- `â””â”€â†’` Ãšltima opÃ§Ã£o ou resultado final
- `[ADMIN]` Acesso exclusivo para administradores
- `*` Campo obrigatÃ³rio
- `âœ“` AÃ§Ã£o completada com sucesso
- `âš ï¸` Aviso ou atenÃ§Ã£o necessÃ¡ria

---

**Ãšltima atualizaÃ§Ã£o:** 28/03/2026
**Desenvolvido por:** [Victor Alves](https://github.com/Victorkaue333)

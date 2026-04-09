# 📝 Tela: Registrar Venda

## 📍 Localização:

**URL:** `/vendas/registrar/`
**View:** `vendas.views.registrar_venda`
**Template:** `vendas/registrar_venda.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Registrar novas vendas com carrinho de produtos, controle de estoque e múltiplas formas de pagamento.

## ⚙️ Funcionalidades Principais:

### Processo Multi-Step:

#### Passo 1: Selecionar Cliente:

- **Busca de Cliente** - Autocomplete por nome/CPF/código;
- **Consumidor Final** - Opção para venda sem cadastro;
- **Novo Cliente** - Botão para cadastro rápido;
- Exibe: Nome, CPF, Telefone do cliente selecionado;

#### Passo 2: Montar Carrinho:

**Busca de Produtos:**

- Campo de busca com autocomplete;
- Exibe: Nome, Preço, Estoque disponível;

**Adicionar ao Carrinho:**

- Produto selecionado;
- **Quantidade*** - Mínimo 1, máximo = estoque;
- **Preço Unitário** - Editável (desconto individual);
- Botão "Adicionar";

**Carrinho:**
Tabela com:

- Imagem do produto (thumbnail);
- Nome;
- Quantidade (editável);
- Preço unitário;
- Subtotal;
- Botão remover;
- **Total Geral** em destaque;

#### Passo 3: Finalizar Pagamento:

**Valores:**

- **Subtotal dos Produtos** - Soma dos itens;
- **Desconto** - Campo opcional (R$ ou %);
- **Total Final** - Calculado automaticamente;

**Pagamento:**

- **Forma de Pagamento*** - Select:
  - Dinheiro;
  - Cartão de Débito;
  - Cartão de Crédito;
  - PIX;
  - Fiado (cria conta a receber);
- **Valor Pago** - Se dinheiro, calcula troco;
- **Troco** - Calculado automaticamente;
- **Observações** - Campo de texto;

**Opções:**

- ☐ Emitir Nota Fiscal após finalizar;
- ☐ Enviar comprovante por WhatsApp (futuro);

#### Passo 4: Confirmação:

- Resumo completo da venda;
- Botão "Finalizar Venda";
- Loading durante processamento;
- Mensagem de sucesso;
- Opções pós-venda:
  - Emitir Nota Fiscal;
  - Nova Venda;
  - Ver Venda Registrada;

## 🔄 Fluxo de Navegação:

```
Home → Registrar Venda
   ├─→ Selecionar Cliente
   │    ├─→ Buscar existente
   │    ├─→ Consumidor Final
   │    └─→ Cadastrar novo → Formulário rápido
   │
   ├─→ Adicionar Produtos
   │    ├─→ Buscar produto
   │    ├─→ Definir quantidade
   │    ├─→ Adicionar ao carrinho
   │    └─→ Repetir para mais produtos
   │
   ├─→ Finalizar Pagamento
   │    ├─→ Aplicar desconto (opcional)
   │    ├─→ Selecionar forma de pagamento
   │    └─→ Informar valor pago
   │
   └─→ Confirmar Venda
        ├─→ Sucesso → Ver Nota Fiscal
        └─→ Erro → Corrigir e reenviar
```

## 📋 Validações:

- ✅ Cliente deve ser selecionado;
- ✅ Carrinho deve ter ao menos 1 produto;
- ✅ Quantidade não pode exceder estoque disponível;
- ✅ Preços devem ser maiores que 0;
- ✅ Forma de pagamento deve ser selecionada;
- ✅ Se dinheiro, valor pago ≥ total;
- ✅ Estoque atualizado automaticamente ao confirmar;
- ⚠️ Aviso se aplicar desconto muito alto;

## 🎨 Layout:

- Wizard com indicador de passos (Step 1/2/3/4);
- Carrinho lateral/flutuante sempre visível;
- Autocomplete com imagens de produtos;
- Calculadora de troco em destaque;
- Botões de navegação (Voltar/Próximo/Finalizar);
- Loading spinner ao processar;
- Modal de sucesso com opções;

## 💡 Benefícios:

- ✅ Processo guiado e intuitivo;
- ✅ Validação em tempo real de estoque;
- ✅ Cálculo automático de totais e troco;
- ✅ Flexibilidade em descontos;
- ✅ Integração automática com estoque;
- ✅ Múltiplas formas de pagamento;
- ✅ Opção de venda fiada;

## 🔐 Controle de Acesso:

- Todos os usuários autenticados;
- Registra usuário que fez a venda;

## 📱 Responsividade:

- Desktop: Layout de 2 colunas (produtos + carrinho);
- Mobile: Steps sequenciais com carrinho minimizado;

## 🔗 Integrações:

- **Estoque:** Valida e atualiza automaticamente;
- **Clientes:** Busca e vincula cliente;
- **Financeiro:** Se fiado, cria conta a receber;
- **Fluxo de Caixa:** Registra entrada se à vista;
- **Nota Fiscal:** Geração opcional ao finalizar;

## ⚡ Atalhos:

- `Enter` - Adicionar produto ao carrinho (quando quantidade preenchida);
- `F2` - Focar no campo de busca de produtos;
- `F3` - Focar no campo de busca de clientes;
- `Esc` - Cancelar venda (com confirmação);

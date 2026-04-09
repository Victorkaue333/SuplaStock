# ðŸ§¾ Tela: Emitir Nota Fiscal

## ðŸ“ LocalizaÃ§Ã£o:

**URL:** `/notas-fiscais/emitir/`
**View:** `vendas.views.emitir_nota_fiscal`
**Template:** `vendas/emitir_nota_fiscal.html`
**PermissÃ£o:** UsuÃ¡rios autenticados

## ðŸŽ¯ Objetivo:

Gerar nota fiscal simplificada em PDF para vendas realizadas, com informaÃ§Ãµes da loja, cliente e produtos vendidos.

## âš™ï¸ Funcionalidades Principais:

### SeleÃ§Ã£o de Venda:

- **Buscar Venda** - Por ID da transaÃ§Ã£o ou cliente;
- Lista de vendas recentes sem nota emitida;
- Filtros por data e cliente;

### Dados da Nota Fiscal:

InformaÃ§Ãµes incluÃ­das automaticamente:

**CabeÃ§alho:**

- Logo SuplaStock;
- Nome da loja;
- CNPJ (se houver);
- EndereÃ§o completo;
- Telefone e email;
- NÃºmero sequencial da nota;
- Data e hora de emissÃ£o;

**Cliente:**

- Nome;
- CPF/CNPJ;
- EndereÃ§o;
- Telefone;

**Produtos:**

Tabela com:

- CÃ³digo;
- DescriÃ§Ã£o;
- Quantidade;
- Valor UnitÃ¡rio;
- Subtotal;

**Totais:**

- Subtotal dos produtos;
- Desconto (se houver);
- **Total da Nota**;

**Pagamento:**

- Forma de pagamento;
- Status (Pago/Pendente);

**RodapÃ©:**

- Data e hora de emissÃ£o;
- UsuÃ¡rio que emitiu;
- "Este documento nÃ£o tem valor fiscal";
- InformaÃ§Ãµes adicionais/observaÃ§Ãµes;

### GeraÃ§Ã£o do PDF:

- FormataÃ§Ã£o profissional;
- Layout limpo e legÃ­vel;
- Pronto para impressÃ£o em A4;
- Arquivo salvo no servidor;
- Download automÃ¡tico;

### ReimpressÃ£o:

- Buscar nota jÃ¡ emitida;
- Baixar PDF novamente;
- HistÃ³rico de emissÃµes;

## ðŸ”„ Fluxo de NavegaÃ§Ã£o:

```
GestÃ£o de Vendas â†’ Emitir Nota Fiscal
   â”œâ”€â†’ Selecionar Venda
   â”œâ”€â†’ Visualizar PrÃ©via
   â”œâ”€â†’ Confirmar EmissÃ£o
   â””â”€â†’ PDF Gerado
        â”œâ”€â†’ Download automÃ¡tico
        â”œâ”€â†’ Visualizar no navegador
        â””â”€â†’ Reimprimir (futuramente)

OU

Registrar Venda â†’ Finalizar â†’ [âœ“] Emitir Nota
   â””â”€â†’ PDF gerado automaticamente
```

## ðŸ“‹ ValidaÃ§Ãµes:

- âœ… Venda deve existir;
- âœ… Venda deve estar finalizada;
- âš ï¸ Aviso se nota jÃ¡ foi emitida;
- âœ… Todos os produtos devem ter dados completos;

## ðŸŽ¨ Layout do PDF:

- **CabeÃ§alho:** Logo + dados da loja;
- **NÃºmero da NF:** Destacado no topo;
- **SeÃ§Ã£o Cliente:** Box com dados;
- **Tabela de Produtos:** Clara e organizada;
- **Totais:** Destacados;
- **RodapÃ©:** InformaÃ§Ãµes legais e data;

## ðŸ’¡ BenefÃ­cios:

- âœ… FormalizaÃ§Ã£o da venda;
- âœ… Comprovante para o cliente;
- âœ… Controle de notas emitidas;
- âœ… Profissionalismo no atendimento;
- âœ… HistÃ³rico de documentos;

## ðŸ” Controle de Acesso:

- Todos os usuÃ¡rios autenticados podem emitir;
- Log de quem emitiu cada nota;
- NumeraÃ§Ã£o sequencial automÃ¡tica;

## ðŸ“± Responsividade:

- FormulÃ¡rio responsivo;
- PDF otimizado para impressÃ£o;

## ðŸ”— IntegraÃ§Ãµes:

- **Vendas:** Busca dados da transaÃ§Ã£o;
- **Clientes:** Dados cadastrais;
- **Produtos:** DescriÃ§Ã£o e valores;
- **Armazenamento:** PDF salvo no servidor;

## âš™ï¸ ConfiguraÃ§Ãµes:

- NumeraÃ§Ã£o sequencial da nota;
- Logo da loja (upload);
- Dados da loja (settings);
- Mensagem personalizada no rodapÃ©;


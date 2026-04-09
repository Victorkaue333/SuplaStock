# Auditoria Front-End e Estrutura de EstÃ¡ticos (Django)

Data da auditoria: 21/03/2026
Escopo analisado: todo o projeto Django em `suplastock/` (templates, `static/`, configuraÃ§Ã£o de `settings.py` e `base.html`).

## 1. VisÃ£o geral da estrutura atual

### 1.1 Como o CSS estÃ¡ sendo usado hoje

- Estrutura atual de estÃ¡ticos:
  - `suplastock/static/css/responsive.css` (Ãºnico arquivo CSS em `static`, com 1243 linhas).
  - NÃ£o existem arquivos CSS por app/mÃ³dulo em `static`.
- O CSS da aplicaÃ§Ã£o estÃ¡ majoritariamente dentro dos templates:
  - `18` blocos `<style>` em templates HTML.
  - `622` usos de `style=""` inline em HTML.
  - Volume estimado de CSS embutido em templates: `~110.486` caracteres.
- ConcentraÃ§Ã£o do inline style:
  - `vendas/gestao_de_vendas.html`: `202` estilos inline.
  - `financeiro/contas_receber.html`: `191`.
  - `estoque/gestao_de_produtos.html`: `172`.
  - Esses 3 templates concentram `90,84%` de todo `style=""` do projeto.

### 1.2 Como o JS estÃ¡ sendo usado hoje

- NÃ£o existe arquivo `.js` em `static/`.
- O JavaScript estÃ¡ todo inline em templates:
  - `13` scripts inline (`<script>...</script>` sem `src`).
  - Volume estimado de JS inline: `~82.781` caracteres.
  - `40` handlers inline em atributos HTML (`onclick`, `onchange`, etc.).
- ConcentraÃ§Ã£o de JS inline:
  - `vendas/emitir_nota_fiscal.html`: `~21.756` chars.
  - `financeiro/contas_receber.html`: `~20.744`.
  - `vendas/gestao_de_vendas.html`: `~18.696`.
  - `financeiro/dashboard_financeiro.html`: `~9.740`.
  - Esses 4 concentram `85,69%` do JS inline total.

### 1.3 Uso de Bootstrap (local, CDN, misto)

- Bootstrap estÃ¡ via CDN (nÃ£o local):
  - `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css`
  - `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js`
- Carregamento:
  - Em `base.html` (pÃ¡ginas que estendem base).
  - TambÃ©m em pÃ¡ginas standalone (`login`, `recuperar_senha`, `resetar_senha`) com duplicaÃ§Ã£o de include.
- HÃ¡ mistura intensa de Bootstrap com CSS customizado:
  - Sobrescritas de classes Bootstrap em CSS global e por pÃ¡gina (`.form-control`, `.modal-*`, `.btn-*`, `.table`, `.badge`, `.alert`).
  - EstratÃ©gia de override sem separaÃ§Ã£o clara entre â€œbase do frameworkâ€ e â€œtema da aplicaÃ§Ã£oâ€.

### 1.4 Inline styles, blocos `<style>` e scripts inline

- Inline styles (`style=""`): presentes em metade dos templates (`13/26`).
- Blocos `<style>`: `17/26` templates.
- Scripts inline: `12/26` templates.
- PÃ¡ginas â€œlimpasâ€ (sem inline CSS/JS): `7/26`  
  (`detalhes_cliente`, `tela_cobranca`, `relatorios/clientes`, `perfil`, `alterar_senha`, `relatorios/fluxo_caixa`, `relatorios/estoque`).

### 1.5 OrganizaÃ§Ã£o atual de manutenÃ§Ã£o

DiagnÃ³stico geral: **funciona, mas estÃ¡ frÃ¡gil para evoluÃ§Ã£o**.

- Existem duas abordagens convivendo:
  - pÃ¡ginas mais â€œBootstrap puroâ€ (relatÃ³rios simples e algumas telas de usuÃ¡rios);
  - pÃ¡ginas monolÃ­ticas com CSS+JS embutidos (vendas/estoque/financeiro).
- A pasta `static/` estÃ¡ subutilizada para JS e CSS modular.
- Forte acoplamento HTML/CSS/JS em templates longos (atÃ© 1732 linhas em uma Ãºnica pÃ¡gina).

## 2. Problemas encontrados

### 2.1 Problemas estruturais principais

1. CSS dentro de templates em grande escala

- Exemplo: `gestao_de_vendas.html`, `gestao_de_produtos.html`, `contas_receber.html`, `dashboard_financeiro.html`.
- Impacto: baixa reutilizaÃ§Ã£o, revisÃ£o difÃ­cil, diff poluÃ­do e risco de regressÃ£o visual.

2. JS espalhado e inline (sem mÃ³dulos)

- LÃ³gica de UI, busca, carrinho, modal, exportaÃ§Ã£o PDF e fetch APIs tudo no HTML.
- Impacto: baixa testabilidade, cache ineficiente, alta chance de efeito colateral entre ajustes.

3. `extra_css` implementado de forma frÃ¡gil em `base.html`

- `base.html` coloca `{% block extra_css %}` dentro de um `<style>` global.
- `9` templates filhos usam `<style>` dentro desse bloco, gerando marcaÃ§Ã£o invÃ¡lida/ambÃ­gua.
- Impacto: comportamento imprevisÃ­vel e padrÃ£o difÃ­cil de manter.

4. Acoplamento direto entre HTML e CSS por seletor de atributo de style

- HÃ¡ CSS com seletores do tipo `div[style*="..."]` em:
  - `vendas/gestao_de_vendas.html`
  - `estoque/gestao_de_produtos.html`
- Impacto: qualquer ajuste de inline style quebra regra CSS â€œindiretamenteâ€.

5. Sobrescrita ampla de classes genÃ©ricas/Bootstrap

- `responsive.css` e estilos de tela usam classes genÃ©ricas e globais (`table`, `modal`, `form-control`, `.mb-4`, etc.).
- Impacto: alto risco de regressÃ£o cruzada entre pÃ¡ginas.

6. RepetiÃ§Ã£o de cÃ³digo de estilo

- `cadastrar_produto.html` e `editar_produto.html` tÃªm bloco CSS praticamente idÃªntico (equivalÃªncia de linhas normalizadas: 100%).
- `resetar_senha.html` e `recuperar_senha.html` repetem o mesmo bloco `<style>`.
- Impacto: custo duplicado de manutenÃ§Ã£o.

7. InconsistÃªncia no padrÃ£o de injeÃ§Ã£o de JS/CSS por template

- Parte das pÃ¡ginas usa `{% block extra_js %}`, outras injetam `<script>` dentro do prÃ³prio `{% block content %}`.
- Ex.: `emitir_nota_fiscal.html`, `contas_receber.html`, `nova_conta_receber.html`.

8. DependÃªncias CDN duplicadas/inconsistentes

- `Chart.js` carregado globalmente em `base.html` e novamente em `vendas/relatorios/dashboard.html`.
- VersÃ£o fixa em um ponto (`4.4.0`) e sem versÃ£o fixa em outro (`https://cdn.jsdelivr.net/npm/chart.js`).

9. Rotas hardcoded em JS/HTML

- Ex.: `/clientes/...`, `/produtos/...`, `/contas-receber/...`, `/notas-fiscais/emitir/`.
- Impacto: quebra fÃ¡cil em refatoraÃ§Ã£o de URLConf.

10. MarcaÃ§Ã£o com fechamento de container fora do bloco de conteÃºdo em telas especÃ­ficas

- Ex.: `vendas/gestao_de_vendas.html` e `financeiro/dashboard_financeiro.html` usam fechamento de container em bloco de JS.
- Impacto: HTML invÃ¡lido/ambÃ­guo e manutenÃ§Ã£o perigosa.

### 2.2 Problemas de escalabilidade/manutenÃ§Ã£o

- Templates muito grandes:
  - `gestao_de_vendas.html` (1732 linhas)
  - `contas_receber.html` (1464)
  - `gestao_de_produtos.html` (1075)
- Falta de separaÃ§Ã£o por responsabilidade:
  - layout global + componente + regra de mÃ³dulo + regra de pÃ¡gina no mesmo arquivo.
- Falta de pipeline para frontend:
  - CI atual valida Python, mas nÃ£o hÃ¡ lint/quality gate para CSS/JS/HTML.

## 3. Estrutura recomendada para `static/`

Estrutura sugerida (adaptada ao projeto atual):

```text
suplastock/static/
  css/
    base/
      tokens.css
      reset.css
      typography.css
      layout.css
      utilities.css
      bootstrap-overrides.css
    components/
      buttons.css
      cards.css
      forms.css
      tables.css
      modals.css
      badges.css
      alerts.css
      toasts.css
    modules/
      usuarios/
        perfil.css
        alterar-senha.css
      estoque/
        gestao-produtos.css
        produto-form.css
      vendas/
        gestao-vendas.css
        gestao-clientes.css
        emitir-nota-fiscal.css
      financeiro/
        dashboard-financeiro.css
        resumo-operacional.css
        contas-receber.css
      relatorios/
        dashboard.css
        clientes.css
        estoque.css
        fluxo-caixa.css
    pages/
      auth/
        login.css
        recuperar-senha.css
        resetar-senha.css
      errors/
        errors.css
    vendor/
      bootstrap/
      fontawesome/

  js/
    base/
      app-shell.js
      api-client.js
      dom-utils.js
      formatters.js
      toast.js
    components/
      modal-manager.js
      table-filter.js
      autocomplete.js
      export-utils.js
    modules/
      estoque/
        gestao-produtos.js
        produto-form.js
      vendas/
        gestao-vendas.js
        gestao-clientes.js
        emitir-nota-fiscal.js
      financeiro/
        dashboard-financeiro.js
        contas-receber.js
        resumo-operacional.js
      usuarios/
        perfil.js
        alterar-senha.js
      relatorios/
        dashboard.js
    pages/
      auth/
        login.js
    vendor/
      chart.js
      jspdf/

  img/
    logos/
    icons/
    ui/
  fonts/
```

FunÃ§Ã£o de cada pasta:

- `css/base`: fundaÃ§Ã£o visual global (tokens, reset, tipografia, layout e utilitÃ¡rios).
- `css/components`: peÃ§as reutilizÃ¡veis (botÃµes, tabelas, cards, formulÃ¡rios etc).
- `css/modules`: estilos por domÃ­nio de negÃ³cio/app Django.
- `css/pages`: exceÃ§Ãµes de pÃ¡ginas especÃ­ficas (auth, erro).
- `css/vendor`: assets de terceiros quando a estratÃ©gia migrar de CDN para local.
- `js/base`: comportamento global (shell da aplicaÃ§Ã£o, menu lateral, utilitÃ¡rios).
- `js/components`: comportamentos compartilhados por vÃ¡rias telas.
- `js/modules`: regras JS por app/mÃ³dulo.
- `js/pages`: scripts de pÃ¡ginas isoladas.
- `js/vendor`: bibliotecas de terceiros quando localizadas.
- `img` e `fonts`: organizaÃ§Ã£o explÃ­cita de assets visuais.

## 4. EstratÃ©gia de reorganizaÃ§Ã£o (migraÃ§Ã£o em etapas)

1. Congelar baseline visual/funcional

- Registrar telas crÃ­ticas e comportamento atual (especialmente: vendas, contas a receber, estoque).

2. Ajustar a base de carregamento de assets

- Em `base.html`, retirar `{% block extra_css %}` de dentro de `<style>`.
- Definir `extra_css` para receber `<link>` e `extra_js` para receber `<script src>`.

3. Extrair o nÃºcleo global

- Mover CSS inline de `base.html` para `css/base/layout.css`.
- Mover JS do menu mobile para `js/base/app-shell.js`.

4. Criar camadas reutilizÃ¡veis

- Extrair padrÃµes repetidos para `css/components` (`cards`, `tables`, `modals`, `buttons`).

5. Atacar os templates de maior risco primeiro

- Ordem sugerida:
  1. `vendas/gestao_de_vendas.html`
  2. `financeiro/contas_receber.html`
  3. `estoque/gestao_de_produtos.html`
  4. `vendas/emitir_nota_fiscal.html`

6. Remover `style=""` gradualmente

- Substituir por classes sem alterar comportamento.
- Eliminar seletor acoplado a inline (`[style*="..."]`).

7. Modularizar JS por domÃ­nio

- Criar arquivos em `js/modules/*` para carrinho, filtros, modais, exportaÃ§Ãµes.

8. Revisar estratÃ©gia de Bootstrap

- Definir Bootstrap como â€œbaseâ€ e centralizar overrides em `css/base/bootstrap-overrides.css`.
- Evitar sobrescrever classes Bootstrap em mÃºltiplos templates.

9. Normalizar rotas front-end

- Trocar rotas hardcoded por `{% url %}` + `data-*` attributes (ou endpoint map em JS).

10. Integrar validaÃ§Ã£o no CI

- Adicionar lint para frontend (ex.: Stylelint + ESLint + checagem de templates).

## 5. ConvenÃ§Ã£o recomendada

### 5.1 Nomes de arquivos CSS

- Formato: `kebab-case`.
- Por mÃ³dulo/tela: `gestao-vendas.css`, `contas-receber.css`, `produto-form.css`.
- Componentes: `tables.css`, `modals.css`, `buttons.css`.

### 5.2 Nomes de arquivos JS

- Formato: `kebab-case`.
- Nome orientado a responsabilidade: `gestao-vendas.js`, `table-filter.js`, `modal-manager.js`.

### 5.3 OrganizaÃ§Ã£o por app

- Cada app Django deve ter seus assets principais em `css/modules/<app>/` e `js/modules/<app>/`.
- Regras especÃ­ficas de relatÃ³rio em `modules/relatorios`.

### 5.4 Quando usar global vs especÃ­fico

- **Global (`base/` e `components/`)**:
  - layout, tipografia, grid, utilitÃ¡rios, componentes compartilhados.
- **EspecÃ­fico (`modules/` ou `pages/`)**:
  - regras de negÃ³cio visual/JS de uma tela ou fluxo Ãºnico.

### 5.5 Como carregar CSS/JS no `base.html`

PadrÃ£o recomendado:

```django
{# HEAD #}
<link rel="stylesheet" href="{% static 'css/base/tokens.css' %}">
<link rel="stylesheet" href="{% static 'css/base/layout.css' %}">
<link rel="stylesheet" href="{% static 'css/components/tables.css' %}">
{% block extra_css %}{% endblock %}

{# Fim do body #}
<script src="{% static 'js/base/app-shell.js' %}" defer></script>
<script src="{% static 'js/base/dom-utils.js' %}" defer></script>
{% block extra_js %}{% endblock %}
```

### 5.6 Uso de `{% block extra_css %}` e `{% block extra_js %}`

- `extra_css`: somente `<link rel="stylesheet" ...>`.
- `extra_js`: preferencialmente `<script src="..." defer></script>`.
- Evitar `<style>` e `<script>` inline dentro de templates de tela, exceto casos pontuais e temporÃ¡rios.

## 6. Exemplo de estrutura final sugerida

```text
suplastock/
  static/
    css/
      base/
        tokens.css
        layout.css
        utilities.css
        bootstrap-overrides.css
      components/
        tables.css
        forms.css
        modals.css
        buttons.css
      modules/
        estoque/
          gestao-produtos.css
          produto-form.css
        vendas/
          gestao-vendas.css
          gestao-clientes.css
          emitir-nota-fiscal.css
        financeiro/
          dashboard-financeiro.css
          resumo-operacional.css
          contas-receber.css
        usuarios/
          perfil.css
      pages/
        auth/
          login.css
          recuperar-senha.css
          resetar-senha.css
        errors/
          errors.css
    js/
      base/
        app-shell.js
        dom-utils.js
        api-client.js
      components/
        modal-manager.js
        table-filter.js
      modules/
        estoque/
          gestao-produtos.js
          produto-form.js
        vendas/
          gestao-vendas.js
          gestao-clientes.js
          emitir-nota-fiscal.js
        financeiro/
          dashboard-financeiro.js
          contas-receber.js
      vendor/
        chart.js
        jspdf/
    img/
      logos/
      icons/
      ui/
    fonts/
```

## 7. PrÃ³ximos passos (para a refatoraÃ§Ã£o futura)

1. Aprovar esta proposta de estrutura e convenÃ§Ãµes.
2. Definir pÃ¡ginas crÃ­ticas da Fase 1 (recomendado: vendas, contas a receber, estoque).
3. Ajustar `base.html` para suportar carregamento modular correto de CSS/JS.
4. Extrair assets globais (`base.html` + `responsive.css`) para camada `base/components`.
5. Migrar as 4 telas mais pesadas para arquivos em `static/css/modules` e `static/js/modules`.
6. Eliminar inline styles e handlers inline gradualmente.
7. Padronizar carregamento de dependÃªncias (Chart.js/jspdf/Bootstrap) com versÃ£o fixa.
8. Substituir rotas hardcoded por `{% url %}` + `data-*`.
9. Adicionar validaÃ§Ã£o de frontend no CI.
10. Executar rodada final de regressÃ£o visual e responsiva antes de produÃ§Ã£o.

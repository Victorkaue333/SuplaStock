# AUDITORIA GERAL DO SISTEMA - SuplaStock

Data da auditoria: 22/03/2026
Escopo auditado: cÃ³digo-fonte Django em `suplastock/` (apps `usuarios`, `estoque`, `vendas`, `financeiro`, templates, JS, settings e pipeline CI).
MÃ©todo: revisÃ£o estÃ¡tica de cÃ³digo e templates + execuÃ§Ã£o de `python manage.py check` e `python manage.py test`.

## 1. Resumo executivo

O sistema tem uma base funcional boa para operaÃ§Ã£o diÃ¡ria, mas ainda nÃ£o estÃ¡ no nÃ­vel de robustez esperado para um ambiente profissional com maior escala de usuÃ¡rios e risco operacional.

Principais conclusÃµes:

- Existem riscos crÃ­ticos de seguranÃ§a e integridade de dados nas rotas de mutaÃ§Ã£o (controle de acesso por perfil incompleto, exclusÃµes sem `POST` obrigatÃ³rio e validaÃ§Ã£o de backend fraca para estoque/valores).
- O front-end Ã© rico visualmente, porÃ©m com alta dÃ­vida tÃ©cnica (muito inline style, JS acoplado a rotas fixas e uso de `innerHTML` com dados vindos do backend).
- O back-end concentra regras de negÃ³cio em views extensas e sem camada de validaÃ§Ã£o estruturada (`forms/services`), dificultando manutenÃ§Ã£o e testes.
- Cobertura de testes automatizados Ã© inexistente no estado atual (`Found 0 test(s)`).

Resultado rÃ¡pido por criticidade:

| Criticidade | Quantidade de achados |
|---|---:|
| Alta | 8 |
| MÃ©dia | 14 |
| Baixa | 8 |

LimitaÃ§Ãµes e transparÃªncia:

- NÃ£o foi feita execuÃ§Ã£o manual de UX em navegador com testes cross-browser/mobile reais; avaliaÃ§Ã£o de UX/UI foi baseada no cÃ³digo (HTML/CSS/JS) e estrutura das telas.
- NÃ£o foi possÃ­vel confirmar controles de infraestrutura externos ao repositÃ³rio (WAF, firewall, polÃ­ticas de hosting, monitoramento externo).

## 2. Pontos positivos

| Item positivo | EvidÃªncia |
|---|---|
| Uso consistente de ORM (reduz risco de SQL Injection clÃ¡ssico) | NÃ£o hÃ¡ uso de `raw()`, `cursor.execute` ou SQL manual nas apps auditadas |
| CSRF aplicado em formulÃ¡rios POST | FormulÃ¡rios POST com `{% csrf_token %}` em templates de `vendas`, `estoque`, `financeiro`, `usuarios` |
| Base de autenticaÃ§Ã£o customizada e papÃ©is definidos | `usuarios/models.py` (`Usuario.nivel_acesso`) e `usuarios/decorators.py` |
| ProteÃ§Ã£o contra open redirect no login | `usuarios/views.py:32-49` (`url_has_allowed_host_and_scheme`) |
| Registro de histÃ³rico de autenticaÃ§Ã£o | `usuarios/views.py:89`, `111`, `126`, `153`, `229`, `260` |
| Healthchecks disponÃ­veis | `suplastock/urls.py:37-38` (`/health/` e `/healthz/`) |
| PaginaÃ§Ã£o jÃ¡ implementada em contas a receber | `financeiro/views.py:226-229` |
| EnforcÌ§o de PostgreSQL na Railway | `suplastock/settings.py:395-403` |

## 3. Problemas de seguranÃ§a

### 3.1 Achados de alta criticidade

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o tÃ©cnica | Prioridade | Status atual (23/03/2026) |
|---|---|---|---|---|---|---|---|
| SEC-01 | Alta | `estoque/views.py:62-144`, `vendas/views.py:171-580`, `financeiro/views.py:254-798`; decorators existem em `usuarios/decorators.py:3-28` | Controle de acesso por perfil nÃ£o aplicado em operaÃ§Ãµes crÃ­ticas (somente `@login_required`) | Qualquer usuÃ¡rio autenticado pode alterar estoque, vendas, clientes e financeiro sem separaÃ§Ã£o adequada por papel | Definir matriz de autorizaÃ§Ã£o por caso de uso e aplicar `@admin_requerido`, `@vendedor_ou_admin`, `@estoquista_ou_admin` (ou `PermissionRequiredMixin`) em todas as rotas de escrita | P0 | Implementado |
| SEC-02 | Alta | `vendas/views.py:565-576`, `vendas/views.py:579-603`, `vendas/views.py:211-221`, `estoque/views.py:143-150`; `static/js/modules/vendas/gestao-clientes.js:34-37` | OperaÃ§Ãµes destrutivas sem enforcement de mÃ©todo HTTP (`POST`) e com exclusÃ£o via navegaÃ§Ã£o GET | Risco de exclusÃ£o acidental e exploraÃ§Ã£o via CSRF em aÃ§Ãµes destrutivas | Aplicar `@require_POST`, validar CSRF e padronizar exclusÃµes por formulÃ¡rio POST com confirmaÃ§Ã£o segura | P0 | Implementado |
| SEC-03 | Alta | `vendas/views.py:458-484`, `financeiro/views.py:474-539`, `estoque/views.py:85-89/115-121`; campos sem validators em `estoque/models.py`, `vendas/models.py`, `financeiro/models.py` | Falta de validaÃ§Ã£o robusta no backend para quantidade, preÃ§o e valor (incluindo negativos/zero indevidos) | ManipulaÃ§Ã£o de estoque/financeiro, fraude e corrupÃ§Ã£o de dados por requests forjadas | Implementar validaÃ§Ã£o server-side centralizada (`ModelForm`/serviÃ§os/validators), `MinValueValidator`, regras de negÃ³cio no domÃ­nio e rejeiÃ§Ã£o explÃ­cita de payload invÃ¡lido | P0 | Implementado com ressalva (ainda sem centralizaÃ§Ã£o completa em `forms/services`) |
| SEC-04 | Alta | `static/js/modules/financeiro/contas-receber.js:33-36`, `100-109`, `198-221`, `315-376`; API retorna dados brutos em `financeiro/views.py:577-595` | Uso de `innerHTML` com dados oriundos de banco sem sanitizaÃ§Ã£o (XSS armazenado/refletido) | ExecuÃ§Ã£o de script malicioso no navegador de usuÃ¡rios autenticados | Trocar para `textContent`/DOM seguro, sanitizar no backend e escapar output no front (inclusive modal de detalhes) | P0 | Parcial (sanitizaÃ§Ã£o adicionada, mas ainda hÃ¡ uso de `innerHTML`) |
| SEC-05 | Alta | `suplastock/settings.py:197`, `200`, `551` | Defaults inseguros: `SECRET_KEY` fallback fixa, `DEBUG=True` por padrÃ£o, CORS liberado com debug | Em deploy mal configurado pode expor stack trace, sessÃ£o e ampliar superfÃ­cie de ataque | Falhar startup sem `SECRET_KEY` real em produÃ§Ã£o, forÃ§ar `DEBUG=False` fora de dev e eliminar fallback permissivo de CORS | P0 | Implementado |
| SEC-06 | Alta | `vendas/templates/vendas/gestao_clientes.html:105` | String em `onclick` sem `escapejs` para nome do cliente | Vetor de XSS ao quebrar string JS com conteÃºdo malicioso de nome | Usar `|escapejs` em todos os parÃ¢metros JS vindos de template ou remover inline handlers | P1 | Implementado |

### 3.2 Achados de mÃ©dia criticidade

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o tÃ©cnica | Prioridade | Status atual (23/03/2026) |
|---|---|---|---|---|---|---|---|
| SEC-07 | MÃ©dia | `suplastock/settings.py:416` vs `usuarios/views.py:221-222` e `255-256` | PolÃ­tica de senha inconsistente (settings exige 8, views aceitam 6) | Regras divergentes e enfraquecimento de seguranÃ§a percebida | Centralizar polÃ­tica com `validate_password` do Django nas views de troca/reset | P1 | Implementado |
| SEC-08 | MÃ©dia | `usuarios/models.py:94`; `usuarios/views.py:212` | Token de recuperaÃ§Ã£o armazenado em texto puro no banco | Em vazamento de DB, tokens vÃ¡lidos podem ser usados atÃ© expiraÃ§Ã£o | Armazenar hash do token (comparaÃ§Ã£o por hash), rotaÃ§Ã£o e limpeza periÃ³dica | P2 | Implementado |
| SEC-09 | MÃ©dia | `usuarios/views.py` (login sem throttle); ausÃªncia de middleware especÃ­fico | Sem rate limit/lockout para tentativas de login | Brute force e credential stuffing mais viÃ¡veis | Adotar throttling (`django-axes`/rate limit por IP/usuÃ¡rio) e alertas | P1 | Implementado |
| SEC-10 | MÃ©dia | `estoque/views.py:75`, `129-130` | Upload de imagem sem validaÃ§Ãµes explÃ­citas (tipo, tamanho, dimensÃµes) | Upload de arquivos indevidos, consumo excessivo de storage/memÃ³ria | Validar extensÃ£o MIME, tamanho mÃ¡ximo e opcionalmente processar imagem segura | P1 | Implementado |
| SEC-11 | MÃ©dia | `financeiro/views.py:563-656` | APIs JSON e detalhe de conta expostos para qualquer usuÃ¡rio autenticado | ExposiÃ§Ã£o indevida de dados financeiros sem restriÃ§Ã£o por funÃ§Ã£o | Aplicar autorizaÃ§Ã£o por perfil e, se necessÃ¡rio, filtro por escopo de dados | P1 | Implementado com ressalva (dados sensÃ­veis restritos por perfil; escopo por proprietÃ¡rio/unidade ainda pode evoluir) |

### 3.3 Achados de baixa criticidade

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o tÃ©cnica | Prioridade | Status atual (23/03/2026) |
|---|---|---|---|---|---|---|---|
| SEC-12 | Baixa | `suplastock/templates/base.html:10-16`, `147-150`; `login.html:8-9` | DependÃªncia de CDN sem `integrity`/`crossorigin` | Risco de supply chain (baixo, mas existente) | Adicionar SRI ou servir assets crÃ­ticos internamente | P3 | Implementado |
| SEC-13 | Baixa | `vendas/views.py:302-304`, `financeiro/views.py` com `except Exception` | Tratamento de erro amplo e pouco padronizado | Dificulta resposta a incidentes e troubleshooting seguro | Padronizar exceÃ§Ãµes de domÃ­nio + logging estruturado por evento | P2 | Implementado |

## 4. Problemas de front-end

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o | Prioridade | Status atual (23/03/2026) |
|---|---|---|---|---|---|---|---|
| FE-01 | Alta | `suplastock/templates/base.html:113-116` | Mensagens Django sÃ£o consumidas e ocultadas no layout base | UsuÃ¡rio perde feedback de sucesso/erro em quase todo o sistema | Implementar componente global de toast/alert para exibir mensagens de forma consistente | P1 | Implementado |
| FE-02 | MÃ©dia | `TOTAL_INLINE_STYLE_ATTRIBUTES=595` (contagem em templates) | Excesso de estilos inline | Baixa manutenibilidade, difÃ­cil padronizaÃ§Ã£o e ajuste responsivo | Extrair para CSS modular por componente/tela | P2 | Parcial (refatoraÃ§Ã£o iniciada em pontos crÃ­ticos; limpeza completa ainda pendente) |
| FE-03 | MÃ©dia | `static/js/modules/vendas/gestao-clientes.js`, `estoque/gestao-produtos.js`, `financeiro/contas-receber.js` | Rotas hardcoded em JS | Alto acoplamento e quebra fÃ¡cil em refator de URLs | Centralizar rotas via `data-*` no template ou helper global de rotas | P2 | Implementado |
| FE-04 | MÃ©dia | `financeiro/contas-receber.js`, `vendas/gestao-clientes.js` | UX inconsistente (mistura de `alert/confirm` nativo e modais custom) | ExperiÃªncia irregular e menor percepÃ§Ã£o de qualidade | Padronizar sistema de confirmaÃ§Ã£o e erro com modais/toasts acessÃ­veis | P2 | Implementado com ressalva (fallback nativo permanece apenas quando utilitÃ¡rio global nÃ£o estiver disponÃ­vel) |
| FE-05 | MÃ©dia | `financeiro/templates/financeiro/contas_receber.html` | Acessibilidade bÃ¡sica incompleta | NavegaÃ§Ã£o por teclado/leitores de tela prejudicada | Corrigir semÃ¢ntica (button real), foco visÃ­vel e rÃ³tulos ARIA | P2 | Implementado |
| FE-06 | Baixa | `suplastock/templates/base.html` | Estrutura HTML do footer com fechamento de `div` extra | Pode causar layout inconsistente em cenÃ¡rios especÃ­ficos | Corrigir markup e validar template com lint HTML | P3 | Implementado |
| FE-07 | Baixa | `static/js/pages/auth/login.js` vazio | Arquivo Ã³rfÃ£o/sem implementaÃ§Ã£o | RuÃ­do arquitetural e confusÃ£o de manutenÃ§Ã£o | Remover arquivo ou implementar responsabilidade clara | P3 | Implementado |

## 5. Problemas de back-end

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o | Prioridade |
|---|---|---|---|---|---|---|
| BE-01 | Alta | `vendas/views.py:427-505`, `financeiro/views.py:438-558` | OperaÃ§Ãµes multi-etapa sem `transaction.atomic` e sem lock de estoque | InconsistÃªncia em falhas parciais e concorrÃªncia (oversell/estoque incorreto) | Encapsular fluxos crÃ­ticos em transaÃ§Ã£o atÃ´mica + `select_for_update`/`F()` | P0 |
| BE-02 | Alta | `estoque/views.py:33` | Filtro invÃ¡lido `fornecedor__icontains` para FK | Erro de runtime ao pesquisar produtos por fornecedor | Ajustar para `fornecedor__nome__icontains` e/ou `fornecedor_nome_legado__icontains` | P1 |
| BE-03 | MÃ©dia | `Get-ChildItem ... forms.py => NO_FORMS_PY`, `NO_SERVICES_PY`, `NO_SERIALIZERS_PY` | AusÃªncia de camada de validaÃ§Ã£o/serviÃ§os explÃ­cita | Regras espalhadas em views, baixa testabilidade | Introduzir `ModelForms` + serviÃ§os de domÃ­nio por mÃ³dulo | P1 |
| BE-04 | MÃ©dia | `vendas/views.py:329-423`, `financeiro/views.py:24-104`, `608-730` | Views extensas com agregaÃ§Ãµes e regras acopladas | ManutenÃ§Ã£o complexa e regressÃµes mais provÃ¡veis | Dividir em funÃ§Ãµes de aplicaÃ§Ã£o (query services + command services) | P2 |
| BE-05 | MÃ©dia | `python manage.py test` => `Found 0 test(s)`; `estoque/tests.py`, `vendas/tests.py`, `financeiro/tests.py`, `usuarios/tests.py` stubs | Sem cobertura de testes automatizados reais | Alto risco de regressÃ£o em produÃ§Ã£o | Implementar testes unitÃ¡rios, integraÃ§Ã£o e regressÃ£o para fluxos crÃ­ticos | P0 |
| BE-06 | MÃ©dia | `vendas/views.py:150-166` + `vendas/models.py:34-37/77-83`; template `contas_receber.html:205-207` sem prefetch | PossÃ­veis N+1 e custo desnecessÃ¡rio de queries | Queda de desempenho com crescimento de dados | `select_related/prefetch_related`, anotaÃ§Ãµes agregadas e paginaÃ§Ã£o em listagens grandes | P1 |
| BE-07 | MÃ©dia | `vendas/views.py:171-188` e `195-205` sem tratamento de integridade | Erros de unicidade (CPF/cÃ³digo) podem gerar 500 | Instabilidade e mÃ¡ experiÃªncia operacional | Validar antes de salvar e capturar `IntegrityError` com mensagem de negÃ³cio | P1 |
| BE-08 | Baixa | `financeiro/views.py:150-154` | GET de listagem com efeito colateral (atualiza status em massa) | Quebra semÃ¢ntica HTTP e possÃ­vel custo oculto | Mover atualizaÃ§Ã£o para job agendado/comando de domÃ­nio | P3 |

## 6. Problemas de arquitetura e organizaÃ§Ã£o

| ID | Criticidade | EvidÃªncia | Problema | Impacto | RecomendaÃ§Ã£o | Prioridade |
|---|---|---|---|---|---|---|
| ARQ-01 | MÃ©dia | `suplastock/settings_prod.py:63`, `70`, `98-100`; pasta `suplastock/gestao` sem app Django ativo | `settings_prod.py` desatualizado/inconsistente com arquitetura atual | Risco de deploy quebrado e divergÃªncia entre ambientes | Unificar configuraÃ§Ã£o em um Ãºnico settings por ambiente real (`base/dev/prod`) e remover referÃªncias mortas | P1 |
| ARQ-02 | MÃ©dia | `.github/workflows/ci.yml:122` e `127` (`test gestao`); execuÃ§Ã£o local mostra 0 testes | CI gera falsa sensaÃ§Ã£o de qualidade (pipeline passa sem cobertura Ãºtil) | RegressÃµes passam despercebidas | Ajustar CI para testar apps reais e impor gate mÃ­nimo de cobertura | P0 |
| ARQ-03 | MÃ©dia | Uso amplo de lÃ³gica em views e JS com HTML embutido | SeparaÃ§Ã£o de responsabilidades fraca (UI/regra/infra misturadas) | EvoluÃ§Ã£o mais cara e maior acoplamento | Definir arquitetura por camadas (view -> service -> repository/model) e componentes front reutilizÃ¡veis | P2 |
| ARQ-04 | Baixa | Duplicidade de campos legado/extrato (`cliente_nome_legado`, `fornecedor_nome_legado`) | DÃ­vida de modelo sem estratÃ©gia de descontinuaÃ§Ã£o | Complexidade de regra e consultas | Planejar migraÃ§Ã£o de dados e depreciaÃ§Ã£o controlada | P3 |

## 7. Itens faltando no sistema

| Item faltante | SituaÃ§Ã£o atual | Impacto | AÃ§Ã£o recomendada |
|---|---|---|---|
| Matriz formal de permissÃµes por perfil | NÃ£o identificada no cÃ³digo | Falhas de autorizaÃ§Ã£o e risco operacional | Documento de RBAC + testes de permissÃ£o por endpoint |
| ValidaÃ§Ã£o de domÃ­nio centralizada | NÃ£o hÃ¡ `forms.py/services.py` | Dados inconsistentes e repetiÃ§Ã£o de regra | Criar camada de validaÃ§Ã£o e serviÃ§os por app |
| Testes automatizados relevantes | `0` testes executados | RegressÃµes em produÃ§Ã£o | Testes para vendas, estoque, financeiro, autenticaÃ§Ã£o e permissÃµes |
| Auditoria de aÃ§Ãµes de negÃ³cio (CRUD crÃ­tico) | HistÃ³rico atual cobre mais autenticaÃ§Ã£o | Baixa rastreabilidade forense | Log/audit trail para criar/editar/deletar em mÃ³dulos crÃ­ticos |
| Observabilidade de erro e performance | Logging parcial | DiagnÃ³stico lento | Sentry/APM + mÃ©tricas de latÃªncia e erro por endpoint |
| PadronizaÃ§Ã£o UX de feedback | ImplementaÃ§Ã£o parcial (toasts globais e confirmaÃ§Ãµes padronizadas jÃ¡ aplicadas) | Parte dos fluxos ainda usa variaÃ§Ãµes antigas de UI | Concluir migraÃ§Ã£o para componentes Ãºnicos de loading/erro/sucesso |

## 8. Prioridades de correÃ§Ã£o

### P0 - imediato (seguranÃ§a e integridade)

1. Fechar autorizaÃ§Ã£o por perfil em todas as rotas de mutaÃ§Ã£o (`SEC-01`).
2. Bloquear mutaÃ§Ãµes via GET com `@require_POST` (`SEC-02`).
3. Corrigir validaÃ§Ãµes backend de quantidade/preÃ§o/valor e impedir negativos (`SEC-03`).
4. Sanear pontos de XSS (`SEC-04` e `SEC-06`).
5. Corrigir defaults inseguros de configuraÃ§Ã£o (`SEC-05`).
6. Implantar testes mÃ­nimos para fluxos crÃ­ticos e permissÃµes (`BE-05`, `ARQ-02`).

### P1 - curto prazo

1. Garantir atomicidade e concorrÃªncia em fluxo de venda/fiado (`BE-01`).
2. Resolver bug de busca de fornecedor (`BE-02`).
3. Corrigir inconsistÃªncia de polÃ­tica de senha (`SEC-07`).
4. Implementar rate limit de login e endurecimento de upload (`SEC-09`, `SEC-10`).
5. Corrigir N+1/performance em listagens crÃ­ticas (`BE-06`).

### P2/P3 - mÃ©dio prazo

1. Refatorar arquitetura por camadas e padronizar front-end (`BE-03`, `BE-04`, `FE-02`, `FE-03`).
2. Revisar `settings_prod.py` e simplificar estratÃ©gia de ambientes (`ARQ-01`).
3. Evoluir acessibilidade, remover artefatos Ã³rfÃ£os e limpar dÃ­vida tÃ©cnica (`FE-05`, `FE-07`, `ARQ-04`).

## 9. Checklist final de auditoria

### SeguranÃ§a

- [x] AutenticaÃ§Ã£o analisada
- [x] AutorizaÃ§Ã£o por perfil analisada
- [x] ProteÃ§Ã£o de rotas analisada
- [x] CSRF analisado
- [x] XSS analisado
- [x] SQL Injection analisado
- [x] Upload de arquivos analisado
- [x] ConfiguraÃ§Ã£o de sessÃ£o/cookies analisada
- [x] ConfiguraÃ§Ã£o de `DEBUG`/`SECRET_KEY` analisada
- [x] Risco em APIs analisado

### Front-end e UX/UI

- [x] ConsistÃªncia visual e responsividade (por cÃ³digo) analisadas
- [x] Feedback visual e mensagens analisados
- [x] FormulÃ¡rios, tabelas, filtros e modais analisados
- [x] Acessibilidade bÃ¡sica analisada

### Back-end e arquitetura

- [x] Views/models/urls revisados
- [x] ValidaÃ§Ãµes e regras de negÃ³cio revisadas
- [x] Performance e N+1 avaliados
- [x] Testes e CI avaliados
- [x] OrganizaÃ§Ã£o do projeto e escalabilidade avaliadas

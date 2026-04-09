# MELHORIAS FUTURAS E ROADMAP - SuplaStock

Data: 22/03/2026  
Base: auditoria tÃ©cnica do cÃ³digo atual em `suplastock/`.

## Objetivo deste roadmap

Organizar a evoluÃ§Ã£o do sistema para um patamar mais profissional em seguranÃ§a, manutenÃ§Ã£o, escalabilidade e experiÃªncia de uso, com prioridades realistas e esforÃ§o estimado.

## VisÃ£o por horizonte

| Horizonte | Foco principal | Resultado esperado |
|---|---|---|
| 0-30 dias | Hardening e correÃ§Ãµes crÃ­ticas | ReduÃ§Ã£o imediata de risco de seguranÃ§a e inconsistÃªncia de dados |
| 31-90 dias | Qualidade estrutural e cobertura | Menos regressÃ£o, manutenÃ§Ã£o mais previsÃ­vel |
| 90+ dias | Escala e evoluÃ§Ã£o de produto | Sistema preparado para crescimento e novos mÃ³dulos |

## 1. SeguranÃ§a futura

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Matriz RBAC formal por endpoint (admin/vendedor/estoquista) | Hoje hÃ¡ permissÃµes incompletas em rotas crÃ­ticas | Reduz acesso indevido e erro operacional | Alta | MÃ©dio |
| Padronizar mutaÃ§Ãµes com `POST` + `@require_POST` | Existem aÃ§Ãµes destrutivas sem trava de mÃ©todo | Reduz risco de CSRF e exclusÃ£o acidental | Alta | Baixo |
| Camada de validaÃ§Ã£o de domÃ­nio (quantidade/preÃ§o/valor) | Regras estÃ£o dispersas e frÃ¡geis | Integridade de dados e prevenÃ§Ã£o de fraude | Alta | MÃ©dio |
| MitigaÃ§Ã£o de brute force no login | NÃ£o hÃ¡ throttle/lockout | Menor risco de tomada de conta | Alta | Baixo |
| Token de recuperaÃ§Ã£o com hash + limpeza automÃ¡tica | Token em texto puro aumenta risco em vazamento | Menor exposiÃ§Ã£o de credenciais temporÃ¡rias | MÃ©dia | MÃ©dio |
| Fortalecer configuraÃ§Ã£o de produÃ§Ã£o (sem fallback inseguro) | Defaults permissivos podem vazar para produÃ§Ã£o | Hardening de ambiente e compliance bÃ¡sico | Alta | Baixo |
| CabeÃ§alhos de seguranÃ§a e CSP progressiva | Complementa proteÃ§Ã£o do browser | Menor superfÃ­cie para XSS/mixed content | MÃ©dia | MÃ©dio |

## 2. Melhorias de UX/UI

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Sistema Ãºnico de feedback (toast/sucesso/erro/loading) | Hoje o feedback Ã© inconsistente entre telas | OperaÃ§Ã£o mais clara e menos retrabalho do usuÃ¡rio | Alta | MÃ©dio |
| Remover `alert/confirm` nativo e padronizar modais | Fluxo visual fragmentado | ExperiÃªncia mais previsÃ­vel e profissional | MÃ©dia | Baixo |
| Reduzir inline styles e consolidar design tokens | Alto acoplamento visual em HTML | EvoluÃ§Ã£o de layout mais rÃ¡pida e consistente | MÃ©dia | Alto |
| Padronizar estados de formulÃ¡rio (erro/disabled/loading) | HÃ¡ divergÃªncias entre mÃ³dulos | Menos erro de operaÃ§Ã£o e melhor percepÃ§Ã£o de qualidade | MÃ©dia | MÃ©dio |
| Melhorar empty states e mensagens contextuais | Alguns fluxos ainda sÃ£o tÃ©cnicos/genÃ©ricos | Melhor orientaÃ§Ã£o do usuÃ¡rio final | MÃ©dia | Baixo |

## 3. Melhorias de performance

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Corrigir N+1 com `select_related/prefetch_related` | Listagens e propriedades podem gerar muitas queries | Resposta mais rÃ¡pida com base maior | Alta | MÃ©dio |
| Mover agregaÃ§Ãµes pesadas para banco (`annotate`) | SomatÃ³rios em Python escalam mal | Menor uso de CPU e latÃªncia menor | MÃ©dia | MÃ©dio |
| PaginaÃ§Ã£o em mais telas (vendas, clientes, estoque) | Algumas listagens carregam tudo | Melhor desempenho e UX em volume alto | Alta | Baixo |
| Ãndices e revisÃ£o de queries de filtros principais | Filtros devem escalar com crescimento de dados | Busca e relatÃ³rios mais estÃ¡veis | MÃ©dia | MÃ©dio |

## 4. Novas funcionalidades

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Trilhas de auditoria para operaÃ§Ãµes crÃ­ticas (CRUD) | HistÃ³rico atual foca mais autenticaÃ§Ã£o | GovernanÃ§a e investigaÃ§Ã£o de incidentes | Alta | MÃ©dio |
| AprovaÃ§Ã£o/dupla confirmaÃ§Ã£o para aÃ§Ãµes crÃ­ticas | Evita erros de exclusÃ£o/cancelamento | Menos perdas operacionais | MÃ©dia | MÃ©dio |
| HistÃ³rico de alteraÃ§Ãµes por registro (quem/quando/o que mudou) | Facilita suporte e compliance | Rastreabilidade de negÃ³cio | MÃ©dia | MÃ©dio |
| Alertas operacionais configurÃ¡veis (estoque/vencimento/atrasos) | Regras fixas podem nÃ£o atender todos cenÃ¡rios | Sistema mais aderente ao processo real | MÃ©dia | MÃ©dio |

## 5. Observabilidade e logs

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Logging estruturado com correlaÃ§Ã£o por request | Logs atuais sÃ£o Ãºteis, mas parciais | DiagnÃ³stico mais rÃ¡pido em produÃ§Ã£o | Alta | MÃ©dio |
| Monitoramento de exceÃ§Ãµes (Sentry/APM) | Erros silenciosos atrasam reaÃ§Ã£o | Menor MTTR e maior estabilidade | Alta | Baixo |
| MÃ©tricas de negÃ³cio e tÃ©cnica (latÃªncia, erro, throughput) | Sem mÃ©tricas fica difÃ­cil priorizar melhorias | DecisÃ£o orientada por dados | MÃ©dia | MÃ©dio |

## 6. Testes automatizados

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Testes de autorizaÃ§Ã£o por perfil | Problema crÃ­tico identificado | Previne regressÃµes de seguranÃ§a | Alta | MÃ©dio |
| Testes de fluxos crÃ­ticos (venda, fiado, recebimento, estoque) | Fluxos tÃªm muitas regras e integraÃ§Ã£o entre mÃ³dulos | Menor risco de quebra em produÃ§Ã£o | Alta | Alto |
| Testes de validaÃ§Ã£o de entrada (negativos, limites, formatos) | Backend hoje Ã© permissivo em pontos crÃ­ticos | Integridade de dados garantida | Alta | MÃ©dio |
| Ajuste do CI para apps reais e cobertura mÃ­nima | CI atual pode passar com pouca efetividade | Gate de qualidade confiÃ¡vel | Alta | Baixo |

## 7. RefatoraÃ§Ãµes

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Introduzir camada de serviÃ§os por domÃ­nio | Views estÃ£o â€œgordasâ€ e acopladas | CÃ³digo mais limpo e testÃ¡vel | Alta | Alto |
| Introduzir `ModelForm`/DTO de entrada | Evita parse manual de `request.POST` | ValidaÃ§Ã£o consistente e menos duplicaÃ§Ã£o | Alta | MÃ©dio |
| Remover dÃ­vida de campos legados gradualmente | Campos duplicados complicam regras | Modelo de dados mais simples e seguro | MÃ©dia | MÃ©dio |
| Padronizar tratamento de exceÃ§Ãµes de domÃ­nio | `except Exception` Ã© muito amplo | Erros previsÃ­veis e suporte facilitado | MÃ©dia | MÃ©dio |

## 8. Escalabilidade

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Lock de estoque em transaÃ§Ãµes concorrentes | Evita oversell em mÃºltiplos usuÃ¡rios | ConsistÃªncia em alta concorrÃªncia | Alta | MÃ©dio |
| Jobs assÃ­ncronos para rotinas periÃ³dicas | Evita side-effect em requisiÃ§Ãµes GET | Melhor performance e semÃ¢ntica HTTP | MÃ©dia | MÃ©dio |
| EstratÃ©gia de cache para dashboards/relatÃ³rios | RelatÃ³rios podem ficar caros com volume | Resposta estÃ¡vel em crescimento | MÃ©dia | MÃ©dio |

## 9. Melhorias no painel administrativo

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| PermissÃµes detalhadas no admin por perfil interno | Reduz risco de operaÃ§Ã£o indevida via admin | GovernanÃ§a e seguranÃ§a | MÃ©dia | MÃ©dio |
| AÃ§Ãµes administrativas auditadas | Facilita rastreio de mudanÃ§as sensÃ­veis | Compliance e investigaÃ§Ã£o | MÃ©dia | Baixo |
| Dashboards operacionais no admin | Acelera tomada de decisÃ£o tÃ©cnica | Visibilidade para suporte/gestÃ£o | Baixa | MÃ©dio |

## 10. Melhorias em relatÃ³rios, dashboards e filtros

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Filtros salvos e parÃ¢metros persistentes | UsuÃ¡rio repete filtros manualmente | Ganho operacional diÃ¡rio | MÃ©dia | MÃ©dio |
| ExportaÃ§Ãµes com limites/paginaÃ§Ã£o e auditoria | Export grande pode impactar performance | Estabilidade e rastreabilidade de dados | MÃ©dia | MÃ©dio |
| KPIs padronizados com definiÃ§Ã£o Ãºnica | MÃ©tricas podem divergir por tela | ConsistÃªncia analÃ­tica | MÃ©dia | MÃ©dio |

## 11. Melhorias em acessibilidade

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| RevisÃ£o semÃ¢ntica de botÃµes/links/div clicÃ¡vel | HÃ¡ controles que nÃ£o sÃ£o amigÃ¡veis a teclado | InclusÃ£o e conformidade bÃ¡sica | MÃ©dia | MÃ©dio |
| Foco visÃ­vel e navegaÃ§Ã£o por teclado em modais | Fluxos com modal dependem muito do mouse | Melhor usabilidade universal | MÃ©dia | Baixo |
| Rotulagem ARIA para botÃµes de Ã­cone | Facilita leitores de tela | Melhor acessibilidade sem grande impacto visual | MÃ©dia | Baixo |

## 12. Melhorias em documentaÃ§Ã£o

| Melhoria | Por que Ãºtil | BenefÃ­cio esperado | Prioridade | EsforÃ§o |
|---|---|---|---|---|
| Documento de arquitetura alvo (camadas e responsabilidades) | Hoje a regra estÃ¡ dispersa | Facilita onboard e refatoraÃ§Ã£o | Alta | Baixo |
| CatÃ¡logo de endpoints com permissÃµes esperadas | PermissÃµes atuais sÃ£o implÃ­citas | SeguranÃ§a operacional e testes direcionados | Alta | Baixo |
| Guia de padrÃµes de cÃ³digo (backend/frontend) | Evita novas divergÃªncias | EvoluÃ§Ã£o consistente entre mÃ³dulos | MÃ©dia | Baixo |
| Runbook de incidentes e rollback | PreparaÃ§Ã£o para produÃ§Ã£o robusta | Resposta rÃ¡pida em falhas | MÃ©dia | MÃ©dio |

## Roadmap recomendado (resumo de execuÃ§Ã£o)

### Fase 1 - Hardening (0-30 dias)

1. Corrigir autorizaÃ§Ã£o por perfil e enforcement de `POST`.
2. Bloquear validaÃ§Ãµes crÃ­ticas de quantidade/preÃ§o/valor no backend.
3. Corrigir vetores de XSS e padronizar saÃ­da segura no front.
4. Ajustar configuraÃ§Ã£o segura de produÃ§Ã£o (`DEBUG`, `SECRET_KEY`, CORS).
5. Criar suÃ­te mÃ­nima de testes crÃ­ticos + CI efetivo.

### Fase 2 - Qualidade estrutural (31-90 dias)

1. Introduzir `forms` e serviÃ§os por domÃ­nio.
2. Refatorar views crÃ­ticas e padronizar erros/logs.
3. Reduzir N+1, paginar listagens e otimizar relatÃ³rios.
4. Unificar UX de feedback e remover acoplamento de rotas no JS.

### Fase 3 - Escala e evoluÃ§Ã£o (90+ dias)

1. Observabilidade completa (APM, mÃ©tricas de negÃ³cio, trilhas de auditoria).
2. EvoluÃ§Ã£o de acessibilidade e padronizaÃ§Ã£o visual definitiva.
3. EstratÃ©gia de cache/jobs assÃ­ncronos para ganho de escala.
4. Limpeza de dÃ­vida legada e documentaÃ§Ã£o arquitetural viva.



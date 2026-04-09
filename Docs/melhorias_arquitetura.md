### Melhorias de arquitetura:

Criar camada Services para lógica de negócio
Adicionar paginação em todas as listagens
Usar annotations do ORM em vez de propriedades Python para evitar N+1 queries
Configurar LOGGING no settings
Expandir testes (atualmente quase zero cobertura de views/services)
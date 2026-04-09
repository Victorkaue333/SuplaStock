# Dados e Banco de Dados do SuplaStock

Esta pasta contÃ©m os arquivos de banco de dados do sistema.

## Arquivos:

- `db.sqlite3` - Banco de dados principal (SQLite);
- `db.sqlite3.backup` - Backup do banco de dados;

## Nota de SeguranÃ§a:

- Nunca commitar arquivos .sqlite3 em produÃ§Ã£o;
- Fazer backups regulares dos dados;
- Em produÃ§Ã£o, usar PostgreSQL configurado via environment variables;

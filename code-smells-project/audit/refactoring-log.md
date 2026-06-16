# Refactoring Log — code-smells-project

## [CRITICAL] Hardcoded SECRET_KEY
- Original file: app.py : 7
- Target file:   config.py
- Action: extracted
- Reason: Chave secreta removida do código e carregada via os.environ.get("SECRET_KEY") em config.py

## [CRITICAL] Endpoint de reset do banco sem autenticação
- Original file: app.py : 47-57
- Target file:   app.py (refactored)
- Action: removed
- Reason: Endpoint /admin/reset-db permitia destruição não autenticada de todos os dados

## [CRITICAL] Endpoint de execução arbitrária de SQL
- Original file: app.py : 59-78
- Target file:   app.py (refactored)
- Action: removed
- Reason: Endpoint /admin/query executava SQL arbitrário sem autenticação

## [CRITICAL] Chave secreta exposta no health check
- Original file: controllers.py : 289
- Target file:   app.py (refactored) — health_check()
- Action: fixed
- Reason: Campos secret_key, debug e db_path removidos da resposta pública do /health

## [CRITICAL] Credenciais hardcoded no seed
- Original file: database.py : 76-84
- Target file:   database.py (refactored) — _seed_data()
- Action: fixed
- Reason: Senhas hasheadas com werkzeug.security.generate_password_hash; admin password via ADMIN_PASSWORD env var

## [CRITICAL] DEBUG=True hardcoded
- Original file: app.py : 8
- Target file:   config.py
- Action: fixed
- Reason: Valor carregado de os.environ.get("DEBUG")

## [CRITICAL] SQL Injection (SELECT) — get_produto_por_id
- Original file: models.py : 28
- Target file:   models/produto.py — get_produto_por_id()
- Action: fixed
- Reason: Concatenação substituída por placeholder posicional (?)

## [CRITICAL] SQL Injection (INSERT) — criar_produto
- Original file: models.py : 47-50
- Target file:   models/produto.py — criar_produto()
- Action: fixed
- Reason: Concatenação substituída por placeholders posicionais

## [CRITICAL] SQL Injection (UPDATE) — atualizar_produto
- Original file: models.py : 57-61
- Target file:   models/produto.py — atualizar_produto()
- Action: fixed
- Reason: Concatenação substituída por placeholders posicionais

## [CRITICAL] SQL Injection (DELETE) — deletar_produto
- Original file: models.py : 68
- Target file:   models/produto.py — deletar_produto()
- Action: fixed
- Reason: Concatenação substituída por placeholder posicional

## [CRITICAL] SQL Injection (Dynamic WHERE Builder) — buscar_produtos
- Original file: models.py : 289-297
- Target file:   models/produto.py — buscar_produtos()
- Action: fixed
- Reason: WHERE builder reescrito com lista de condições e placeholders parametrizados

## [CRITICAL] Senhas retornadas nas respostas da API
- Original file: models.py : 82-86 e 95-102
- Target file:   models/usuario.py — _serialize()
- Action: fixed
- Reason: Campo "senha" removido do dicionário de serialização em _serialize()

## [CRITICAL] SQL Injection (SELECT) — get_usuario_por_id
- Original file: models.py : 92
- Target file:   models/usuario.py — get_usuario_por_id()
- Action: fixed
- Reason: Concatenação substituída por placeholder posicional

## [CRITICAL] SQL Injection (Authentication Bypass) — login_usuario
- Original file: models.py : 109-111
- Target file:   models/usuario.py — login_usuario()
- Action: fixed
- Reason: Query reescrita buscando por email com placeholder; senha verificada com check_password_hash

## [CRITICAL] SQL Injection (INSERT) — criar_usuario
- Original file: models.py : 126-129
- Target file:   models/usuario.py — criar_usuario()
- Action: fixed
- Reason: Concatenação substituída por placeholders posicionais; senha hasheada antes de armazenar

## [CRITICAL] SQL Injection (SELECT) — criar_pedido
- Original file: models.py : 140, 155
- Target file:   models/pedido.py — criar_pedido()
- Action: fixed
- Reason: Concatenações substituídas por placeholders posicionais

## [CRITICAL] SQL Injection (INSERT/UPDATE) — criar_pedido (itens e estoque)
- Original file: models.py : 148-165
- Target file:   models/pedido.py — criar_pedido()
- Action: fixed
- Reason: Todas as concatenações substituídas por placeholders posicionais

## [CRITICAL] SQL Injection (SELECT) — get_pedidos_usuario
- Original file: models.py : 174
- Target file:   models/pedido.py — get_pedidos_usuario()
- Action: fixed
- Reason: Concatenação substituída por placeholder posicional

## [CRITICAL] SQL Injection (UPDATE) — atualizar_status_pedido
- Original file: models.py : 279-281
- Target file:   models/pedido.py — atualizar_status_pedido()
- Action: fixed
- Reason: Concatenação substituída por placeholders posicionais

## [HIGH] Lógica de notificações no controller
- Original file: controllers.py : 208-210, 248-250
- Target file:   services/notifications.py
- Action: extracted
- Reason: Side effects de notificação movidos para services/notifications.py; controller delega via chamada de serviço

## [HIGH] Estado global mutável (db_connection)
- Original file: database.py : 4
- Target file:   database.py (refactored)
- Action: fixed
- Reason: Singleton global substituído por flask.g com close_db() via teardown_appcontext

## [HIGH] Regra de desconto na camada de dados
- Original file: models.py : 256-263
- Target file:   services/relatorio_service.py — calcular_desconto()
- Action: extracted
- Reason: Lógica de desconto movida para camada de serviço; model retorna apenas dados brutos via relatorio_dados_brutos()

## [MEDIUM] N+1 queries em get_pedidos_usuario
- Original file: models.py : 187-199
- Target file:   models/pedido.py — get_pedidos_usuario()
- Action: fixed
- Reason: Loops aninhados com 3 cursores substituídos por única query com LEFT JOIN

## [MEDIUM] N+1 queries em get_todos_pedidos
- Original file: models.py : 219-232
- Target file:   models/pedido.py — get_todos_pedidos()
- Action: fixed
- Reason: Loops aninhados com 3 cursores substituídos por única query com LEFT JOIN; helper _aggregate_pedidos() compartilhado

## [MEDIUM] Validação duplicada em criar_produto / atualizar_produto
- Original file: controllers.py : 30-54 e 72-80
- Target file:   controllers/produtos.py — _validar_dados_produto()
- Action: extracted
- Reason: Helper privado _validar_dados_produto() centraliza todas as regras de validação

## [LOW] Lista de categorias como magic string
- Original file: controllers.py : 52
- Target file:   models/produto.py — CATEGORIAS_VALIDAS
- Action: extracted
- Reason: Lista definida como constante nomeada no modelo e importada pelo controller

## [LOW] Magic numbers nas faixas de desconto
- Original file: models.py : 257-262
- Target file:   services/relatorio_service.py
- Action: fixed
- Reason: Literais numéricos substituídos por constantes nomeadas DESCONTO_*_LIMITE e DESCONTO_*_TAXA

## [LOW] print() como logging
- Original file: controllers.py : múltiplas linhas
- Target file:   controllers/*.py e services/notifications.py
- Action: fixed
- Reason: Todos os print() substituídos por logger.info() / logger.error() / logger.warning()

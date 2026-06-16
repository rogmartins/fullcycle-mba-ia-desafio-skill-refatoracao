# Refactoring Log — task-manager-api

## [CRITICAL] Hardcoded Secret Key
- Original file: app.py : line 13
- Target file:   config.py
- Action: extracted
- Reason: SECRET_KEY movido para variável de ambiente via config.py + python-dotenv

## [CRITICAL] Hardcoded Email Password
- Original file: services/notification_service.py : line 10
- Target file:   services/notification_service.py (atualizado) + config.py
- Action: fixed
- Reason: EMAIL_PASSWORD e demais configurações SMTP carregadas de variáveis de ambiente

## [CRITICAL] MD5 para Hash de Senhas
- Original file: models/user.py : line 29
- Target file:   models/user.py (atualizado)
- Action: fixed
- Reason: hashlib.md5 substituído por werkzeug.security.generate_password_hash (pbkdf2_sha256 com salt)

## [HIGH] Exposição do Hash de Senha na API
- Original file: models/user.py : line 22
- Target file:   models/user.py (atualizado)
- Action: fixed
- Reason: campo 'password' removido do retorno de to_dict()

## [HIGH] Token JWT Falso no Login
- Original file: routes/user_routes.py : line 210
- Target file:   routes/user_routes.py (atualizado)
- Action: fixed
- Reason: 'fake-jwt-token-{id}' substituído por jwt.encode() com PyJWT, assinado com SECRET_KEY e exp claim

## [HIGH] Lógica de Negócio em Route Handler (task_routes)
- Original file: routes/task_routes.py : lines 30-58
- Target file:   routes/task_routes.py (atualizado)
- Action: fixed
- Reason: lógica de overdue delegada a Task.is_overdue(); N+1 eliminado via joinedload

## [HIGH] Lógica de Negócio em Route Handler (report_routes)
- Original file: routes/report_routes.py : lines 54-68
- Target file:   services/report_service.py (novo)
- Action: extracted
- Reason: lógica de produtividade e relatório extraída para ReportService; rotas apenas orquestram

## [MEDIUM] N+1 Queries em get_tasks
- Original file: routes/task_routes.py : lines 41-57
- Target file:   routes/task_routes.py (atualizado)
- Action: fixed
- Reason: joinedload(Task.user, Task.category) carrega relacionamentos em uma única query

## [MEDIUM] N+1 Queries em summary_report
- Original file: routes/report_routes.py : lines 54-68
- Target file:   services/report_service.py (novo)
- Action: fixed
- Reason: joinedload(User.tasks) substitui Task.query.filter_by() dentro do loop de usuários

## [MEDIUM] Lógica de Overdue Duplicada em 4 Locais
- Original file: routes/task_routes.py:30, routes/task_routes.py:71, routes/user_routes.py:171, routes/report_routes.py:33
- Target file:   models/task.py (Task.is_overdue() já existia)
- Action: fixed
- Reason: todas as ocorrências substituídas por t.is_overdue() — ponto único de verdade no Model

## [MEDIUM] Validação de Email Duplicada
- Original file: routes/user_routes.py : lines 61, 106
- Target file:   routes/user_routes.py (atualizado)
- Action: fixed
- Reason: regex inline substituída por validate_email() de utils/helpers.py em ambas as ocorrências

## [LOW] Função process_task_data Nunca Utilizada
- Original file: utils/helpers.py : lines 57-108
- Target file:   utils/helpers.py (atualizado)
- Action: removed
- Reason: código morto removido; constantes e funções úteis mantidas

## [LOW] Uso de type() em Vez de isinstance()
- Original file: routes/task_routes.py : lines 141, 210
- Target file:   routes/task_routes.py (atualizado)
- Action: fixed
- Reason: isinstance(tags, list) substitui type(tags) == list em create_task e update_task

## [LOW] Números Mágicos para Limites de Validação
- Original file: routes/task_routes.py:96-100, routes/user_routes.py:64
- Target file:   routes/task_routes.py e routes/user_routes.py (atualizados)
- Action: fixed
- Reason: MIN_TITLE_LENGTH, MAX_TITLE_LENGTH, DEFAULT_PRIORITY, VALID_STATUSES, VALID_ROLES, MIN_PASSWORD_LENGTH importados de utils/helpers.py

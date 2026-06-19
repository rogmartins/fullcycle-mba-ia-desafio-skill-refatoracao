# Audit Report — task-manager-api

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (SQLAlchemy)
Files:   11 analyzed | ~1158 lines of code

Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 5 | LOW: 4

Findings

[CRITICAL] Hardcoded SECRET_KEY
File: app.py:13
Description: SECRET_KEY definida diretamente no código ('super-secret-key-123').
Impact:      Segredo versionado permite forjar tokens/sessões assinados pela
             aplicação.
Recommendation: Ler SECRET_KEY de variável de ambiente.

[CRITICAL] Credenciais SMTP hardcoded
File: services/notification_service.py:9
Description: Usuário e senha do servidor de email estão escritos no código
             (email_user/email_password='senha123').
Impact:      Credenciais de envio de email expostas no repositório, permitindo
             uso indevido da conta de email.
Recommendation: Ler host/porta/usuário/senha de variáveis de ambiente.

[CRITICAL] Hash de senha fraco (MD5 sem sal)
File: models/user.py:29
Description: set_password usa MD5 sem sal para guardar a senha.
Impact:      MD5 é facilmente revertível por dicionário/rainbow tables; as senhas
             ficam praticamente desprotegidas.
Recommendation: Usar hash com sal (werkzeug generate_password_hash / bcrypt).

[CRITICAL] Hash de senha exposto nas respostas
File: models/user.py:21
Description: User.to_dict inclui o campo password, vazando o hash em GET
             /users/<id>, /login e POST /users.
Impact:      O hash de senha é entregue a qualquer cliente, facilitando ataques
             offline para recuperar a senha.
Recommendation: Remover password de toda serialização da entidade User.

[HIGH] Consultas N+1 na listagem de tasks e no relatório
File: routes/task_routes.py:41
Description: GET /tasks faz uma query de User e outra de Category por task; o
             relatório de resumo consulta tasks por usuário em laço
             (report_routes.py:55).
Impact:      O número de queries cresce com o volume de dados, degradando a
             performance.
Recommendation: Usar eager loading (joinedload) e/ou agregação em uma consulta.

[HIGH] Lógica de negócio duplicada e fora do model
File: routes/task_routes.py:30
Description: O cálculo de "overdue" é reescrito em várias rotas
             (task_routes, user_routes, report_routes), enquanto o método
             Task.is_overdue() existe e é ignorado.
Impact:      Regra de negócio espalhada e duplicada diverge facilmente e dificulta
             a manutenção.
Recommendation: Centralizar a regra no model/serializer e reutilizar.

[HIGH] Debug habilitado de forma fixa
File: app.py:34
Description: app.run(debug=True) fixo no código.
Impact:      O debugger interativo do Flask em produção expõe stack traces e
             execução de código.
Recommendation: Controlar debug por variável de ambiente, desligado por padrão.

[HIGH] Regras nas rotas sem usar a camada de serviço
File: routes/task_routes.py:11
Description: As rotas concentram validação, regra e serialização; a camada
             services existe (NotificationService) mas nunca é instanciada/usada.
Impact:      Controllers "gordos" impedem reuso e teste isolado da regra de
             negócio.
Recommendation: Mover a lógica para services e deixar as rotas finas.

[MEDIUM] Cláusulas except genéricas engolindo erros
File: routes/task_routes.py:62
Description: Vários blocos usam `except:` sem capturar/logar a exceção.
Impact:      Falhas silenciosas escondem a causa real e dificultam o diagnóstico.
Recommendation: Capturar Exception, logar e responder de forma consistente.

[MEDIUM] Serialização duplicada (dict manual em vez de to_dict)
File: routes/task_routes.py:17
Description: GET /tasks e GET /users/<id>/tasks remontam o dicionário da task à
             mão em vez de usar Task.to_dict.
Impact:      Duplicação de serialização propensa a divergir do model.
Recommendation: Centralizar a serialização em funções/serializers reutilizáveis.

[MEDIUM] Validação duplicada e utilitário não utilizado
File: utils/helpers.py:57
Description: process_task_data (validação completa de task) existe em helpers mas
             não é usada; as rotas reimplementam a validação.
Impact:      Duas fontes de verdade para validação que tendem a divergir.
Recommendation: Usar uma única função/serviço de validação.

[MEDIUM] print() usado como logging
File: routes/task_routes.py:149
Description: Eventos e erros são registrados com print em várias rotas.
Impact:      Logging não estruturado, sem níveis nem destino configurável.
Recommendation: Usar o módulo logging.

[MEDIUM] Regex de email e constantes duplicadas
File: routes/user_routes.py:61
Description: A validação de email é feita por regex inline, duplicando
             utils.validate_email; constantes VALID_* de helpers não são usadas.
Impact:      Regras repetidas em pontos diferentes divergem com facilidade.
Recommendation: Centralizar validação e constantes e reutilizar.

[LOW] Imports não usados e código morto
File: utils/helpers.py:3
Description: helpers importa os/sys/json/math/hashlib sem uso e define funções
             nunca chamadas (generate_id, sanitize_string, log_action, etc.).
Impact:      Ruído que dificulta a leitura e a manutenção.
Recommendation: Remover imports e funções não utilizados.

[LOW] Números e strings mágicos repetidos
File: routes/task_routes.py:110
Description: Listas de status, faixa de prioridade (1-5) e roles aparecem
             repetidas em várias rotas.
Impact:      Valores mágicos espalhados dificultam evolução das regras.
Recommendation: Centralizar em constantes nomeadas.

[LOW] Métodos booleanos verbosos
File: models/user.py:34
Description: is_admin e Task.validate_status/validate_priority usam if/else para
             retornar booleanos.
Impact:      Verbosidade desnecessária.
Recommendation: Retornar diretamente a expressão booleana.

[LOW] Imports utilitários não utilizados no relatório
File: routes/report_routes.py:7
Description: format_date e calculate_percentage são importados mas nunca usados.
Impact:      Código morto.
Recommendation: Remover imports não utilizados.

================================
Total: 17 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

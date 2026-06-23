# Architecture Audit Report — Project 3

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   11 analyzed | ~900 lines of code

Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Credencial de acesso exposta no código-fonte
File: app.py:13
Description: SECRET_KEY definida como literal 'super-secret-key-123' diretamente no
           código-fonte versionado.
Impact:  Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão
           Flask, assumindo qualquer identidade de usuário.
Recommendation: Mover para variável de ambiente via os.environ.get('SECRET_KEY') e
              bloquear inicialização se ausente em produção.

[CRITICAL] Credenciais de e-mail hardcoded no serviço de notificação
File: services/notification_service.py:9-10
Description: Usuário SMTP 'taskmanager@gmail.com' e senha 'senha123' definidos como
           atributos da classe, presentes no repositório.
Impact:  Credenciais expostas permitem uso indevido da conta de e-mail e violam
           políticas de segurança de dados.
Recommendation: Ler host, porta, usuário e senha de variáveis de ambiente;
              nunca versionar credenciais reais.

[CRITICAL] Hash de senha usando MD5 — algoritmo criptograficamente quebrado
File: models/user.py:29
Description: Senhas armazenadas com hashlib.md5 sem sal, algoritmo projetado para
           velocidade e não para armazenamento seguro de senhas.
Impact:  Banco de dados comprometido expõe todas as senhas em segundos via tabelas
           rainbow ou força bruta com GPUs modernas.
Recommendation: Substituir por hashlib.pbkdf2_hmac com sal aleatório de 16 bytes
              e ≥100.000 iterações, ou flask-bcrypt.

[HIGH] Senha exposta em respostas da API
File: models/user.py:to_dict() → routes/user_routes.py:get_user()
Description: O método to_dict() serializa o campo password; GET /users/<id> retorna
           o hash da senha no corpo da resposta JSON.
Impact:  Qualquer cliente autenticado pode obter hashes de outros usuários via
           chamada de API, facilitando ataques offline.
Recommendation: Remover o campo password do to_dict(); nunca retornar hash em
              resposta de API.

[HIGH] Token de autenticação previsível (pseudo-JWT)
File: routes/user_routes.py:210
Description: Login retorna 'fake-jwt-token-' + str(user.id) como token de sessão,
           valor previsível e sem assinatura criptográfica.
Impact:  Atacante pode adivinhar o token de qualquer usuário conhecendo apenas
           seu ID, contornando toda a autenticação da API.
Recommendation: Substituir por secrets.token_hex(32) assinado com a SECRET_KEY
              ou PyJWT com expiração definida.

[HIGH] CRUD de categorias misturado no blueprint de relatórios
File: routes/report_routes.py
Description: Endpoints de criação, leitura, atualização e remoção de categorias estão
           definidos dentro do blueprint de relatórios, que deveria tratar apenas
           consultas analíticas.
Impact:  Viola o princípio de responsabilidade única; dificulta testes isolados,
           reutilização e manutenção futura das rotas de categorias.
Recommendation: Extrair o CRUD de categorias para routes/category_routes.py com
              blueprint próprio registrado em app.py.

[HIGH] Lógica de validação duplicada entre rotas e utils
File: routes/task_routes.py, routes/user_routes.py, utils/helpers.py
Description: Validação de status e prioridade de tasks está replicada em
           task_routes.py (create e update), em models/task.py (validate_status,
           validate_priority) e em utils/helpers.py (process_task_data).
Impact:  Mudança em regra de negócio exige atualização em múltiplos locais;
           qualquer dessincronização introduz bugs silenciosos.
Recommendation: Centralizar toda validação nos métodos do modelo Task; remover
              duplicatas em rotas e utils.

[MEDIUM] Consultas N+1 em listagem de tasks
File: routes/task_routes.py:42
Description: Para cada task retornada, o código executa queries separadas para buscar
           User.query.get(t.user_id) e Category.query.get(t.category_id), gerando
           2N+1 consultas ao banco para N tasks.
Impact:  Em listas com dezenas de tasks, o tempo de resposta cresce linearmente
           com o número de registros, degradando performance sob carga.
Recommendation: Usar joinedload do SQLAlchemy: Task.query.options(
              joinedload(Task.user), joinedload(Task.category)).all()

[MEDIUM] Consultas N+1 em relatório de resumo
File: routes/report_routes.py:56
Description: summary_report() carrega todos os usuários e, para cada um, executa
           Task.query.filter_by(user_id=u.id).all() em loop, gerando N+1 consultas.
Impact:  Com muitos usuários, o relatório torna-se progressivamente mais lento,
           podendo causar timeouts em ambientes de produção.
Recommendation: Substituir por query única com JOIN e GROUP BY para agregar contagens
              no banco em uma única roundtrip ao banco de dados.

[MEDIUM] Uso de API deprecada datetime.utcnow()
File: models/task.py:15-16, services/notification_service.py:36,
         utils/helpers.py:38
Description: datetime.utcnow() foi depreciado no Python 3.12 — não retorna objeto
           timezone-aware, podendo causar comportamento indefinido em comparações.
Impact:  Código incompatível com Python ≥3.12; comparações de datas sem timezone
           produzem resultados incorretos ao misturar com objetos aware.
Recommendation: Substituir por datetime.now(timezone.utc) em todos os arquivos
              afetados, importando from datetime import datetime, timezone.

[LOW] Lógica de overdue duplicada em múltiplas rotas
File: routes/task_routes.py, routes/user_routes.py, routes/report_routes.py
Description: Verificação de task atrasada está replicada inline em pelo menos três
           funções de rota, ignorando o método task.is_overdue() já definido no
           modelo Task.
Impact:  Código redundante aumenta superfície de erro; mudança na regra exige
           atualização em cada ocorrência.
Recommendation: Remover lógica inline; chamar task.is_overdue() em todos os pontos.

[LOW] Imports não utilizados em helpers.py
File: utils/helpers.py:1-7
Description: Módulos os, json, sys, math e hashlib são importados mas não utilizados
           em nenhuma função do arquivo.
Impact:  Imports desnecessários aumentam tempo de carga do módulo e geram confusão
           sobre dependências reais.
Recommendation: Remover imports não utilizados; manter apenas datetime e re.

[LOW] Constantes de domínio duplicadas entre model e utils
File: utils/helpers.py:110-116
Description: VALID_STATUSES, MAX_TITLE_LENGTH, MIN_TITLE_LENGTH e outras constantes
           de domínio de Task estão definidas em utils/helpers.py, separadas do
           modelo ao qual pertencem.
Impact:  Fonte única da verdade fragmentada; risco de dessincronização entre
           constantes do modelo e do helper.
Recommendation: Mover todas as constantes de domínio de Task para models/task.py;
              importar de lá onde necessário.

================================
Total: 13 findings
================================
```

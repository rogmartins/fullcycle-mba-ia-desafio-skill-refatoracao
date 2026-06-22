# Relatório de Auditoria de Arquitetura — Projeto 3

```
================================
RELATÓRIO DE AUDITORIA DE ARQUITETURA
================================
Projeto: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Arquivos: 11 analisados | ~900 linhas de código

Resumo
CRÍTICO: 3 | ALTO: 4 | MÉDIO: 3 | BAIXO: 3

Achados

[CRÍTICO] Credencial de acesso exposta no código-fonte
Arquivo: app.py:13
Descrição: SECRET_KEY definida como literal 'super-secret-key-123' diretamente no
           código-fonte versionado.
Impacto:  Qualquer pessoa com acesso ao repositório pode forjar tokens de sessão
           Flask, assumindo qualquer identidade de usuário.
Recomendação: Mover para variável de ambiente via os.environ.get('SECRET_KEY') e
              bloquear inicialização se ausente em produção.

[CRÍTICO] Credenciais de e-mail hardcoded no serviço de notificação
Arquivo: services/notification_service.py:9-10
Descrição: Usuário SMTP 'taskmanager@gmail.com' e senha 'senha123' definidos como
           atributos da classe, presentes no repositório.
Impacto:  Credenciais expostas permitem uso indevido da conta de e-mail e violam
           políticas de segurança de dados.
Recomendação: Ler host, porta, usuário e senha de variáveis de ambiente;
              nunca versionar credenciais reais.

[CRÍTICO] Hash de senha usando MD5 — algoritmo criptograficamente quebrado
Arquivo: models/user.py:29
Descrição: Senhas armazenadas com hashlib.md5 sem sal, algoritmo projetado para
           velocidade e não para armazenamento seguro de senhas.
Impacto:  Banco de dados comprometido expõe todas as senhas em segundos via tabelas
           rainbow ou força bruta com GPUs modernas.
Recomendação: Substituir por hashlib.pbkdf2_hmac com sal aleatório de 16 bytes
              e ≥100.000 iterações, ou flask-bcrypt.

[ALTO] Senha exposta em respostas da API
Arquivo: models/user.py:to_dict() → routes/user_routes.py:get_user()
Descrição: O método to_dict() serializa o campo password; GET /users/<id> retorna
           o hash da senha no corpo da resposta JSON.
Impacto:  Qualquer cliente autenticado pode obter hashes de outros usuários via
           chamada de API, facilitando ataques offline.
Recomendação: Remover o campo password do to_dict(); nunca retornar hash em
              resposta de API.

[ALTO] Token de autenticação previsível (pseudo-JWT)
Arquivo: routes/user_routes.py:210
Descrição: Login retorna 'fake-jwt-token-' + str(user.id) como token de sessão,
           valor previsível e sem assinatura criptográfica.
Impacto:  Atacante pode adivinhar o token de qualquer usuário conhecendo apenas
           seu ID, contornando toda a autenticação da API.
Recomendação: Substituir por secrets.token_hex(32) assinado com a SECRET_KEY
              ou PyJWT com expiração definida.

[ALTO] CRUD de categorias misturado no blueprint de relatórios
Arquivo: routes/report_routes.py
Descrição: Endpoints de criação, leitura, atualização e remoção de categorias estão
           definidos dentro do blueprint de relatórios, que deveria tratar apenas
           consultas analíticas.
Impacto:  Viola o princípio de responsabilidade única; dificulta testes isolados,
           reutilização e manutenção futura das rotas de categorias.
Recomendação: Extrair o CRUD de categorias para routes/category_routes.py com
              blueprint próprio registrado em app.py.

[ALTO] Lógica de validação duplicada entre rotas e utils
Arquivo: routes/task_routes.py, routes/user_routes.py, utils/helpers.py
Descrição: Validação de status e prioridade de tasks está replicada em
           task_routes.py (create e update), em models/task.py (validate_status,
           validate_priority) e em utils/helpers.py (process_task_data).
Impacto:  Mudança em regra de negócio exige atualização em múltiplos locais;
           qualquer dessincronização introduz bugs silenciosos.
Recomendação: Centralizar toda validação nos métodos do modelo Task; remover
              duplicatas em rotas e utils.

[MÉDIO] Consultas N+1 em listagem de tasks
Arquivo: routes/task_routes.py:42
Descrição: Para cada task retornada, o código executa queries separadas para buscar
           User.query.get(t.user_id) e Category.query.get(t.category_id), gerando
           2N+1 consultas ao banco para N tasks.
Impacto:  Em listas com dezenas de tasks, o tempo de resposta cresce linearmente
           com o número de registros, degradando performance sob carga.
Recomendação: Usar joinedload do SQLAlchemy: Task.query.options(
              joinedload(Task.user), joinedload(Task.category)).all()

[MÉDIO] Consultas N+1 em relatório de resumo
Arquivo: routes/report_routes.py:56
Descrição: summary_report() carrega todos os usuários e, para cada um, executa
           Task.query.filter_by(user_id=u.id).all() em loop, gerando N+1 consultas.
Impacto:  Com muitos usuários, o relatório torna-se progressivamente mais lento,
           podendo causar timeouts em ambientes de produção.
Recomendação: Substituir por query única com JOIN e GROUP BY para agregar contagens
              no banco em uma única roundtrip ao banco de dados.

[MÉDIO] Uso de API deprecada datetime.utcnow()
Arquivo: models/task.py:15-16, services/notification_service.py:36,
         utils/helpers.py:38
Descrição: datetime.utcnow() foi depreciado no Python 3.12 — não retorna objeto
           timezone-aware, podendo causar comportamento indefinido em comparações.
Impacto:  Código incompatível com Python ≥3.12; comparações de datas sem timezone
           produzem resultados incorretos ao misturar com objetos aware.
Recomendação: Substituir por datetime.now(timezone.utc) em todos os arquivos
              afetados, importando from datetime import datetime, timezone.

[BAIXO] Lógica de overdue duplicada em múltiplas rotas
Arquivo: routes/task_routes.py, routes/user_routes.py, routes/report_routes.py
Descrição: Verificação de task atrasada está replicada inline em pelo menos três
           funções de rota, ignorando o método task.is_overdue() já definido no
           modelo Task.
Impacto:  Código redundante aumenta superfície de erro; mudança na regra exige
           atualização em cada ocorrência.
Recomendação: Remover lógica inline; chamar task.is_overdue() em todos os pontos.

[BAIXO] Imports não utilizados em helpers.py
Arquivo: utils/helpers.py:1-7
Descrição: Módulos os, json, sys, math e hashlib são importados mas não utilizados
           em nenhuma função do arquivo.
Impacto:  Imports desnecessários aumentam tempo de carga do módulo e geram confusão
           sobre dependências reais.
Recomendação: Remover imports não utilizados; manter apenas datetime e re.

[BAIXO] Constantes de domínio duplicadas entre model e utils
Arquivo: utils/helpers.py:110-116
Descrição: VALID_STATUSES, MAX_TITLE_LENGTH, MIN_TITLE_LENGTH e outras constantes
           de domínio de Task estão definidas em utils/helpers.py, separadas do
           modelo ao qual pertencem.
Impacto:  Fonte única da verdade fragmentada; risco de dessincronização entre
           constantes do modelo e do helper.
Recomendação: Mover todas as constantes de domínio de Task para models/task.py;
              importar de lá onde necessário.

================================
Total: 13 achados
================================
```

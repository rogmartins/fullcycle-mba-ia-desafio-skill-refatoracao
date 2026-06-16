```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   10 analyzed | ~1060 lines of code

Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 3

Findings

[CRITICAL] Hardcoded Secret Key
File: app.py:13
Description: A chave secreta da aplicação Flask está definida diretamente no
             código-fonte como string literal ('super-secret-key-123').
Impact:      Qualquer pessoa com acesso ao repositório conhece a chave usada
             para assinar cookies e tokens. Um atacante pode forjar sessões
             e tokens válidos sem precisar de credenciais.
Recommendation: Mover para variável de ambiente (SECRET_KEY) carregada com
                python-dotenv. Nunca commitar valores reais em arquivos de código.

[CRITICAL] Hardcoded Email Password
File: services/notification_service.py:10
Description: A senha de e-mail SMTP está escrita diretamente no código
             como 'senha123'.
Impact:      A senha fica exposta a qualquer pessoa com acesso ao repositório,
             permitindo uso não autorizado da conta de e-mail para envio de
             mensagens, spam ou acesso à caixa de entrada.
Recommendation: Mover para variável de ambiente (EMAIL_PASSWORD). Usar
                autenticação OAuth2 para SMTP em produção.

[CRITICAL] MD5 para Hash de Senhas
File: models/user.py:29
Description: As senhas dos usuários são armazenadas usando MD5
             (hashlib.md5), algoritmo criptograficamente quebrado para
             este fim.
Impact:      MD5 é extremamente rápido e sem salt, permitindo que um
             atacante que obtenha o banco de dados quebre as senhas em
             segundos usando tabelas rainbow ou força bruta com GPU.
             Todas as contas ficam comprometidas em caso de vazamento do BD.
Recommendation: Substituir por bcrypt ou argon2 (biblioteca passlib ou
                werkzeug.security). Adicionar salt automático por usuário.

[HIGH] Exposição do Hash de Senha na API
File: models/user.py:22
Description: O método to_dict() inclui o campo 'password' (hash MD5) na
             resposta JSON retornada pela API para todos os endpoints de usuário.
Impact:      Toda resposta de GET /users ou POST /users devolve o hash da
             senha ao cliente. Isso facilita ataques offline de dicionário e
             força bruta contra as senhas.
Recommendation: Remover o campo 'password' do retorno de to_dict(). Se
                necessário para uso interno, criar um método separado to_auth_dict().

[HIGH] Token JWT Falso no Login
File: routes/user_routes.py:210
Description: O endpoint /login retorna um token no formato
             'fake-jwt-token-{user_id}' sem qualquer assinatura criptográfica.
Impact:      Qualquer cliente pode adivinhar ou forjar tokens para qualquer
             usuário sabendo apenas o user_id. Não existe mecanismo real de
             autenticação nem autorização por token.
Recommendation: Implementar JWT real com PyJWT, assinado com a SECRET_KEY,
                contendo claims de expiração (exp) e identidade (sub).

[HIGH] Lógica de Negócio em Route Handler (task_routes)
File: routes/task_routes.py:30
Description: O handler get_tasks() executa cálculo de atraso (overdue),
             busca individual de User e Category para cada task dentro de
             um loop — tudo lógica de domínio dentro da camada de rota.
Impact:      Acopla regras de negócio à camada HTTP, impossibilitando
             reuso, testes unitários e manutenção independente. A lógica
             se duplica em outros handlers sem ponto único de verdade.
Recommendation: Mover cálculo de overdue para Task.is_overdue() (já existe,
                apenas não é utilizado). Extrair montagem do payload para
                Task.to_dict_full() ou um serviço TaskService.

[HIGH] Lógica de Negócio em Route Handler (report_routes)
File: routes/report_routes.py:54
Description: O handler summary_report() calcula métricas de produtividade
             por usuário com loops e contadores dentro da função de rota.
Impact:      Regras de cálculo de produtividade ficam presas na camada
             HTTP, impedindo reuso por outros endpoints ou serviços e
             dificultando testes isolados.
Recommendation: Extrair para um ReportService ou método estático no Model
                User.get_productivity_stats().

[MEDIUM] N+1 Queries em get_tasks
File: routes/task_routes.py:41
Description: Para cada task retornada pelo query principal, o handler
             executa User.query.get() e Category.query.get() separadamente
             dentro do loop de iteração.
Impact:      Para N tasks, são executadas 2N+1 queries no banco. Com volume
             crescente de tasks, o tempo de resposta degrada linearmente,
             sobrecarregando o banco de dados.
Recommendation: Usar eager loading com joinedload ou subqueryload:
                Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()

[MEDIUM] N+1 Queries em summary_report
File: routes/report_routes.py:54
Description: O loop sobre todos os usuários executa
             Task.query.filter_by(user_id=u.id) para cada usuário
             individualmente.
Impact:      Para N usuários, são executadas N+1 queries. Em sistemas
             com muitos usuários, o endpoint de relatório se torna
             progressivamente mais lento.
Recommendation: Usar agregação via GROUP BY com db.session.query ou
                joinedload para carregar tasks junto com usuários.

[MEDIUM] Lógica de Overdue Duplicada em 4 Locais
File: routes/task_routes.py:30
Description: O cálculo de overdue (verificar se due_date < utcnow e status
             não é done/cancelled) está repetido em task_routes.py (2x),
             user_routes.py e report_routes.py, ignorando Task.is_overdue()
             que já existe no Model.
Impact:      Qualquer correção ou mudança na regra de negócio precisa ser
             replicada em 4 lugares, criando risco de inconsistência entre
             endpoints.
Recommendation: Usar Task.is_overdue() em todos os locais. A implementação
                correta já existe em models/task.py:50.

[MEDIUM] Validação de Email Duplicada
File: routes/user_routes.py:61
Description: A expressão regular de validação de e-mail é copiada
             literalmente em create_user() (linha 61) e update_user()
             (linha 106), ignorando validate_email() de utils/helpers.py.
Impact:      Mudanças na regra de validação precisam ser feitas em 2
             lugares. Divergências silenciosas podem causar comportamento
             inconsistente entre criação e atualização de usuários.
Recommendation: Substituir as duas ocorrências por validate_email() de
                utils/helpers.py.

[LOW] Função process_task_data Nunca Utilizada
File: utils/helpers.py:57
Description: A função process_task_data() (52 linhas) foi implementada
             em utils/helpers.py mas nenhuma rota ou serviço a chama.
Impact:      Código morto aumenta a carga cognitiva de quem mantém o
             sistema, pois não está claro se a função é intencional ou
             esquecida.
Recommendation: Usar process_task_data() em task_routes.py substituindo
                a validação inline, ou remover se não for mais necessária.

[LOW] Uso de type() em Vez de isinstance()
File: routes/task_routes.py:141
Description: A verificação de tipo é feita com type(tags) == list nas
             linhas 141 e 210, em vez da forma idiomática isinstance(tags, list).
Impact:      type() não reconhece subclasses, tornando o código frágil e
             não-Pythônico. Leitores menos experientes podem confundir-se
             sobre a intenção.
Recommendation: Substituir por isinstance(tags, list).

[LOW] Números Mágicos para Limites de Validação
File: routes/task_routes.py:96
Description: Limites como 3, 200 (título), 1, 5 (prioridade) e 4 (senha)
             aparecem inline nos handlers, apesar de constantes equivalentes
             estarem definidas em utils/helpers.py (MIN_TITLE_LENGTH,
             MAX_TITLE_LENGTH, DEFAULT_PRIORITY, MIN_PASSWORD_LENGTH).
Impact:      Mudança em um limite exige busca manual por todas as
             ocorrências no código. Fácil de esquecer um local, causando
             comportamento inconsistente.
Recommendation: Importar e usar as constantes de utils/helpers.py em
                todas as validações.

================================
Total: 14 findings
================================

Phase 3 — Refactoring: COMPLETE
Phase 4 — Validation:  COMPLETE (13/13 routes OK)

Files changed:
  app.py                              — SECRET_KEY carregado de config.py
  config.py                           — NOVO: todas as configurações via env vars
  .env.example                        — NOVO: template de variáveis de ambiente
  requirements.txt                    — PyJWT>=2.10.1 adicionado
  models/user.py                      — werkzeug password hash; password fora do to_dict()
  routes/task_routes.py               — joinedload N+1; is_overdue(); isinstance; constantes
  routes/user_routes.py               — JWT real; validate_email(); constantes
  routes/report_routes.py             — delega para ReportService
  services/notification_service.py    — credenciais SMTP via config.py
  services/report_service.py          — NOVO: lógica de relatório extraída das rotas
  utils/helpers.py                    — process_task_data morto removido

audit/refactoring-log.md             — log completo de 14 mudanças
audit/post-refactor-tests.txt        — resultados pós-refatoração
================================
```

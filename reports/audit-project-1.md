# Architecture Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project (Loja API)
Stack:   Python + Flask
Files:   4 analyzed | ~784 lines of code

Summary
CRITICAL: 6 | HIGH: 5 | MEDIUM: 5 | LOW: 4

Findings

---[ CRITICAL ]---

[CRITICAL] SQL Injection — Authentication Query
File: models.py:110
Description: A função login_usuario() usa uma query de autenticação cujo
             WHERE é montado por concatenação de strings com os campos
             email e senha recebidos do usuário: "...WHERE email = '"
             + email + "' AND senha = '" + senha + "'".
Impact:      Por se tratar de uma query de autenticação (WHERE filtrando
             campos de credencial), um atacante pode ignorar a verificação
             de login sem fornecer uma senha válida. Qualquer valor como
             ' OR '1'='1 faz a condição sempre retornar verdadeiro,
             concedendo acesso como qualquer usuário, incluindo admins.
Recommendation: Substituir pela query parametrizada:
             cursor.execute("SELECT * FROM usuarios WHERE email = ?
             AND senha = ?", (email, senha))

[CRITICAL] SQL Injection — Dynamic WHERE Builder (buscar_produtos)
File: models.py:291
Description: A função buscar_produtos() constrói um SELECT com cláusulas
             WHERE montadas dinamicamente a partir dos parâmetros termo,
             categoria, preco_min e preco_max fornecidos pelo usuário,
             sem nenhuma sanitização ou parametrização.
Impact:      Por se tratar de um SELECT com WHERE builder dinâmico, os
             riscos são: (1) leitura de dados que o usuário não deveria
             ver, como ignorar os filtros de preço e categoria para
             obter registros restritos; (2) se for possível injetar
             cláusulas UNION, o atacante pode também ler dados de outras
             tabelas — como senhas da tabela de usuários — através do
             endpoint de busca de produtos. Isso representa a extração
             não autorizada de dados do sistema para uma parte externa.
Recommendation: Reescrever usando uma lista de condições acumuladas e
             placeholders parametrizados, eliminando toda concatenação
             de strings na construção da query.

[CRITICAL] SQL Injection — Systemic CRUD Operations
File: models.py:28
Description: Concatenação de strings é usada para construir SQL em todas
             as funções CRUD do arquivo. Cada tipo de operação expõe um
             risco distinto:
             — SELECT (linhas 28, 92, 174, 188, 192, 220, 224): leitura
               de dados que o usuário não está autorizado a ver; se
               injeção UNION for possível, também leitura de dados de
               outras tabelas — extração não autorizada de dados do
               sistema para uma parte externa.
             — INSERT (linhas 48, 126, 148, 157): inserção de registros
               sem autorização.
             — UPDATE (linhas 57, 163, 280): modificação de registros
               sem autorização.
             — DELETE (linha 68): exclusão de registros sem autorização.
Impact:      Cada caminho de leitura ou escrita no sistema é um vetor de
             ataque independente, possibilitando desde leitura indevida
             de dados até inserção, modificação e exclusão de registros
             por qualquer cliente HTTP.
Recommendation: Substituir toda concatenação SQL por queries
             parametrizadas com placeholders em todo o arquivo models.py.

[CRITICAL] Arbitrary SQL Execution Endpoint (/admin/query)
File: app.py:59
Description: O endpoint /admin/query recebe uma string SQL bruta no corpo
             da requisição e a executa diretamente no banco, sem nenhuma
             autenticação, autorização ou sanitização.
Impact:      Qualquer cliente HTTP anônimo pode executar qualquer operação
             no banco de dados: ler todos os dados, inserir ou modificar
             registros, excluir tabelas inteiras ou executar sequências
             arbitrárias de comandos SQL.
Recommendation: Remover o endpoint completamente. Se for imprescindível
             mantê-lo, protegê-lo com autenticação forte e verificação
             de perfil admin antes de qualquer execução.

[CRITICAL] Hardcoded SECRET_KEY Exposed in Health Response
File: app.py:7  /  controllers.py:289
Description: A SECRET_KEY do Flask está hardcoded como string simples em
             app.py:7 ("minha-chave-super-secreta-123") e é retornada
             literalmente no JSON do endpoint /health em
             controllers.py:289.
Impact:      Qualquer cliente que chame /health obtém a chave de
             assinatura da aplicação, permitindo forjar tokens de sessão
             e contornar proteções contra requisições falsas (CSRF) caso
             cookies de sessão sejam utilizados.
Recommendation: Carregar a SECRET_KEY de uma variável de ambiente.
             Remover o campo "secret_key" do payload de resposta do
             health-check.

[CRITICAL] Hardcoded Plaintext Credentials in Database Seed
File: database.py:76
Description: Os dados de seed inserem usuários com senhas em texto puro
             diretamente no código-fonte: ("Admin", "admin@loja.com",
             "admin123", "admin"), ("João Silva", "joao@email.com",
             "123456", ...).
Impact:      As credenciais ficam expostas no histórico do controle de
             versão; a conta admin utiliza uma senha trivialmente
             adivinhável sem nenhum hash, podendo ser usada por qualquer
             pessoa com acesso ao repositório.
Recommendation: Remover credenciais hardcoded do seed. Utilizar variáveis
             de ambiente ou um gerenciador de segredos para criação
             inicial do admin. Sempre armazenar senhas com hash.

---[ HIGH ]---

[HIGH] Plaintext Password Storage
File: database.py:77  /  models.py:127
Description: Senhas são inseridas e consultadas como strings em texto puro
             tanto no seed (database.py:77) quanto em criar_usuario
             (models.py:127). Nenhum algoritmo de hash é aplicado.
Impact:      Um dump do banco ou um ataque bem-sucedido expõe
             imediatamente todas as senhas dos usuários, permitindo que
             o atacante acesse outras contas onde as mesmas senhas
             sejam reutilizadas.
Recommendation: Aplicar hash nas senhas com bcrypt ou
             werkzeug.security.generate_password_hash antes de armazenar;
             verificar com check_password_hash no login.

[HIGH] Passwords Returned in API Responses
File: models.py:83  /  models.py:98
Description: As funções get_todos_usuarios() e get_usuario_por_id()
             incluem o campo "senha" em texto puro nos dicionários de
             retorno, que são serializados e enviados ao cliente.
Impact:      Qualquer chamada aos endpoints /usuarios ou /usuarios/<id>
             retorna as senhas de todos os usuários cadastrados para
             quem fizer a requisição.
Recommendation: Excluir o campo senha de todos os serializadores de
             resposta da API.

[HIGH] Global Mutable Database Connection (Shared State)
File: database.py:4
Description: Uma única variável de módulo db_connection = None é mutada
             e compartilhada entre todas as requisições via singleton
             get_db().
Impact:      Em ambientes com múltiplas requisições simultâneas,
             requisições concorrentes compartilham a mesma conexão,
             causando condições de corrida (situações onde o resultado
             depende da ordem imprevisível de execução), corrupção de
             cursores e inconsistência nos dados retornados.
Recommendation: Utilizar o objeto flask.g ou um pool de conexões (ex.:
             SQLAlchemy) para escopar conexões por requisição.

[HIGH] Discount Business Logic Embedded in Data Layer
File: models.py:257
Description: A função relatorio_vendas() aplica regras de desconto por
             faixa (>10000 → 10%, >5000 → 5%, >1000 → 2%) diretamente
             na camada de Model, que deveria apenas agregar dados brutos.
Impact:      Regras de negócio ficam ocultas na camada de dados,
             impossibilitando testes isolados e forçando duplicação se
             outros pontos da aplicação precisarem da mesma lógica.
Recommendation: Retornar apenas agregados brutos do Model e mover o
             cálculo de desconto para uma camada de serviço ou controller.

[HIGH] Notification Side Effects in Controller
File: controllers.py:208
Description: A função criar_pedido() contém stubs de notificação (email,
             SMS, push) implementados como chamadas print() embutidas
             diretamente no corpo do controller.
Impact:      A lógica de notificação está acoplada ao controller HTTP e
             não pode ser testada de forma isolada, desativada ou
             substituída por um serviço real sem alterar o controller.
Recommendation: Extrair a lógica de notificações para um módulo dedicado
             (ex.: notifications.py) e chamá-lo a partir do controller.

---[ MEDIUM ]---

[MEDIUM] N+1 Queries in get_pedidos_usuario
File: models.py:188  /  models.py:192
Description: Para cada pedido, a função emite uma query para buscar os
             itens (linha 188) e, para cada item, emite outra query para
             obter o nome do produto (linha 192), usando cursor2 e
             cursor3 separados.
Impact:      Para um usuário com P pedidos e I itens cada, são geradas
             1 + P + (P×I) consultas ao banco em vez de 1 a 3 com JOINs,
             degradando a performance proporcionalmente ao volume de dados.
Recommendation: Substituir o loop aninhado por uma única query com JOIN:
             SELECT p.*, ip.*, pr.nome FROM pedidos p
             JOIN itens_pedido ip ON ip.pedido_id = p.id
             JOIN produtos pr ON pr.id = ip.produto_id
             WHERE p.usuario_id = ?

[MEDIUM] N+1 Queries in get_todos_pedidos
File: models.py:220  /  models.py:224
Description: get_todos_pedidos() é uma cópia quase idêntica de
             get_pedidos_usuario() com o mesmo loop de cursores aninhados
             e o mesmo padrão N+1.
Impact:      Agrava o problema em escopo global (todos os pedidos de
             todos os usuários); a complexidade é O(P×I) onde P é o
             total de pedidos e I a média de itens por pedido.
Recommendation: Extrair a serialização em um helper privado
             _serialize_pedidos(rows) e aplicar a mesma query com JOIN.

[MEDIUM] Duplicated Order-Fetching Logic
File: models.py:171  /  models.py:203
Description: get_pedidos_usuario() e get_todos_pedidos() compartilham
             aproximadamente 30 linhas de código quase idêntico: loop
             de cursor, busca de itens, resolução do nome do produto e
             construção do dicionário de retorno.
Impact:      Correções de bugs ou mudanças de schema precisam ser
             aplicadas em dois lugares; as funções já divergiram
             levemente, aumentando o risco de inconsistência futura.
Recommendation: Extrair a lógica compartilhada em um helper privado
             _serialize_pedidos(rows) reutilizável pelas duas funções.

[MEDIUM] Unauthenticated Admin Endpoint (/admin/reset-db)
File: app.py:47
Description: O endpoint POST /admin/reset-db deleta todas as linhas de
             todas as tabelas sem exigir nenhuma autenticação ou
             verificação de autorização.
Impact:      Qualquer cliente HTTP com acesso de rede ao servidor pode
             apagar instantaneamente todos os produtos, usuários e
             pedidos do sistema.
Recommendation: Exigir autenticação de administrador (ex.: JWT com
             role=admin) antes de executar operações destrutivas.

[MEDIUM] Missing Email Format Validation in criar_usuario
File: controllers.py:157
Description: A função criar_usuario() verifica apenas se o campo email
             é não vazio, sem validar o formato (ex.: presença de @),
             permitindo que endereços malformados sejam armazenados.
Impact:      Endereços inválidos causam falhas silenciosas na entrega de
             e-mails; dados malformados acumulam-se no banco sem que o
             sistema emita qualquer alerta.
Recommendation: Validar o formato do email com regex ou com a biblioteca
             email-validator antes de passá-lo ao model.

---[ LOW ]---

[LOW] Magic Numbers in Discount Thresholds
File: models.py:257
Description: Os limites de faixa de desconto (10000, 5000, 1000) e as
             taxas (0.1, 0.05, 0.02) aparecem como literais numéricos
             sem constantes nomeadas nem comentários explicativos.
Impact:      Leitores não conseguem entender a regra de negócio sem
             contexto; qualquer alteração exige localizar e atualizar
             todos os valores manualmente.
Recommendation: Extrair para constantes nomeadas:
             DISCOUNT_TIER_HIGH = 10000; DISCOUNT_RATE_HIGH = 0.10, etc.

[LOW] Meaningless Variable Names (cursor2, cursor3)
File: models.py:187  /  models.py:192  /  models.py:219  /  models.py:224
Description: Cursores de banco aninhados são nomeados cursor2 e cursor3,
             sem transmitir nenhuma intenção sobre o que consultam.
Impact:      Baixa legibilidade; o problema será eliminado naturalmente
             quando o N+1 for corrigido com queries JOIN.
Recommendation: Corrigir como parte da remediação do N+1 (MEDIUM acima).

[LOW] DEBUG Mode Hardcoded to True
File: app.py:8
Description: app.config["DEBUG"] = True está definido incondicionalmente
             no código-fonte, ativando o debugger interativo em qualquer
             ambiente onde a aplicação for executada.
Impact:      Em produção, o debugger interativo pode expor informações
             internas da aplicação e permitir execução de código por
             quem tiver acesso à interface de erro.
Recommendation: Carregar do ambiente:
             app.config["DEBUG"] = os.getenv("DEBUG","false").lower()=="true"

[LOW] print() Used for Logging Throughout
File: controllers.py:8, 11, 57, 106, 161, 179, 208, 219
Description: Mensagens de debug e operacionais são emitidas por chamadas
             print() espalhadas por controllers.py e database.py.
Impact:      Sem níveis de log, sem timestamps e sem saída estruturada,
             é impossível silenciar mensagens em produção ou direcioná-las
             para um sistema de monitoramento.
Recommendation: Substituir pelo módulo logging do Python:
             import logging; logger = logging.getLogger(__name__)

================================
Total: 20 findings
================================
```

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

[CRITICAL] SQL Injection — Authentication Bypass
File: models.py:110
Description: A função login_usuario() constrói a cláusula WHERE por
             concatenação de strings: "...WHERE email = '" + email +
             "' AND senha = '" + senha + "'". Qualquer valor como
             ' OR '1'='1 ignora a autenticação por completo.
Impact:      Um atacante não autenticado pode acessar o sistema como
             qualquer usuário, incluindo administradores, sem precisar
             conhecer nenhuma credencial válida.
Recommendation: Substituir pela query parametrizada:
             cursor.execute("SELECT * FROM usuarios WHERE email = ?
             AND senha = ?", (email, senha))

[CRITICAL] SQL Injection — Dynamic Query Builder (buscar_produtos)
File: models.py:291
Description: A função buscar_produtos() monta a string SQL concatenando
             diretamente os parâmetros termo, categoria, preco_min e
             preco_max fornecidos pelo usuário, sem sanitização ou
             parametrização.
Impact:      Um atacante pode injetar SQL arbitrário em qualquer campo
             de busca, possibilitando exfiltração de dados, modificações
             e até deleção completa do banco.
Recommendation: Reescrever usando placeholders parametrizados e uma lista
             de condições acumuladas, eliminando toda concatenação de
             strings na construção da query.

[CRITICAL] SQL Injection — Systemic in CRUD Operations
File: models.py:28
Description: Concatenação de strings é usada para construir SQL em todas
             as funções CRUD: get_produto_por_id (:28), criar_produto
             (:48), atualizar_produto (:57), deletar_produto (:68),
             get_usuario_por_id (:92), criar_usuario (:126),
             criar_pedido (:140, :148, :155, :163),
             get_pedidos_usuario (:174, :188, :192),
             get_todos_pedidos (:220, :224),
             atualizar_status_pedido (:280).
Impact:      Todos os caminhos de leitura e escrita são vetores de SQL
             Injection, expondo o banco inteiro à manipulação por
             qualquer cliente HTTP.
Recommendation: Substituir toda concatenação SQL por queries
             parametrizadas com o placeholder ? em todo o arquivo
             models.py.

[CRITICAL] Arbitrary SQL Execution Endpoint (/admin/query)
File: app.py:59
Description: O endpoint /admin/query recebe uma string SQL bruta no corpo
             da requisição e a executa diretamente no banco, sem nenhuma
             autenticação, autorização ou sanitização.
Impact:      Qualquer cliente HTTP anônimo pode ler, modificar ou deletar
             todos os dados, realizar DROP de tabelas ou executar qualquer
             operação arbitrária no banco de dados.
Recommendation: Remover o endpoint completamente. Se necessário mantê-lo,
             protegê-lo com autenticação forte e verificação de perfil
             admin antes de qualquer execução.

[CRITICAL] Hardcoded SECRET_KEY Exposed in Health Response
File: app.py:7  /  controllers.py:289
Description: A SECRET_KEY do Flask está hardcoded como string simples em
             app.py:7 ("minha-chave-super-secreta-123") e é retornada
             literalmente na resposta JSON do endpoint /health em
             controllers.py:289.
Impact:      Qualquer cliente que chame /health obtém a chave de
             assinatura, permitindo forjar sessões e contornar proteções
             CSRF caso cookies de sessão sejam utilizados.
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
             adivinhável e armazenada sem nenhum hash.
Recommendation: Remover credenciais hardcoded do seed. Utilizar variáveis
             de ambiente ou um gerenciador de segredos para a criação
             inicial do admin. Sempre armazenar senhas com hash.

---[ HIGH ]---

[HIGH] Plaintext Password Storage
File: database.py:77  /  models.py:127
Description: Senhas são inseridas e consultadas como strings em texto puro
             tanto no seed (database.py:77) quanto em criar_usuario
             (models.py:127). Nenhum algoritmo de hash é aplicado em
             nenhum ponto do fluxo.
Impact:      Um dump do banco ou um ataque de SQL Injection expõe
             imediatamente todas as senhas dos usuários. Ataques de
             credential stuffing tornam-se triviais.
Recommendation: Aplicar hash nas senhas com bcrypt ou
             werkzeug.security.generate_password_hash antes de armazenar;
             verificar com check_password_hash no login.

[HIGH] Passwords Returned in API Responses
File: models.py:83  /  models.py:98
Description: As funções get_todos_usuarios() e get_usuario_por_id()
             incluem o campo "senha" (senha em texto puro) nos dicionários
             de retorno, que são então serializados e enviados ao cliente.
Impact:      Qualquer chamada autenticada a /usuarios ou /usuarios/<id>
             retorna as senhas de todos os usuários cadastrados.
Recommendation: Excluir o campo senha de todos os serializadores de
             resposta da API.

[HIGH] Global Mutable Database Connection (Shared State)
File: database.py:4
Description: Uma única variável de módulo db_connection = None é mutada e
             compartilhada entre todas as requisições via singleton get_db().
Impact:      No Flask multi-threaded (padrão), requisições concorrentes
             compartilham a mesma conexão, causando race conditions,
             corrupção de cursores e inconsistência de dados.
             O flag check_same_thread=False silencia o erro, não o risco.
Recommendation: Utilizar o objeto flask.g ou um pool de conexões (ex.:
             SQLAlchemy) para escopar conexões por requisição.

[HIGH] Discount Business Logic Embedded in Data Layer
File: models.py:257
Description: A função relatorio_vendas() aplica regras de desconto por
             faixa (>10000 → 10%, >5000 → 5%, >1000 → 2%) diretamente
             dentro da camada de Model, que deveria apenas agregar dados
             brutos.
Impact:      Regras de negócio ficam ocultas na camada de dados,
             impossibilitando testes isolados e gerando duplicação se
             outros pontos precisarem da mesma lógica.
Recommendation: Retornar apenas agregados brutos do Model e mover o
             cálculo de desconto para uma camada de serviço ou para o
             controller.

[HIGH] Notification Side Effects in Controller
File: controllers.py:208
Description: A função criar_pedido() contém stubs de notificação (email,
             SMS, push) implementados como chamadas print() embutidas
             diretamente no corpo do controller.
Impact:      A lógica de notificação está acoplada ao controller HTTP;
             não pode ser testada de forma isolada, desativada ou
             substituída por um serviço real de notificações.
Recommendation: Extrair a lógica de notificações para um módulo dedicado
             (ex.: notifications.py) e chamá-lo a partir do controller.

---[ MEDIUM ]---

[MEDIUM] N+1 Queries in get_pedidos_usuario
File: models.py:188  /  models.py:192
Description: Para cada pedido, a função emite uma query para buscar os
             itens_pedido (linha 188) e, para cada item, emite outra
             query para obter o nome do produto (linha 192), usando
             cursor2 e cursor3 separados.
Impact:      Para um usuário com P pedidos e I itens cada, são geradas
             1 + P + P*I consultas ao banco em vez de 1 a 3 com JOINs,
             degradando severamente a performance em volumes reais.
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
Impact:      Agrava o problema de N+1 em escopo global (todos os pedidos,
             todos os usuários); qualquer carga no endpoint /pedidos tem
             complexidade O(P*I).
Recommendation: Extrair a lógica de serialização de pedidos em uma função
             auxiliar privada _serialize_pedidos(rows) e usar a mesma
             abordagem com JOIN.

[MEDIUM] Duplicated Order-Fetching Logic
File: models.py:171  /  models.py:203
Description: get_pedidos_usuario() e get_todos_pedidos() compartilham
             aproximadamente 30 linhas de código quase idêntico: loop de
             cursor, busca de itens, resolução do nome do produto e
             construção do dicionário.
Impact:      Correções de bugs ou mudanças de schema precisam ser
             aplicadas em dois lugares; as funções já divergiram
             levemente (linha em branco extra em 211 vs 178).
Recommendation: Extrair a serialização compartilhada em um helper privado
             _serialize_pedidos(rows) reutilizável por ambas as funções.

[MEDIUM] Unauthenticated Admin Endpoint (/admin/reset-db)
File: app.py:47
Description: O endpoint POST /admin/reset-db deleta todas as linhas de
             todas as tabelas sem exigir nenhuma autenticação ou
             verificação de autorização.
Impact:      Qualquer cliente HTTP com acesso de rede ao servidor pode
             apagar instantaneamente todos os produtos, usuários e pedidos
             do sistema.
Recommendation: Exigir autenticação de administrador (ex.: JWT ou token
             de sessão com role=admin) antes de executar operações
             destrutivas.

[MEDIUM] Missing Email Format Validation in criar_usuario
File: controllers.py:157
Description: A função criar_usuario() verifica apenas se o campo email é
             não vazio, sem validar o formato (ex.: presença de @),
             permitindo que endereços malformados sejam armazenados.
Impact:      Endereços inválidos causam falhas silenciosas na entrega de
             e-mails; combinado com SQL Injection, amplia a superfície de
             ataque.
Recommendation: Validar o formato do email com regex ou com a biblioteca
             email-validator antes de passá-lo ao model.

---[ LOW ]---

[LOW] Magic Numbers in Discount Thresholds
File: models.py:257
Description: Os valores de faixa de desconto (10000, 5000, 1000) e as
             taxas (0.1, 0.05, 0.02) aparecem como literais numéricos
             sem constantes nomeadas nem comentários explicativos.
Impact:      Leitores não conseguem entender a regra de negócio sem
             contexto adicional; alterações exigem localizar todas as
             ocorrências manualmente.
Recommendation: Extrair para constantes nomeadas:
             DISCOUNT_TIER_HIGH = 10000; DISCOUNT_RATE_HIGH = 0.10, etc.

[LOW] Meaningless Variable Names (cursor2, cursor3)
File: models.py:187  /  models.py:192  /  models.py:219  /  models.py:224
Description: Cursores de banco de dados aninhados são nomeados cursor2 e
             cursor3 em todas as funções de busca de pedidos, sem
             transmitir nenhuma intenção.
Impact:      Baixa legibilidade; o problema será eliminado naturalmente
             quando o N+1 for corrigido com queries JOIN (os cursores
             extras se tornam desnecessários).
Recommendation: Corrigir como parte da remediação do N+1 (MEDIUM acima).

[LOW] DEBUG Mode Hardcoded to True
File: app.py:8
Description: app.config["DEBUG"] = True está definido incondicionalmente
             no código-fonte, mantendo o debugger interativo sempre ativo.
Impact:      Em produção, isso expõe o debugger interativo do Werkzeug
             com um PIN que pode permitir execução remota de código.
Recommendation: Carregar do ambiente:
             app.config["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"

[LOW] print() Used for Logging Throughout
File: controllers.py:8, 11, 57, 106, 161, 179, 208, 219
Description: Mensagens de debug e operacionais são emitidas por chamadas
             print() espalhadas por controllers.py e database.py, sem
             nenhuma estrutura de log formal.
Impact:      Sem níveis de log, sem timestamps, sem saída estruturada;
             impossível silenciar em produção ou direcionar para um
             agregador de logs.
Recommendation: Substituir pelo módulo logging do Python:
             import logging; logger = logging.getLogger(__name__)

================================
Total: 20 findings
================================
```

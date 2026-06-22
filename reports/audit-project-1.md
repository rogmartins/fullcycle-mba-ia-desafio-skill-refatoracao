```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 3 | LOW: 2

Findings

[CRITICAL] Hardcoded Secret Key
File: app.py:7
Description: A chave secreta da aplicação está definida literalmente no
             código-fonte em vez de ser lida de uma variável de ambiente.
Impact:      Qualquer pessoa com acesso ao repositório obtém a chave usada
             para assinar tokens e sessões, podendo forjar identidades.
Recommendation: Mover para variável de ambiente e ler via
                `os.environ.get("SECRET_KEY")`. Nunca versionar segredos.

[CRITICAL] SQL Injection — Execução Arbitrária de Query
File: app.py:69
Description: O endpoint POST /admin/query recebe uma string SQL do corpo
             da requisição e a executa diretamente no banco sem qualquer
             sanitização ou autenticação.
Impact:      Um atacante sem autenticação pode executar qualquer instrução
             SQL — SELECT para ler todos os dados, DELETE para apagar
             registros, DROP TABLE para destruir tabelas. Exposição total
             do banco de dados.
Recommendation: Remover o endpoint /admin/query. Operações administrativas
                devem ser realizadas por migrações controladas, não por
                endpoints dinâmicos. Se necessário, exigir autenticação de
                administrador e limitar a operações previamente catalogadas.

[CRITICAL] SQL Injection — INSERT com Concatenação de Strings
File: models.py:47
Description: A função `criar_produto` monta a query INSERT concatenando
             os parâmetros `nome`, `descricao` e `categoria` diretamente
             na string SQL usando o operador `+`.
Impact:      Um atacante pode injetar SQL nos campos de texto do produto,
             inserindo registros arbitrários ou corrompendo dados existentes
             — operação de INSERT permite inserção de dados não autorizados.
Recommendation: Substituir por query parametrizada:
                `cursor.execute("INSERT INTO produtos (...) VALUES (?,?,?,?,?)",
                (nome, descricao, preco, estoque, categoria))`.

[CRITICAL] SQL Injection — Autenticação via Concatenação de Strings
File: models.py:109
Description: A query de login monta a cláusula WHERE concatenando `email`
             e `senha` diretamente na string SQL, ambos vindos do corpo da
             requisição.
Impact:      Um atacante pode ignorar a verificação de senha sem fornecer
             uma senha válida. Por exemplo, informando `email = "' OR '1'='1"`,
             a query retorna todos os usuários e o primeiro é autenticado.
             Isso é uma falha de autenticação que dá acesso não autorizado
             ao sistema — incluindo contas de administrador.
Recommendation: Substituir por query parametrizada:
                `cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?",
                (email, senha))`. Além disso, armazenar senhas com hash
                (bcrypt ou argon2) em vez de texto puro.

[CRITICAL] SQL Injection — Dynamic WHERE Builder
File: models.py:285
Description: A função `buscar_produtos` constrói dinamicamente uma query
             SELECT concatenando os parâmetros `termo`, `categoria`,
             `preco_min` e `preco_max` diretamente na string SQL.
Impact:      Um atacante pode injetar SQL no campo `termo` ou `categoria`,
             lendo dados de outras tabelas via UNION (por exemplo, extraindo
             emails e senhas da tabela `usuarios`) — o que configura
             exfiltração não autorizada de dados do sistema.
Recommendation: Usar query parametrizada com placeholders `?` e acumular
                parâmetros em uma lista. Exemplo:
                `params = []; query += " AND nome LIKE ?"; params.append(f"%{termo}%")`.

[HIGH] Business Logic in Controller — Notifications
File: controllers.py:208
Description: O controller `criar_pedido` contém lógica de negócio de
             notificação (email, SMS, push) simulada via `print`,
             misturando responsabilidade de orquestração com regras de
             domínio.
Impact:      Notificações são regras de negócio — sua presença no controller
             impede reutilização, dificulta testes e cria acoplamento entre
             camadas. Qualquer mudança na política de notificação exige
             modificar o controller.
Recommendation: Extrair para um `NotificationService` independente. O
                controller apenas chama `notification_service.pedido_criado(pedido_id)`.

[HIGH] Sensitive Data Exposed in API Response
File: controllers.py:289
Description: O endpoint GET /health retorna a `secret_key` da aplicação no
             corpo da resposta JSON.
Impact:      Qualquer cliente que chamar o endpoint de health check obtém a
             chave secreta usada para assinar sessões e tokens, mesmo sem
             autenticação. Isso anula qualquer proteção oferecida pela chave.
Recommendation: Remover completamente o campo `secret_key` da resposta do
                health check. Informações de configuração interna não devem
                ser expostas via API.

[HIGH] Tight Coupling — Direct DB Access in Controller
File: controllers.py:266
Description: O controller `health_check` importa e chama diretamente
             `get_db()`, acessando o banco de dados sem passar pela camada
             de Model.
Impact:      O controller fica acoplado à implementação do banco, tornando
             impossível testar o health check em isolamento ou trocar a
             fonte de dados sem modificar o controller.
Recommendation: Criar um método no Model ou em um serviço de infraestrutura
                que exponha o status da conexão. O controller deve chamar
                apenas esse serviço.

[HIGH] Mutable Global State — Database Connection
File: database.py:4
Description: A variável `db_connection` é declarada no escopo do módulo e
             mutada a cada chamada de `get_db()`, criando estado global
             compartilhado entre todas as requisições.
Impact:      Em ambientes com múltiplas threads (Flask em produção), o
             compartilhamento de uma única conexão causa race conditions e
             erros de concorrência. Impossível isolar conexões por requisição
             ou por teste.
Recommendation: Usar `flask.g` para armazenar a conexão por requisição,
                ou adotar um pool de conexões. Remover a variável global.

[MEDIUM] Missing Input Validation — Login Request Body
File: controllers.py:167
Description: O controller `login` chama `dados.get(...)` sem verificar
             antes se `dados` é `None` — o que ocorre quando o cliente
             envia uma requisição sem `Content-Type: application/json`.
Impact:      Uma requisição mal formada causa `AttributeError: 'NoneType'
             object has no attribute 'get'`, que vaza o stack trace
             internamente e retorna erro 500 sem mensagem clara.
Recommendation: Adicionar verificação `if not dados: return jsonify({"erro":
                "Corpo da requisição inválido"}), 400` antes de qualquer
                acesso a `dados`.

[MEDIUM] N+1 Queries — get_pedidos_usuario
File: models.py:186
Description: Para cada pedido retornado pela query inicial, a função executa
             uma query adicional para buscar os itens e outra para buscar o
             nome de cada produto, resultando em 1 + N + N×M queries.
Impact:      Para um usuário com 10 pedidos de 5 itens cada, são executadas
             51 queries onde 1 seria suficiente com JOINs. A degradação de
             performance é proporcional ao volume de dados.
Recommendation: Substituir pelo padrão de eager loading: buscar pedidos,
                itens e produtos em queries separadas por IDs e montar os
                objetos em memória, ou usar uma única query com JOIN e
                agrupar os resultados.

[MEDIUM] N+1 Queries — get_todos_pedidos
File: models.py:219
Description: Idêntico ao padrão em `get_pedidos_usuario`: para cada pedido
             da tabela inteira, são executadas queries adicionais para
             itens e nomes de produtos.
Impact:      Em produção com centenas de pedidos, o endpoint GET /pedidos
             pode demorar segundos por estar emitindo centenas de queries
             individuais onde um JOIN resolveria.
Recommendation: Aplicar o mesmo padrão de eager loading descrito para
                `get_pedidos_usuario`. Considerar paginação no endpoint
                para limitar o volume total.

[LOW] Magic Strings — Hardcoded Category List
File: controllers.py:52
Description: A lista de categorias válidas está definida como literal
             inline dentro do controller, sem nenhuma constante nomeada.
Impact:      A lista precisa ser mantida manualmente em qualquer lugar
             onde categorias sejam validadas. Uma divergência cria bugs
             silenciosos.
Recommendation: Extrair para uma constante em um módulo de configuração:
                `CATEGORIAS_VALIDAS = ["informatica", "moveis", ...]` e
                importar onde necessário.

[LOW] Magic Numbers — Discount Thresholds
File: models.py:257
Description: Os limites de faturamento para cálculo de desconto (10000,
             5000, 1000) e os percentuais (0.1, 0.05, 0.02) estão como
             literais numéricos sem nomes que expliquem seu significado.
Impact:      Não é possível entender as regras de negócio sem contexto
             externo. Qualquer alteração nas faixas de desconto requer
             localizar os números no código.
Recommendation: Extrair para constantes nomeadas:
                `DESCONTO_ALTO = 0.10; LIMITE_FATURAMENTO_ALTO = 10000`.

================================
Total: 14 findings
================================
```

---
**Generated**: 2026-06-22 10:00
**Analyzer**: refactor-arch skill
**Project number**: 1

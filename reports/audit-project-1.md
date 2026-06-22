```
================================
RELATÓRIO DE AUDITORIA ARQUITETURAL
================================
Projeto: code-smells-project
Stack:   Python + Flask 3.1.1
Arquivos: 4 analisados | ~780 linhas de código

Resumo
CRÍTICO: 5 | ALTO: 4 | MÉDIO: 3 | BAIXO: 2

Achados

[CRÍTICO] Chave Secreta Hardcoded
Arquivo: app.py:7
Descrição:    A chave secreta da aplicação está definida literalmente no
              código-fonte em vez de ser lida de uma variável de ambiente.
Impacto:      Qualquer pessoa com acesso ao repositório obtém a chave usada
              para assinar tokens e sessões, podendo forjar identidades.
Recomendação: Mover para variável de ambiente e ler via
              `os.environ.get("SECRET_KEY")`. Nunca versionar segredos.

[CRÍTICO] Injeção de SQL — Execução Arbitrária de Query
Arquivo: app.py:69
Descrição:    O endpoint POST /admin/query recebe uma string SQL do corpo
              da requisição e a executa diretamente no banco sem qualquer
              sanitização ou autenticação.
Impacto:      Um atacante sem autenticação pode executar qualquer instrução
              SQL — SELECT para ler todos os dados, DELETE para apagar
              registros, DROP TABLE para destruir tabelas. Exposição total
              do banco de dados.
Recomendação: Remover o endpoint /admin/query. Operações administrativas
              devem ser realizadas por migrações controladas, não por
              endpoints dinâmicos. Se necessário, exigir autenticação de
              administrador e limitar a operações previamente catalogadas.

[CRÍTICO] Injeção de SQL — INSERT com Concatenação de Strings
Arquivo: models.py:47
Descrição:    A função `criar_produto` monta a query INSERT concatenando
              os parâmetros `nome`, `descricao` e `categoria` diretamente
              na string SQL usando o operador `+`.
Impacto:      Um atacante pode injetar SQL nos campos de texto do produto,
              inserindo registros arbitrários ou corrompendo dados existentes
              — operação de INSERT permite inserção de dados não autorizados.
Recomendação: Substituir por query parametrizada:
              `cursor.execute("INSERT INTO produtos (...) VALUES (?,?,?,?,?)",
              (nome, descricao, preco, estoque, categoria))`.

[CRÍTICO] Injeção de SQL — Autenticação via Concatenação de Strings
Arquivo: models.py:109
Descrição:    A query de login monta a cláusula WHERE concatenando `email`
              e `senha` diretamente na string SQL, ambos vindos do corpo da
              requisição.
Impacto:      Um atacante pode ignorar a verificação de senha sem fornecer
              uma senha válida. Por exemplo, informando `email = "' OR '1'='1"`,
              a query retorna todos os usuários e o primeiro é autenticado.
              Isso é uma falha de autenticação que dá acesso não autorizado
              ao sistema — incluindo contas de administrador.
Recomendação: Substituir por query parametrizada:
              `cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?",
              (email, senha))`. Além disso, armazenar senhas com hash
              (bcrypt ou argon2) em vez de texto puro.

[CRÍTICO] Injeção de SQL — Construtor Dinâmico de WHERE
Arquivo: models.py:285
Descrição:    A função `buscar_produtos` constrói dinamicamente uma query
              SELECT concatenando os parâmetros `termo`, `categoria`,
              `preco_min` e `preco_max` diretamente na string SQL.
Impacto:      Um atacante pode injetar SQL no campo `termo` ou `categoria`,
              lendo dados de outras tabelas via UNION (por exemplo, extraindo
              emails e senhas da tabela `usuarios`) — o que configura
              exfiltração não autorizada de dados do sistema.
Recomendação: Usar query parametrizada com placeholders `?` e acumular
              parâmetros em uma lista. Exemplo:
              `params = []; query += " AND nome LIKE ?"; params.append(f"%{termo}%")`.

[ALTO] Lógica de Negócio no Controller — Notificações
Arquivo: controllers.py:208
Descrição:    O controller `criar_pedido` contém lógica de negócio de
              notificação (email, SMS, push) simulada via `print`,
              misturando responsabilidade de orquestração com regras de
              domínio.
Impacto:      Notificações são regras de negócio — sua presença no controller
              impede reutilização, dificulta testes e cria acoplamento entre
              camadas. Qualquer mudança na política de notificação exige
              modificar o controller.
Recomendação: Extrair para um `NotificationService` independente. O
              controller apenas chama `notification_service.pedido_criado(pedido_id)`.

[ALTO] Dado Sensível Exposto na Resposta da API
Arquivo: controllers.py:289
Descrição:    O endpoint GET /health retorna a `secret_key` da aplicação no
              corpo da resposta JSON.
Impacto:      Qualquer cliente que chamar o endpoint de health check obtém a
              chave secreta usada para assinar sessões e tokens, mesmo sem
              autenticação. Isso anula qualquer proteção oferecida pela chave.
Recomendação: Remover completamente o campo `secret_key` da resposta do
              health check. Informações de configuração interna não devem
              ser expostas via API.

[ALTO] Acoplamento Forte — Acesso Direto ao Banco no Controller
Arquivo: controllers.py:266
Descrição:    O controller `health_check` importa e chama diretamente
              `get_db()`, acessando o banco de dados sem passar pela camada
              de Model.
Impacto:      O controller fica acoplado à implementação do banco, tornando
              impossível testar o health check em isolamento ou trocar a
              fonte de dados sem modificar o controller.
Recomendação: Criar um método no Model ou em um serviço de infraestrutura
              que exponha o status da conexão. O controller deve chamar
              apenas esse serviço.

[ALTO] Estado Global Mutável — Conexão com Banco de Dados
Arquivo: database.py:4
Descrição:    A variável `db_connection` é declarada no escopo do módulo e
              mutada a cada chamada de `get_db()`, criando estado global
              compartilhado entre todas as requisições.
Impacto:      Em ambientes com múltiplas threads (Flask em produção), o
              compartilhamento de uma única conexão causa condições de corrida
              e erros de concorrência. Impossível isolar conexões por
              requisição ou por teste.
Recomendação: Usar `flask.g` para armazenar a conexão por requisição,
              ou adotar um pool de conexões. Remover a variável global.

[MÉDIO] Validação de Entrada Ausente — Corpo da Requisição de Login
Arquivo: controllers.py:167
Descrição:    O controller `login` chama `dados.get(...)` sem verificar
              antes se `dados` é `None` — o que ocorre quando o cliente
              envia uma requisição sem `Content-Type: application/json`.
Impacto:      Uma requisição mal formada causa `AttributeError: 'NoneType'
              object has no attribute 'get'`, que vaza o stack trace
              internamente e retorna erro 500 sem mensagem clara.
Recomendação: Adicionar verificação `if not dados: return jsonify({"erro":
              "Corpo da requisição inválido"}), 400` antes de qualquer
              acesso a `dados`.

[MÉDIO] Queries N+1 — get_pedidos_usuario
Arquivo: models.py:186
Descrição:    Para cada pedido retornado pela query inicial, a função executa
              uma query adicional para buscar os itens e outra para buscar o
              nome de cada produto, resultando em 1 + N + N×M queries.
Impacto:      Para um usuário com 10 pedidos de 5 itens cada, são executadas
              51 queries onde 1 seria suficiente com JOINs. A degradação de
              performance é proporcional ao volume de dados.
Recomendação: Substituir pelo padrão de carregamento antecipado (eager
              loading): buscar pedidos, itens e produtos em queries separadas
              por IDs e montar os objetos em memória, ou usar uma única query
              com JOIN e agrupar os resultados.

[MÉDIO] Queries N+1 — get_todos_pedidos
Arquivo: models.py:219
Descrição:    Idêntico ao padrão em `get_pedidos_usuario`: para cada pedido
              da tabela inteira, são executadas queries adicionais para
              itens e nomes de produtos.
Impacto:      Em produção com centenas de pedidos, o endpoint GET /pedidos
              pode demorar segundos por estar emitindo centenas de queries
              individuais onde um JOIN resolveria.
Recomendação: Aplicar o mesmo padrão de carregamento antecipado descrito para
              `get_pedidos_usuario`. Considerar paginação no endpoint
              para limitar o volume total.

[BAIXO] Strings Mágicas — Lista de Categorias Hardcoded
Arquivo: controllers.py:52
Descrição:    A lista de categorias válidas está definida como literal
              inline dentro do controller, sem nenhuma constante nomeada.
Impacto:      A lista precisa ser mantida manualmente em qualquer lugar
              onde categorias sejam validadas. Uma divergência cria erros
              silenciosos.
Recomendação: Extrair para uma constante em um módulo de configuração:
              `CATEGORIAS_VALIDAS = ["informatica", "moveis", ...]` e
              importar onde necessário.

[BAIXO] Números Mágicos — Limiares de Desconto
Arquivo: models.py:257
Descrição:    Os limites de faturamento para cálculo de desconto (10000,
              5000, 1000) e os percentuais (0.1, 0.05, 0.02) estão como
              literais numéricos sem nomes que expliquem seu significado.
Impacto:      Não é possível entender as regras de negócio sem contexto
              externo. Qualquer alteração nas faixas de desconto requer
              localizar os números no código.
Recomendação: Extrair para constantes nomeadas:
              `DESCONTO_ALTO = 0.10; LIMITE_FATURAMENTO_ALTO = 10000`.

================================
Total: 14 achados
================================
```

---
**Gerado em**: 2026-06-22
**Analisador**: skill refactor-arch
**Número do projeto**: 1

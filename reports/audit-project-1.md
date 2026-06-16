# Architecture Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project (Loja API)
Stack:   Python + Flask
Files:   4 analyzed | ~784 lines of code

Summary
CRITICAL: 17 | HIGH: 3 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hardcoded Flask SECRET_KEY
File: app.py:7
Description: A chave secreta do Flask está hardcoded diretamente no código-fonte
             como string literal ("minha-chave-super-secreta-123"), visível a
             qualquer pessoa com acesso ao repositório.
Impact:      Qualquer pessoa com acesso ao código pode forjar tokens de sessão e
             cookies assinados, assumindo a identidade de qualquer usuário,
             incluindo administradores.
Recommendation: Remover o valor do código e carregá-lo via variável de ambiente
                (os.environ.get("SECRET_KEY")) com uma chave aleatória e forte
                gerada para cada ambiente.

[CRITICAL] Endpoint de reset do banco sem autenticação
File: app.py:47
Description: O endpoint POST /admin/reset-db deleta todos os registros de todas
             as tabelas (itens_pedido, pedidos, produtos, usuarios) sem exigir
             qualquer forma de autenticação ou autorização.
Impact:      Qualquer pessoa com acesso de rede à aplicação pode destruir todo o
             banco de dados com uma única requisição HTTP, resultando em perda
             total e irreversível de dados.
Recommendation: Remover este endpoint de produção. Se necessário para manutenção,
                exigir autenticação de administrador via token e restringir acesso
                por IP ou colocar atrás de uma VPN.

[CRITICAL] Endpoint de execução arbitrária de SQL sem autenticação
File: app.py:59
Description: O endpoint POST /admin/query aceita qualquer instrução SQL enviada
             pelo cliente e a executa diretamente contra o banco de dados, sem
             autenticação, sem validação e sem restrição de operação.
Impact:      Qualquer pessoa com acesso de rede pode ler, modificar, inserir ou
             deletar quaisquer dados do banco. Permite exfiltração completa de
             todos os dados, incluindo senhas e informações de usuários, bem como
             destruição total do banco.
Recommendation: Remover este endpoint imediatamente. Não existe caso de uso
                legítimo para expor execução arbitrária de SQL via HTTP.

[CRITICAL] Chave secreta exposta na resposta da API de health check
File: controllers.py:289
Description: A função health_check() retorna o valor da SECRET_KEY da aplicação
             ("minha-chave-super-secreta-123") dentro do payload JSON da resposta
             ao endpoint GET /health, que é publicamente acessível.
Impact:      Qualquer cliente HTTP que acesse /health recebe a chave secreta da
             aplicação, permitindo forjar cookies e tokens de sessão para se passar
             por qualquer usuário.
Recommendation: Remover os campos "secret_key", "debug" e "db_path" da resposta.
                O health check deve retornar apenas status operacional sem
                metadados de configuração interna.

[CRITICAL] Credenciais hardcoded e senhas em texto plano no seed do banco
File: database.py:76
Description: O arquivo de inicialização insere usuários com senhas em texto plano
             hardcoded no código-fonte, incluindo conta de administrador
             ("admin123") e contas de clientes ("123456", "senha123").
Impact:      Qualquer pessoa com acesso ao repositório conhece as credenciais de
             todos os usuários iniciais. Um dump do banco expõe todas as senhas
             diretamente, sem necessidade de quebra de hash.
Recommendation: Usar hashing de senhas (bcrypt ou werkzeug.security) antes de
                armazenar. Remover credenciais hardcoded e usar variáveis de
                ambiente ou processo de seed separado por ambiente.

[CRITICAL] SQL Injection (SELECT) em get_produto_por_id
File: models.py:28
Description: A query SELECT concatena o parâmetro "id" diretamente como string:
             "SELECT * FROM produtos WHERE id = " + str(id).
Impact:      Um atacante que consiga injetar SQL neste SELECT pode ler dados de
             produtos que não está autorizado a ver. Se conseguir anexar cláusulas
             UNION, pode extrair dados de outras tabelas, incluindo senhas e tokens
             — extração não autorizada de dados do sistema para uma parte externa.
Recommendation: Substituir por parâmetro posicional:
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

[CRITICAL] SQL Injection (INSERT) em criar_produto
File: models.py:47
Description: A query INSERT concatena as strings "nome", "descricao" e "categoria"
             diretamente na instrução SQL, sem sanitização ou parametrização.
Impact:      Um atacante pode injetar SQL via campos de texto para inserir registros
             arbitrários no banco, incluindo produtos com dados falsos ou manipulados,
             sem autorização.
Recommendation: Usar parâmetros posicionais:
                cursor.execute("INSERT INTO produtos (nome, descricao, preco,
                estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                (nome, descricao, preco, estoque, categoria))

[CRITICAL] SQL Injection (UPDATE) em atualizar_produto
File: models.py:57
Description: A query UPDATE concatena diretamente os campos "nome", "descricao",
             "categoria" e o ID na instrução SQL sem nenhuma parametrização.
Impact:      Um atacante pode injetar SQL nos campos de texto para modificar
             registros que não deveria poder alterar, ou alterar o predicado WHERE
             para atualizar múltiplos registros ao mesmo tempo, sem autorização.
Recommendation: Usar parâmetros posicionais:
                cursor.execute("UPDATE produtos SET nome=?, descricao=?, preco=?,
                estoque=?, categoria=? WHERE id=?",
                (nome, descricao, preco, estoque, categoria, id))

[CRITICAL] SQL Injection (DELETE) em deletar_produto
File: models.py:68
Description: A query DELETE concatena o parâmetro "id" diretamente na instrução
             SQL: "DELETE FROM produtos WHERE id = " + str(id).
Impact:      Um atacante que consiga manipular o valor de "id" pode deletar
             registros que não deveria poder remover, ou alterar o predicado WHERE
             para deletar múltiplos ou todos os registros da tabela, sem autorização.
Recommendation: Usar parâmetro posicional:
                cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))

[CRITICAL] Senhas retornadas em texto plano nas respostas da API
File: models.py:82
Description: As funções get_todos_usuarios() e get_usuario_por_id() incluem o
             campo "senha" (em texto plano) nos dicionários de retorno, que são
             serializados diretamente para JSON e enviados ao cliente pela API.
Impact:      Qualquer chamada aos endpoints GET /usuarios ou GET /usuarios/{id}
             retorna as senhas de todos os usuários em texto plano, expondo
             credenciais que podem ser usadas para comprometer contas diretamente.
Recommendation: Remover o campo "senha" de todos os dicionários retornados pelas
                funções de leitura de usuários. Senhas nunca devem ser retornadas
                por uma API.

[CRITICAL] SQL Injection (SELECT) em get_usuario_por_id
File: models.py:92
Description: A query SELECT concatena o parâmetro "id" diretamente na instrução:
             "SELECT * FROM usuarios WHERE id = " + str(id).
Impact:      Um atacante pode injetar SQL neste SELECT para ler dados de usuários
             que não está autorizado a ver, incluindo emails e senhas em texto plano.
             Com cláusulas UNION injetadas, pode extrair dados de qualquer tabela,
             configurando extração não autorizada de dados do sistema.
Recommendation: Usar parâmetro posicional:
                cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))

[CRITICAL] SQL Injection (Authentication Bypass) em login_usuario
File: models.py:109
Description: A query de autenticação concatena "email" e "senha" diretamente na
             cláusula WHERE. Esta é uma query de autenticação — o tipo mais perigoso
             de injeção SQL, pois filtra sobre campos de credencial.
Impact:      Um atacante pode ignorar completamente a verificação de senha sem
             precisar conhecer uma senha válida. Com email = "' OR '1'='1' --", a
             condição sempre retorna verdadeiro, concedendo acesso como qualquer
             usuário (frequentemente o administrador) sem autenticação.
Recommendation: Usar parâmetros posicionais:
                cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?",
                (email, senha))
                Além disso, implementar hashing de senhas (bcrypt) para que a
                comparação seja feita sobre o hash, não o texto plano.

[CRITICAL] SQL Injection (INSERT) em criar_usuario
File: models.py:126
Description: A query INSERT concatena "nome", "email", "senha" e "tipo" diretamente
             na instrução SQL sem parametrização.
Impact:      Um atacante pode injetar SQL nos campos de texto para criar usuários com
             dados arbitrários, incluindo definir o tipo como "admin" ou executar
             instruções adicionais no banco de dados, sem autorização.
Recommendation: Usar parâmetros posicionais:
                cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo)
                VALUES (?, ?, ?, ?)", (nome, email, senha, tipo))

[CRITICAL] SQL Injection (SELECT) em criar_pedido
File: models.py:140
Description: Dentro do loop de validação de estoque em criar_pedido, a query SELECT
             concatena item["produto_id"] diretamente: "SELECT * FROM produtos WHERE
             id = " + str(item["produto_id"]).
Impact:      Um atacante pode enviar um produto_id com SQL injetado para ler dados de
             produtos que não deveria acessar, ou com cláusulas UNION extrair dados
             de outras tabelas, incluindo dados de usuários e credenciais.
Recommendation: Usar parâmetro posicional:
                cursor.execute("SELECT * FROM produtos WHERE id = ?",
                (item["produto_id"],))

[CRITICAL] SQL Injection (SELECT) em get_pedidos_usuario
File: models.py:174
Description: A query SELECT concatena "usuario_id" diretamente na instrução:
             "SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id).
Impact:      Um atacante pode injetar SQL via usuario_id para ler pedidos de outros
             usuários que não está autorizado a ver, ou com cláusulas UNION extrair
             dados de qualquer tabela do banco, configurando extração não autorizada
             de dados do sistema.
Recommendation: Usar parâmetro posicional:
                cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?",
                (usuario_id,))

[CRITICAL] SQL Injection (UPDATE) em atualizar_status_pedido
File: models.py:279
Description: A query UPDATE concatena "novo_status" e "pedido_id" diretamente na
             instrução SQL. Embora novo_status seja validado por whitelist no
             controller, a estrutura de concatenação é inerentemente insegura.
Impact:      Um atacante que contorne a validação do controller pode modificar campos
             além do status ou alterar o predicado WHERE para atualizar múltiplos
             pedidos simultaneamente sem autorização.
Recommendation: Usar parâmetros posicionais:
                cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?",
                (novo_status, pedido_id))

[CRITICAL] SQL Injection (Dynamic WHERE Builder) em buscar_produtos
File: models.py:289
Description: A função constrói dinamicamente um SELECT concatenando os parâmetros
             "termo" e "categoria" recebidos diretamente da query string da URL, sem
             qualquer sanitização. Trata-se de um construtor de WHERE dinâmico com
             entrada do usuário não filtrada.
Impact:      Um atacante pode injetar SQL via parâmetros "q" ou "categoria" da URL
             para ler dados que não está autorizado a ver. Com cláusulas UNION
             injetadas via "termo", pode extrair dados de qualquer tabela do banco,
             incluindo senhas e informações de usuários — extração não autorizada de
             dados do sistema para uma parte externa.
Recommendation: Usar lista de condições com placeholders parametrizados:
                conditions = ["1=1"]; params = []
                if termo: conditions.append("(nome LIKE ? OR descricao LIKE ?)")
                          params.extend([f"%{termo}%", f"%{termo}%"])
                if categoria: conditions.append("categoria = ?")
                              params.append(categoria)
                cursor.execute("SELECT * FROM produtos WHERE " +
                " AND ".join(conditions), params)

[HIGH] Lógica de notificações misturada na camada de controller
File: controllers.py:208
Description: A função criar_pedido() contém chamadas simuladas de email, SMS e push
             notification diretamente no fluxo de criação do pedido (linhas 208-210
             e 248-250), usando print() para simular o envio dessas notificações.
Impact:      O controller acumula responsabilidades de orquestração de pedido e
             disparo de notificações. Quando notificações reais forem implementadas,
             o acoplamento tornará impossível testar a lógica de pedido sem simular
             o serviço de notificações, violando o princípio de responsabilidade única.
Recommendation: Extrair toda lógica de notificação para um módulo
                services/notifications.py com funções dedicadas. O controller deve
                apenas chamar o serviço após confirmar a operação com sucesso.

[HIGH] Estado global mutável para conexão com banco de dados
File: database.py:4
Description: A variável global "db_connection = None" e o padrão singleton lazy em
             get_db() compartilham uma única conexão SQLite entre todas as requisições
             da aplicação via estado de módulo mutável.
Impact:      Em ambiente multithread (padrão em produção com Flask), múltiplas
             requisições simultâneas compartilham a mesma conexão, podendo causar
             corrupção de dados, deadlocks ou erros intermitentes difíceis de
             reproduzir. O uso de check_same_thread=False mascara o problema sem
             resolvê-lo.
Recommendation: Usar o objeto flask.g com teardown_appcontext para gerenciar conexões
                por requisição, ou adotar SQLAlchemy com pool de conexões adequado.

[HIGH] Regra de negócio (cálculo de desconto) embutida na camada de acesso a dados
File: models.py:256
Description: A função relatorio_vendas() calcula descontos por faixas de faturamento
             (10%, 5%, 2% para R$10.000, R$5.000 e R$1.000 respectivamente) diretamente
             dentro do modelo de acesso a dados.
Impact:      Regras de negócio na camada de dados violam a separação de
             responsabilidades. Alterar as faixas ou percentuais requer modificar o
             arquivo de acesso a dados, aumentando o risco de regressão e dificultando
             testes unitários da regra de negócio de forma isolada.
Recommendation: Retornar apenas agregados brutos do Model e extrair o cálculo de
                desconto para um módulo services/relatorio_service.py.

[MEDIUM] N+1 queries em get_pedidos_usuario
File: models.py:187
Description: Para cada pedido retornado pela query principal, a função abre dois
             cursores adicionais em loops aninhados: um para buscar os itens do pedido
             (cursor2, linha 188) e outro para buscar o nome de cada produto (cursor3,
             linha 192), resultando em 1 + N + (N×M) queries para N pedidos com M
             itens cada.
Impact:      Para um usuário com 10 pedidos de 5 itens cada, são executadas 61 queries
             ao invés de 1 a 3 com JOINs. Em produção com volume real de dados, causa
             degradação severa de performance e pode derrubar a aplicação sob carga
             moderada.
Recommendation: Substituir os loops aninhados por uma única query com JOINs:
                SELECT p.*, ip.*, pr.nome FROM pedidos p
                JOIN itens_pedido ip ON ip.pedido_id = p.id
                JOIN produtos pr ON pr.id = ip.produto_id
                WHERE p.usuario_id = ?

[MEDIUM] N+1 queries em get_todos_pedidos
File: models.py:219
Description: Idêntico ao problema em get_pedidos_usuario: para cada pedido retornado,
             são abertas queries aninhadas para buscar itens e nomes de produtos,
             multiplicando o número de queries pelo volume de dados em escopo global.
Impact:      Em um banco com 100 pedidos de 10 itens cada, são executadas 1.101
             queries ao invés de 1. Este endpoint lista todos os pedidos de todos os
             usuários, tornando o impacto de performance o mais severo do sistema.
Recommendation: Aplicar a mesma solução com JOIN de get_pedidos_usuario e extrair a
                lógica de serialização para um helper privado _serialize_pedidos(rows)
                reutilizável pelas duas funções.

[MEDIUM] Validação de produto duplicada entre criar_produto e atualizar_produto
File: controllers.py:37
Description: As funções criar_produto() e atualizar_produto() contêm blocos de
             validação quase idênticos: verificação de campos obrigatórios (nome,
             preco, estoque), validação de preco negativo, estoque negativo e
             comprimento do nome (linhas 30-50 e 74-80 respectivamente).
Impact:      Qualquer alteração nas regras de validação precisa ser replicada
             manualmente nos dois lugares, criando risco de inconsistência entre
             criação e atualização do mesmo recurso. A função atualizar_produto já
             omite a validação de comprimento do nome presente em criar_produto.
Recommendation: Extrair a lógica de validação para uma função auxiliar
                _validar_dados_produto(dados) que ambos os handlers chamam,
                eliminando a duplicação e centralizando as regras.

[LOW] Lista de categorias válidas como magic string no controller
File: controllers.py:52
Description: A lista de categorias válidas está hardcoded como literal dentro da
             função criar_produto(): ["informatica", "moveis", "vestuario", "geral",
             "eletronicos", "livros"], sem definição como constante nomeada.
Impact:      A lista não é reutilizada em atualizar_produto (que aceita qualquer
             categoria sem validação), criando inconsistência no sistema. Adicionar
             uma nova categoria requer encontrar e editar a string dentro da lógica
             de negócio.
Recommendation: Definir como constante no topo do módulo:
                CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral",
                "eletronicos", "livros"]
                E reutilizar em todos os pontos de validação.

[LOW] Magic numbers nas faixas de desconto do relatório
File: models.py:256
Description: Os valores de limite de faturamento (10000, 5000, 1000) e os percentuais
             de desconto (0.1, 0.05, 0.02) são usados como literais numéricos sem
             constantes nomeadas que expliquem seu significado ou origem.
Impact:      Um leitor do código não consegue inferir de onde vêm esses valores sem
             contexto externo. Alterar as faixas requer localizar e modificar números
             dispersos no código, com risco de errar um valor.
Recommendation: Definir constantes nomeadas antes da função:
                LIMITE_DESCONTO_ALTO = 10_000; TAXA_DESCONTO_ALTO = 0.10
                LIMITE_DESCONTO_MEDIO = 5_000; TAXA_DESCONTO_MEDIO = 0.05
                LIMITE_DESCONTO_BAIXO = 1_000; TAXA_DESCONTO_BAIXO = 0.02

[LOW] Uso de print() como mecanismo de logging
File: controllers.py:8
Description: O arquivo controllers.py usa print() extensivamente (linhas 8, 11, 57,
             106, 161, 179, 208, 209, 210, 219, 248, 249, 250) para registrar
             operações, erros e notificações, em vez de usar o módulo logging do Python.
Impact:      Mensagens de print() vão para stdout sem timestamp, nível de severidade
             ou capacidade de filtragem. Em produção, não é possível distinguir logs
             de debug de erros críticos, nem redirecionar saída para sistemas de log
             centralizados.
Recommendation: Substituir todos os print() por chamadas ao módulo logging:
                import logging; logger = logging.getLogger(__name__)
                Usar logger.info(), logger.error(), logger.warning() conforme a
                severidade de cada mensagem.

================================
Total: 26 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

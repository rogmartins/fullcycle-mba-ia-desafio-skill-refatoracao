# Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3 + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 4 | HIGH: 6 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hardcoded SECRET_KEY
File: app.py:7
Description: A SECRET_KEY da aplicação está fixa no código-fonte
             ("minha-chave-super-secreta-123") e ainda é exposta na resposta
             do endpoint /health (controllers.py:289).
Impact:      Qualquer pessoa com acesso ao repositório ou ao /health obtém a
             chave usada para assinar sessões/tokens, podendo forjar credenciais.
Recommendation: Mover a chave para variável de ambiente (os.environ) e remover
             qualquer exposição dela em respostas da API.

[CRITICAL] Endpoint de execução de SQL arbitrário
File: app.py:59
Description: O endpoint POST /admin/query recebe uma string SQL do corpo da
             requisição e a executa diretamente no banco, sem autenticação.
Impact:      Permite a um atacante ler, alterar ou apagar qualquer dado do banco
             (controle total da base) — é a exposição completa do banco a um
             terceiro não autorizado.
Recommendation: Remover o endpoint por completo. Operações administrativas devem
             usar consultas específicas e parametrizadas, com autenticação.

[CRITICAL] SQL Injection via concatenação de string (camada de dados)
File: models.py:28
Description: Praticamente todas as queries são montadas concatenando entrada do
             usuário (ex.: get_produto_por_id:28 SELECT, criar_produto:47 INSERT,
             atualizar_produto:57 UPDATE, deletar_produto:68 DELETE,
             buscar_produtos:289 WHERE dinâmico). SQL Injection é a injeção de
             comandos SQL maliciosos por meio de dados de entrada.
Impact:      No SELECT, um atacante pode ler dados não autorizados (inclusive de
             outras tabelas via UNION); nos INSERT/UPDATE/DELETE, pode inserir,
             alterar ou apagar registros sem autorização; no WHERE dinâmico de
             buscar_produtos, combina leitura indevida com manipulação do filtro.
Recommendation: Substituir toda concatenação por queries parametrizadas
             (placeholders ? e tupla de parâmetros), conforme o playbook.

[CRITICAL] SQL Injection na query de autenticação (login)
File: models.py:109
Description: O login monta a query concatenando email e senha diretamente
             ("... WHERE email = '" + email + "' AND senha = '" + senha + "'").
             É uma query de autenticação (filtra por campos de credencial).
Impact:      Um atacante pode burlar a verificação de login sem fornecer uma
             senha válida (ex.: injetando ' OR '1'='1), autenticando-se como
             outro usuário.
Recommendation: Usar query parametrizada e, idealmente, comparar hash de senha
             em vez de texto puro.

[HIGH] Modo debug habilitado em produção
File: app.py:8
Description: DEBUG=True na configuração e debug=True em app.run (app.py:88),
             enquanto /health declara "ambiente": "producao".
Impact:      O debugger interativo do Werkzeug fica exposto, permitindo execução
             de código no servidor em caso de exceção; também vaza stack traces.
Recommendation: Controlar o modo debug por variável de ambiente e mantê-lo
             desligado em produção.

[HIGH] Endpoint destrutivo sem autenticação
File: app.py:47
Description: POST /admin/reset-db apaga todas as tabelas (itens_pedido, pedidos,
             produtos, usuarios) sem qualquer autenticação ou confirmação.
Impact:      Qualquer cliente pode destruir todos os dados da aplicação com uma
             única requisição.
Recommendation: Remover o endpoint ou protegê-lo com autenticação/autorização
             administrativa e confirmação explícita.

[HIGH] Lógica de notificação/infra dentro do controller
File: controllers.py:208
Description: O controller dispara "notificações" (e-mail/SMS/push via print) em
             criar_pedido (208-210) e atualizar_status_pedido (248-250),
             misturando orquestração HTTP com efeitos colaterais de domínio.
Impact:      Controllers deixam de ser apenas orquestradores; a lógica fica
             difícil de testar e reutilizar, e acoplada ao ciclo de requisição.
Recommendation: Extrair para um serviço de notificação chamado pela camada de
             Model/serviço, fora do controller.

[HIGH] Conexão global mutável compartilhada entre threads
File: database.py:4
Description: db_connection é um singleton global (database.py:4) aberto com
             check_same_thread=False (database.py:10) e compartilhado por toda a
             aplicação.
Impact:      Estado global mutável compartilhado entre requisições/threads pode
             causar condições de corrida e corrupção de dados sob concorrência.
Recommendation: Encapsular o acesso ao banco em uma camada de conexão por
             requisição (ou pool) e injetá-la onde necessário.

[HIGH] Armazenamento de senhas em texto puro
File: database.py:76
Description: O seed grava senhas em texto puro (database.py:76-78) e o login
             compara texto puro (models.py:110).
Impact:      Vazamento do banco expõe diretamente as senhas dos usuários;
             ausência de hashing é uma falha grave de segurança de credenciais.
Recommendation: Armazenar apenas hash com salt (ex.: bcrypt/argon2) e comparar
             o hash no login.

[HIGH] Exposição de senha nas respostas da API
File: models.py:83
Description: get_todos_usuarios (models.py:83) e get_usuario_por_id
             (models.py:99) incluem o campo "senha" no dicionário retornado pela
             API.
Impact:      As senhas dos usuários são devolvidas em endpoints HTTP, expondo
             dados sensíveis a qualquer consumidor da API.
Recommendation: Nunca serializar o campo senha; criar um serializer/DTO que
             exponha apenas campos públicos.

[HIGH] Ausência de camada de Model real
File: models.py:1
Description: models.py é um conjunto de funções procedurais com SQL cru,
             sem entidades nem abstração de persistência; regras de negócio
             (cálculo de total e desconto) convivem com o acesso a dados.
Impact:      Acoplamento forte entre regras de negócio e SQL, baixa testabilidade
             e duplicação de acesso a dados espalhada.
Recommendation: Introduzir Models por entidade (Produto, Usuario, Pedido) que
             encapsulem persistência e regras, conforme mvc-patterns.md.

[MEDIUM] Validação duplicada entre controllers
File: controllers.py:30
Description: Os blocos de validação de produto são repetidos quase idênticos em
             criar_produto (30-54) e atualizar_produto (74-90).
Impact:      Duplicação dificulta manutenção: uma regra alterada precisa ser
             mudada em vários pontos, com risco de divergência.
Recommendation: Extrair a validação para uma função/serviço único reutilizado
             por ambos os handlers.

[MEDIUM] N+1 queries na montagem de pedidos
File: models.py:187
Description: get_pedidos_usuario (187-193) e get_todos_pedidos (219-225) executam
             uma query por item e outra por produto dentro de loops aninhados.
Impact:      O número de consultas cresce linearmente com itens/pedidos,
             degradando a performance conforme o volume aumenta.
Recommendation: Substituir por uma única consulta com JOIN (produtos/itens) e
             montar os objetos em memória.

[MEDIUM] Lógica de leitura de pedidos duplicada
File: models.py:203
Description: get_todos_pedidos (203-233) é praticamente idêntica a
             get_pedidos_usuario (171-201), diferindo apenas pelo filtro.
Impact:      Duplicação de lógica de leitura aumenta o custo de manutenção e o
             risco de inconsistência entre as duas funções.
Recommendation: Unificar em uma única função parametrizada pelo filtro opcional
             de usuário.

[LOW] Strings mágicas de categorias e status
File: controllers.py:52
Description: Listas de categorias válidas (controllers.py:52) e de status
             válidos (controllers.py:242) estão embutidas como literais.
Impact:      Valores de domínio espalhados como literais dificultam reuso e
             evolução; mudanças exigem caçar ocorrências.
Recommendation: Centralizar em constantes nomeadas (ou enum) reutilizadas pelos
             handlers e models.

[LOW] Dados sensíveis na resposta do /health
File: controllers.py:285
Description: O /health retorna secret_key, db_path e debug (controllers.py:285-289).
Impact:      Informação interna e sensível é exposta a qualquer consumidor do
             endpoint de saúde.
Recommendation: Reduzir o /health a status/contadores não sensíveis.

[LOW] Números mágicos no cálculo de desconto
File: models.py:257
Description: Os limiares e percentuais de desconto (10000/5000/1000 e
             0.1/0.05/0.02) estão embutidos em relatorio_vendas (models.py:257-262).
Impact:      Regras de negócio difíceis de localizar e ajustar; sem nome que
             explique a intenção.
Recommendation: Extrair para constantes nomeadas com significado de negócio.

================================
Total: 16 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---
**Generated**: 2026-06-22
**Analyzer**: refactor-arch skill
**Project number**: 1

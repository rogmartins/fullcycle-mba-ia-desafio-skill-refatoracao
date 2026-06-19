# Audit Report — code-smells-project

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

Summary
CRITICAL: 10 | HIGH: 5 | MEDIUM: 5 | LOW: 4

Findings

[CRITICAL] Hardcoded SECRET_KEY
File: app.py:7
Description: A SECRET_KEY da aplicação está escrita diretamente no código-fonte
             ("minha-chave-super-secreta-123").
Impact:      Qualquer pessoa com acesso ao repositório consegue forjar sessões e
             tokens assinados pela aplicação, pois a chave secreta deixa de ser
             secreta.
Recommendation: Mover a chave para uma variável de ambiente lida via os.environ
             e nunca versionar o valor real.

[CRITICAL] Endpoint de execução de SQL arbitrário
File: app.py:59
Description: A rota /admin/query recebe uma string SQL do corpo da requisição e a
             executa diretamente no banco, sem autenticação.
Impact:      Um atacante pode ler, alterar ou apagar qualquer dado do banco
             (execução de comandos SQL arbitrários — qualquer comando enviado é
             rodado sem restrição), comprometendo toda a base de dados.
Recommendation: Remover o endpoint. Acesso administrativo a dados deve usar
             operações específicas e autenticadas, nunca SQL livre.

[CRITICAL] SECRET_KEY exposta na resposta de health-check
File: controllers.py:289
Description: O endpoint /health devolve no JSON a secret_key, o debug e o ambiente
             da aplicação.
Impact:      A chave secreta é entregue a qualquer cliente que chame /health,
             expondo publicamente um segredo que permite forjar sessões.
Recommendation: Remover secret_key/debug do payload de health; retornar apenas
             status e contadores.

[CRITICAL] Senhas armazenadas e retornadas em texto puro
File: database.py:76
Description: Os usuários são semeados com senhas em texto puro e o endpoint
             GET /usuarios (models.get_todos_usuarios) devolve o campo senha.
Impact:      Vazamento direto de credenciais: qualquer um que liste usuários lê
             as senhas reais, e um vazamento do banco expõe todas as senhas.
Recommendation: Aplicar hash nas senhas (ex.: werkzeug/bcrypt) e nunca incluir o
             campo senha em respostas da API.

[CRITICAL] SQL Injection — SELECT por id
File: models.py:28
Description: get_produto_por_id monta a query concatenando o id na string SQL
             ("... WHERE id = " + str(id)).
Impact:      Operação SELECT: um atacante pode ler dados que não deveria ver e,
             encadeando cláusulas (ex.: UNION), ler dados de outras tabelas como
             senhas — extração não autorizada de dados do sistema.
Recommendation: Usar query parametrizada (placeholders ? e tupla de parâmetros).

[CRITICAL] SQL Injection — consulta de autenticação
File: models.py:109
Description: login_usuario concatena email e senha diretamente na cláusula WHERE.
Impact:      Consulta de autenticação: um atacante pode burlar a verificação de
             login sem fornecer uma senha válida (ex.: injetando ' OR '1'='1).
Recommendation: Parametrizar a consulta e comparar hash de senha, nunca texto.

[CRITICAL] SQL Injection — INSERT
File: models.py:48
Description: criar_produto (e criar_usuario em models.py:126) montam o INSERT
             concatenando os valores recebidos do usuário.
Impact:      Operação INSERT: um atacante pode inserir registros não autorizados
             ou corromper a inserção com dados forjados.
Recommendation: Usar INSERT parametrizado com placeholders.

[CRITICAL] SQL Injection — UPDATE
File: models.py:58
Description: atualizar_produto monta o UPDATE concatenando valores e id.
Impact:      Operação UPDATE: um atacante pode modificar registros sem
             autorização, alterando dados que não deveria.
Recommendation: Usar UPDATE parametrizado.

[CRITICAL] SQL Injection — DELETE
File: models.py:68
Description: deletar_produto concatena o id na cláusula DELETE.
Impact:      Operação DELETE: um atacante pode apagar registros sem autorização.
Recommendation: Usar DELETE parametrizado.

[CRITICAL] SQL Injection — construtor dinâmico de WHERE
File: models.py:289
Description: buscar_produtos concatena termo, categoria e faixas de preço numa
             cláusula WHERE montada em tempo de execução.
Impact:      Construtor dinâmico de WHERE: combina risco de leitura não
             autorizada (os parâmetros injetáveis alimentam um SELECT), podendo
             expor dados de outras tabelas.
Recommendation: Construir a query com placeholders e lista de parâmetros.

[HIGH] Debug mode habilitado em produção
File: app.py:8
Description: app.config["DEBUG"]=True e debug=True no app.run, com /health
             reportando ambiente "producao".
Impact:      O debugger do Flask expõe stack traces e um console interativo que
             permite execução de código se uma exceção ocorrer em produção.
Recommendation: Controlar debug por variável de ambiente, desligado por padrão.

[HIGH] Endpoint administrativo destrutivo sem autenticação
File: app.py:47
Description: /admin/reset-db apaga todas as tabelas sem qualquer autenticação.
Impact:      Qualquer cliente pode zerar o banco inteiro com uma única chamada.
Recommendation: Proteger rotas administrativas com autenticação/autorização.

[HIGH] Efeitos colaterais de notificação acoplados ao controller
File: controllers.py:208
Description: O envio de email/SMS/push está implementado como prints dentro de
             criar_pedido (controller).
Impact:      Lógica de notificação misturada à orquestração HTTP dificulta teste,
             reuso e troca do canal de notificação.
Recommendation: Extrair um serviço de notificação injetável, chamado pela camada
             de negócio.

[HIGH] Estado global mutável de conexão com o banco
File: database.py:4
Description: db_connection é uma variável global única, com
             check_same_thread=False, compartilhada por toda a aplicação.
Impact:      Conexão única compartilhada entre threads gera condições de corrida
             e acoplamento global difícil de testar e isolar.
Recommendation: Gerenciar conexão por requisição/contexto e injetá-la nas
             funções de dados.

[HIGH] Regras de negócio dentro da camada de dados
File: models.py:133
Description: criar_pedido valida estoque, calcula total e atualiza estoque
             diretamente na camada de acesso a dados.
Impact:      Mistura de regra de negócio com acesso a dados impede reuso e teste
             isolado das regras e viola a separação de responsabilidades.
Recommendation: Separar uma camada de serviço para a regra de pedido, deixando o
             model apenas com persistência.

[MEDIUM] Validação de produto duplicada entre controllers
File: controllers.py:24
Description: criar_produto (linha 24) e atualizar_produto (linha 64) repetem o
             mesmo bloco de validação de campos.
Impact:      Duplicação aumenta o custo de manutenção e o risco de as regras
             divergirem entre criar e atualizar.
Recommendation: Extrair uma função única de validação de produto reutilizável.

[MEDIUM] Ausência de validação de formato de entrada
File: controllers.py:146
Description: criar_usuario (146) e login (167) não validam formato de email nem
             tamanho mínimo de senha.
Impact:      Dados inválidos chegam à camada de persistência sem checagem,
             gerando registros inconsistentes.
Recommendation: Validar formato de email e regras de senha antes de persistir.

[MEDIUM] Estrutura dos itens do pedido não validada
File: controllers.py:188
Description: criar_pedido aceita "itens" sem validar a presença de produto_id e
             quantidade em cada item.
Impact:      Itens malformados só falham na camada de dados, com mensagens de
             erro pouco claras.
Recommendation: Validar a estrutura de cada item antes de chamar a camada de
             negócio.

[MEDIUM] Consultas N+1 na listagem de pedidos
File: models.py:187
Description: get_pedidos_usuario (187) e get_todos_pedidos (219) executam uma
             query por item de cada pedido para buscar o nome do produto.
Impact:      Número de queries cresce com a quantidade de itens, degradando a
             performance conforme o volume aumenta.
Recommendation: Usar JOIN ou uma única query com IN para carregar os nomes.

[MEDIUM] Lógica de listagem de pedidos duplicada
File: models.py:171
Description: get_pedidos_usuario (171) e get_todos_pedidos (203) são quase
             idênticas, diferindo apenas no filtro.
Impact:      Duplicação dificulta manutenção e propaga o mesmo problema de N+1.
Recommendation: Unificar numa função parametrizada pelo filtro.

[LOW] Lista de categorias e limites de nome mágicos
File: controllers.py:47
Description: Tamanhos mínimo/máximo de nome (2/200) e a lista de categorias
             válidas estão embutidos no controller (linhas 47-52).
Impact:      Valores mágicos espalhados dificultam manutenção e reuso.
Recommendation: Extrair constantes nomeadas.

[LOW] Strings de status mágicas embutidas
File: controllers.py:242
Description: A lista de status válidos do pedido está embutida na verificação.
Impact:      Repetição de literais sem nome dificulta evolução dos estados.
Recommendation: Definir os status como constantes/enum.

[LOW] Logging via print com concatenação de string
File: controllers.py:8
Description: O código usa print("..." + str(...)) como log em vários pontos.
Impact:      Logging não estruturado e ruidoso, sem níveis nem destino
             configurável.
Recommendation: Usar o módulo logging com níveis apropriados.

[LOW] Números mágicos no cálculo de desconto
File: models.py:257
Description: relatorio_vendas usa limiares (10000/5000/1000) e taxas
             (0.1/0.05/0.02) sem nome.
Impact:      Regras de desconto pouco legíveis e difíceis de ajustar.
Recommendation: Extrair constantes nomeadas para limiares e taxas.

================================
Total: 24 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

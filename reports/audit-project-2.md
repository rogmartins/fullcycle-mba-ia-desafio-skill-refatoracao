# Audit Report — ecommerce-api-legacy

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 4

Findings

[CRITICAL] God Class AppManager
File: src/AppManager.js:4
Description: AppManager concentra criação do banco, seeds, definição de rotas,
             regra de negócio, pagamento e auditoria em uma única classe.
Impact:      Toda a aplicação depende de uma classe que faz tudo, impossível de
             testar e manter por partes; qualquer mudança arrisca o sistema todo.
Recommendation: Separar em camadas (config, models, services, controllers,
             routes) com responsabilidade única por arquivo.

[CRITICAL] Número de cartão e chave do gateway em log
File: src/AppManager.js:45
Description: O handler imprime no console o número completo do cartão e a chave do
             gateway de pagamento.
Impact:      Dados sensíveis de pagamento (cartão completo) e o segredo do gateway
             vazam para os logs, expondo dados de clientes e permitindo uso
             indevido da chave de cobrança.
Recommendation: Nunca logar o cartão; mascarar (apenas últimos 4 dígitos) e
             manter a chave fora dos logs.

[CRITICAL] Credenciais hardcoded
File: src/utils.js:1
Description: dbUser, dbPass, paymentGatewayKey e smtpUser estão escritos no código
             (config) com valores de produção.
Impact:      Senha de banco e chave de pagamento de produção ficam visíveis a
             qualquer um com acesso ao repositório.
Recommendation: Ler todos os segredos de variáveis de ambiente; nunca versionar.

[CRITICAL] Hashing de senha quebrado e senha em texto puro
File: src/utils.js:17
Description: badCrypto gera um "hash" concatenando base64 e truncando em 10 chars;
             o seed grava a senha do usuário em texto puro ('123').
Impact:      As senhas ficam efetivamente sem proteção, triviais de reverter, e
             um vazamento do banco expõe as credenciais dos usuários.
Recommendation: Usar um algoritmo de hash com sal (ex.: scrypt/bcrypt do módulo
             crypto) e nunca gravar senha em texto puro.

[HIGH] Regra de negócio dentro do handler de rota
File: src/AppManager.js:28
Description: O checkout valida, cobra, matricula, registra pagamento e auditoria
             tudo dentro do handler da rota.
Impact:      Regra de negócio acoplada ao transporte HTTP impede reuso e teste
             isolado do fluxo de checkout.
Recommendation: Extrair um checkoutService chamado por um controller fino.

[HIGH] Ausência de camada Model
File: src/AppManager.js:11
Description: Todas as queries SQL estão espalhadas diretamente nos handlers, sem
             uma camada de acesso a dados.
Impact:      Sem Model, o acesso a dados é duplicado e não há ponto único para
             evoluir/otimizar consultas.
Recommendation: Criar models (user, course, enrollment, payment) que encapsulem
             o acesso ao banco.

[HIGH] Operações de checkout sem transação
File: src/AppManager.js:50
Description: Matrícula, pagamento e auditoria são gravados em callbacks aninhados
             sem transação atômica.
Impact:      Uma falha no meio do fluxo deixa o banco inconsistente (ex.:
             matrícula sem pagamento).
Recommendation: Executar o checkout em uma transação (BEGIN/COMMIT/ROLLBACK).

[HIGH] Gateway de pagamento fake acoplado inline
File: src/AppManager.js:46
Description: A "aprovação" do pagamento é decidida por card.startsWith("4")
             embutido no handler.
Impact:      Lógica de pagamento acoplada e não substituível dificulta integrar
             um gateway real ou testar cenários.
Recommendation: Isolar um paymentGateway injetável com interface única.

[HIGH] Estado global mutável compartilhado
File: src/utils.js:9
Description: globalCache e totalRevenue são variáveis globais mutáveis
             compartilhadas entre componentes.
Impact:      Estado global gera acoplamento oculto e comportamento imprevisível
             sob concorrência.
Recommendation: Encapsular cache/estado em um módulo com interface explícita.

[MEDIUM] N+1 no relatório financeiro
File: src/AppManager.js:89
Description: O relatório percorre cursos, para cada curso percorre matrículas e,
             para cada matrícula, faz uma query de usuário e outra de pagamento.
Impact:      O número de queries cresce multiplicativamente com os dados,
             degradando a performance.
Recommendation: Usar JOIN/agregação em uma ou poucas consultas.

[MEDIUM] Registros órfãos ao deletar usuário
File: src/AppManager.js:131
Description: DELETE /api/users/:id apaga o usuário mas deixa matrículas e
             pagamentos no banco (o próprio retorno admite isso).
Impact:      Dados ficam inconsistentes e o relatório passa a exibir "Unknown".
Recommendation: Remover em cascata (ou bloquear o delete) dentro de uma transação.

[MEDIUM] Falta de validação de entrada
File: src/AppManager.js:28
Description: O checkout não valida formato de email nem do cartão.
Impact:      Dados inválidos chegam ao fluxo de pagamento/persistência sem
             checagem.
Recommendation: Validar email e cartão antes de processar.

[MEDIUM] Tratamento de erro inconsistente/ignorado
File: src/AppManager.js:57
Description: Erros do insert de auditoria e do delete de usuário são ignorados.
Impact:      Falhas silenciosas escondem problemas e dificultam o diagnóstico.
Recommendation: Tratar e propagar erros de forma consistente.

[MEDIUM] Formato de resposta inconsistente
File: src/AppManager.js:35
Description: Respostas misturam texto puro ("Bad Request", "Curso não encontrado")
             e JSON.
Impact:      Clientes precisam tratar formatos diferentes por rota, aumentando o
             acoplamento.
Recommendation: Padronizar respostas (ex.: sempre JSON com { error } / { data }).

[LOW] Nomes de variáveis sem significado
File: src/AppManager.js:29
Description: Variáveis u, e, p, cid, cc no checkout.
Impact:      Código difícil de ler e manter.
Recommendation: Renomear para nomes descritivos (nome, email, senha, courseId,
             card).

[LOW] Números e strings mágicos
File: src/AppManager.js:46
Description: Prefixo "4" para aprovar cartão e o laço de 10000 em badCrypto sem
             constantes nomeadas.
Impact:      Valores mágicos dificultam o entendimento das regras.
Recommendation: Extrair constantes nomeadas.

[LOW] console.log usado como logging
File: src/AppManager.js:45
Description: Logs feitos com console.log direto, inclusive de dados sensíveis.
Impact:      Logging não estruturado e sem níveis.
Recommendation: Usar um logger com níveis e sem dados sensíveis.

[LOW] Import não utilizado
File: src/AppManager.js:2
Description: totalRevenue é importado mas nunca usado.
Impact:      Código morto que confunde a leitura.
Recommendation: Remover imports não utilizados.

================================
Total: 18 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

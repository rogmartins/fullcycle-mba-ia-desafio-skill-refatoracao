```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express.js + SQLite3
Files:   3 analyzed | ~180 lines of code

Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 3

Findings

[CRITICAL] Hardcoded Credentials in Source Code
File: src/utils.js:1
Description: Credenciais sensíveis de produção estão literalmente escritas no código
             fonte: senha do banco de dados (`dbPass: "senha_super_secreta_prod_123"`),
             chave live do gateway de pagamento (`paymentGatewayKey: "pk_live_1234567890abcdef"`),
             credencial de SMTP e nome de usuário do banco. Qualquer pessoa com acesso
             ao repositório tem acesso imediato a esses segredos.
Impact:      Comprometimento imediato de sistemas externos em caso de vazamento do
             repositório (acidental ou mal-intencionado). A chave `pk_live_` indica
             ambiente de produção real — transações financeiras reais podem ser afetadas.
Recommendation: Mover todas as credenciais para variáveis de ambiente (`.env`) usando
                biblioteca como `dotenv`. Nunca versionar valores sensíveis; adicionar
                `.env` ao `.gitignore` e revogar imediatamente as chaves expostas.

[CRITICAL] Armazenamento Inseguro de Senhas (badCrypto)
File: src/utils.js:17
Description: A função `badCrypto` simula criptografia, mas na prática aplica codificação
             Base64 repetida e truncada à senha do usuário. Base64 é reversível — não é
             um algoritmo de hash. Qualquer senha armazenada com essa função pode ser
             decodificada trivialmente por qualquer pessoa com acesso ao banco de dados.
Impact:      Se o banco de dados for comprometido, todas as senhas de usuários podem ser
             recuperadas em texto claro. Isso viola os requisitos básicos de proteção de
             dados (LGPD, OWASP ASVS) e expõe os usuários a ataques de reutilização de
             credencial em outros sistemas. A função usa o próprio nome `badCrypto`,
             indicando ciência do problema sem correção.
Recommendation: Substituir `badCrypto` pelo algoritmo `bcrypt` (pacote `bcryptjs`) com
                fator de custo mínimo 12, ou `argon2` (pacote `argon2`). Atualizar a
                rota de login para comparar usando `bcrypt.compare()` em vez de comparação
                direta.

[CRITICAL] God Class — AppManager Concentra Toda a Aplicação
File: src/AppManager.js:1
Description: A classe `AppManager` (141 linhas) acumula simultaneamente: inicialização
             do banco de dados, registro de rotas Express, lógica de negócio (checkout,
             processamento de pagamento, criação de usuário, matrícula), lógica de
             auditoria e geração de relatório financeiro. É um arquivo que faz tudo
             sozinho, sem nenhuma separação de responsabilidades.
Impact:      Qualquer mudança em qualquer parte do sistema exige alterar esta única
             classe, criando conflitos constantes em times, dificultando testes unitários
             (impossível testar a lógica de pagamento sem subir o Express e o banco) e
             tornando a adição de novas funcionalidades cada vez mais arriscada.
Recommendation: Extrair responsabilidades em camadas MVC: criar `models/` para acesso
                a dados (UserModel, CourseModel, EnrollmentModel, PaymentModel), `controllers/`
                para orquestração de requisições (CheckoutController, FinancialController,
                UserController) e `routes/` para registro das rotas Express. AppManager
                deve ser eliminado.

[HIGH] Lógica de Negócio Complexa Dentro de Route Handlers
File: src/AppManager.js:28
Description: O handler da rota `POST /api/checkout` (linhas 28–78) contém toda a lógica
             de domínio embutida: busca de curso, busca/criação de usuário, decisão de
             aprovação de pagamento (cc.startsWith), criação de matrícula, registro de
             pagamento e log de auditoria. O mesmo ocorre em `GET /api/admin/financial-report`
             (linhas 80–129) com a geração do relatório.
Impact:      Controladores com lógica de negócio são impossíveis de testar sem simular
             toda a infraestrutura Express. A regra de negócio de "cartão começa com 4 =
             aprovado" está misturada com infraestrutura HTTP, tornando impossível
             reutilizá-la ou alterá-la sem mexer nas rotas.
Recommendation: Extrair a lógica de checkout para um serviço (`services/CheckoutService.js`)
                e a lógica de relatório para (`services/FinancialService.js`). Os controllers
                devem apenas receber o request, chamar o serviço e retornar o response.

[HIGH] Ausência de Camada Model — Queries Espalhadas nos Handlers
File: src/AppManager.js:37
Description: Não existe nenhuma camada de modelo (Model) na aplicação. Todas as queries
             SQL são escritas diretamente dentro dos route handlers em `setupRoutes()`:
             SELECT de cursos, INSERT de usuários, INSERT de matrículas, INSERT de
             pagamentos, SELECT de relatório — tudo misturado com código Express.
Impact:      Duplicação inevitável ao adicionar novas rotas que precisem dos mesmos
             dados; impossibilidade de trocar o banco de dados sem reescrever toda a
             lógica de negócio; queries não testáveis isoladamente.
Recommendation: Criar arquivos de modelo em `src/models/`: `UserModel.js`, `CourseModel.js`,
                `EnrollmentModel.js`, `PaymentModel.js`. Cada model encapsula as queries
                do seu domínio e recebe a instância do banco via injeção de dependência.

[HIGH] Acoplamento Forte — Sem Injeção de Dependência
File: src/AppManager.js:7
Description: O banco de dados SQLite é instanciado diretamente no construtor de
             `AppManager` (`new sqlite3.Database(':memory:')`), criando acoplamento
             direto e irreversível. As funções utilitárias também são importadas como
             módulo estático. Não há interfaces ou abstrações entre as camadas.
Impact:      É impossível substituir o banco de dados para testes sem modificar a classe.
             Impossível mockar dependências para testar comportamentos isolados. O código
             de produção e o de teste precisam compartilhar o mesmo banco `:memory:`,
             o que pode causar interferências.
Recommendation: Receber a instância do banco como parâmetro no construtor
                (`constructor(db)`) e usar a instância injetada. Isso possibilita passar
                um banco de teste nos testes e o banco real em produção.

[HIGH] Estado Global Mutável Compartilhado
File: src/utils.js:9
Description: As variáveis `globalCache` (objeto) e `totalRevenue` (número) são definidas
             com `let` no escopo de módulo em `utils.js` e exportadas. São mutadas pela
             função `logAndCache()` chamada durante o checkout. `totalRevenue` é exportado
             mas nunca utilizado, indicando código morto com estado global.
Impact:      Em ambiente com múltiplas requisições concorrentes, o cache global pode
             causar condições de corrida (race conditions), retornando dados de uma
             requisição para outra. Dificulta testes pois o estado persiste entre casos
             de teste.
Recommendation: Substituir o cache global por uma solução de cache com escopo controlado
                (ex: Map local no serviço, Redis, ou módulo de cache com interface limpa).
                Remover `totalRevenue` que está sem uso.

[MEDIUM] N+1 Queries no Relatório Financeiro
File: src/AppManager.js:89
Description: O handler de `GET /api/admin/financial-report` executa queries aninhadas
             em callbacks: 1 query para todos os cursos, depois para cada curso uma query
             de matrículas, e para cada matrícula duas queries (usuário e pagamento).
             Com N cursos e M matrículas por curso, são executadas 1 + N + 2×(N×M) queries.
Impact:      Com volume crescente de dados (ex: 50 cursos, 200 alunos cada), esse endpoint
             pode facilmente executar milhares de queries por requisição, tornando o
             relatório inutilizável em produção e sobrecarregando o banco de dados.
Recommendation: Substituir por uma query com JOIN que busque cursos, matrículas, usuários
                e pagamentos em uma única operação:
                `SELECT c.title, u.name, u.email, p.amount, p.status
                 FROM courses c
                 LEFT JOIN enrollments e ON e.course_id = c.id
                 LEFT JOIN users u ON u.id = e.user_id
                 LEFT JOIN payments p ON p.enrollment_id = e.id`

[MEDIUM] Validação de Entrada Ausente ou Insuficiente na Rota de Checkout
File: src/AppManager.js:35
Description: A rota `POST /api/checkout` verifica apenas se os campos existem (truthy),
             mas não valida o formato: `e` (email) não é validado como e-mail, `cid` não
             é validado como número inteiro, `cc` (cartão) não é validado quanto ao
             comprimento mínimo. O campo `p` (senha) não é checado e recebe default
             `"123456"` silenciosamente caso ausente.
Impact:      Entradas malformadas chegam diretamente ao banco de dados e à lógica de
             pagamento. A senha padrão silenciosa pode criar usuários com senha "123456"
             sem que o usuário saiba, comprometendo a segurança das contas.
Recommendation: Usar biblioteca de validação como `joi` ou `zod` para definir esquemas
                de entrada. Validar: formato de e-mail, `cid` como inteiro positivo,
                tamanho mínimo de cartão, e exigir senha explícita sem fallback silencioso.

[MEDIUM] Dados Órfãos na Exclusão de Usuário
File: src/AppManager.js:131
Description: A rota `DELETE /api/users/:id` executa apenas `DELETE FROM users WHERE id = ?`,
             sem remover ou tratar as matrículas e pagamentos associados ao usuário.
             O próprio código reconhece o problema no response: "matrículas e pagamentos
             ficaram sujos no banco."
Impact:      O banco acumula registros de matrículas e pagamentos sem referência válida
             de usuário (dados órfãos), corrompendo a integridade referencial. Relatórios
             financeiros exibirão entradas com `student: 'Unknown'` indefinidamente.
Recommendation: Usar transação para deletar em cascata (`enrollments` → `payments` →
                `users`) ou configurar `FOREIGN KEY` com `ON DELETE CASCADE` no SQLite
                (`PRAGMA foreign_keys = ON`).

[LOW] Nomes de Variáveis sem Significado
File: src/AppManager.js:29
Description: As variáveis locais no handler de checkout são de letra única: `u` (nome
             do usuário), `e` (e-mail), `p` (senha), `cid` (id do curso), `cc` (número
             do cartão). O alias `self` (linha 26) também é desnecessário em contextos
             onde arrow functions já preservam o `this`.
Impact:      Código difícil de ler e revisar. Um revisor precisa voltar à definição
             para entender o que cada variável representa.
Recommendation: Renomear para nomes descritivos: `userName`, `email`, `password`,
                `courseId`, `cardNumber`. Remover `self` e usar arrow functions
                consistentemente.

[LOW] Valores Mágicos sem Constantes Nomeadas
File: src/AppManager.js:46
Description: A lógica de aprovação de pagamento usa `cc.startsWith("4")` — o valor `"4"`
             é um número mágico sem documentação (representa cartões Visa). Os status
             de pagamento `"PAID"` e `"DENIED"` são strings literais repetidas em vários
             pontos sem uma constante central.
Impact:      Se a regra mudar (ex: adicionar cartões Mastercard que começam com "5"),
             é necessário buscar todas as ocorrências manualmente, com risco de esquecimento.
Recommendation: Criar constantes nomeadas:
                `const VISA_PREFIX = "4"`, `const PAYMENT_STATUS = { PAID: "PAID", DENIED: "DENIED" }`
                e referenciá-las no código.

[LOW] Seed Data com Senha em Texto Claro
File: src/AppManager.js:18
Description: O script de inicialização do banco insere o usuário de seed com senha
             literal `'123'` em texto claro na coluna `pass`. Mesmo sendo dado de
             demonstração, reforça o padrão incorreto de armazenamento de senhas.
Impact:      Desenvolvedores novos podem assumir que este é o padrão esperado pela
             aplicação para armazenar senhas. Em ambientes onde o banco é persistente
             (não `:memory:`), o seed expõe uma credencial real.
Recommendation: Aplicar a mesma função de hash segura (após substituir `badCrypto`) no
                seed data, ou usar uma senha de seed obfuscada apenas para demonstração.

================================
Total: 13 findings
================================
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

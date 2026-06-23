```
================================
ARCHITECTURE AUDIT REPORT
================================
Project:  ecommerce-api-legacy
Stack:    Node.js + Express 4.18.2
Files:    3 analyzed | ~181 lines of code

Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 2 | LOW: 2

Findings

[CRITICAL] Credenciais Hardcoded no Código-Fonte
File: src/utils.js:2
Description:    O objeto `config` contém credenciais reais de produção
              diretamente no código-fonte: senha do banco (`dbPass`),
              chave de gateway de pagamento (`paymentGatewayKey`) e
              usuário administrador (`dbUser`).
Impact:      Qualquer pessoa com acesso ao repositório obtém credenciais
              de produção válidas — incluindo a chave `pk_live_*` do
              gateway de pagamento, que permite processar ou estornar
              cobranças reais.
Recommendation: Mover todas as credenciais para variáveis de ambiente e
              ler via `process.env.DB_PASS`, `process.env.PAYMENT_KEY`.
              Nunca versionar segredos.

[CRITICAL] Algoritmo de Hash de Senha Ineficaz
File: src/utils.js:17
Description:    A função `badCrypto` usa codificação Base64 iterada e
              truncada como substituta de hash de senha. Base64 é
              reversível — não é uma função de hash criptográfico.
Impact:      Senhas armazenadas no banco podem ser recuperadas em texto
              puro por qualquer pessoa com acesso ao banco ou ao código.
              Toda a base de usuários fica vulnerável a exposição imediata
              caso o banco seja comprometido.
Recommendation: Substituir por `bcrypt` ou `argon2`:
              `const hash = await bcrypt.hash(pwd, 12)`. Invalidar e
              redefinir todas as senhas existentes após a migração.

[CRITICAL] Classe Deus — AppManager concentra toda a aplicação
File: src/AppManager.js:4
Description:    A classe `AppManager` concentra em um único arquivo:
              definição de rotas, lógica de pagamento, criação de usuário,
              matrícula em curso, inserção de log de auditoria e acesso
              direto ao banco — violação completa de separação de
              responsabilidades.
Impact:      Impossível testar qualquer comportamento de forma isolada.
              Qualquer mudança em uma responsabilidade arrisca quebrar
              as demais. O crescimento natural do sistema torna o arquivo
              incontrolável.
Recommendation: Decompor em camadas MVC: Model para acesso ao banco,
              Controller para orquestração de requisições e Services para
              regras de negócio (pagamento, matrícula).

[HIGH] Lógica de Negócio no Handler de Rota — Checkout
File: src/AppManager.js:43
Description:    O handler de `/api/checkout` contém a lógica de negócio de
              pagamento (aprovação por prefixo de cartão), criação de
              usuário e matrícula diretamente no callback de rota.
Impact:      Regras de negócio misturadas com infraestrutura HTTP impedem
              reutilização e tornam o teste de cada regra dependente de
              uma requisição HTTP real.
Recommendation: Extrair para `PaymentService.process(card, amount)` e
              `EnrollmentService.enroll(userId, courseId)`. O controller
              apenas chama os serviços e retorna a resposta.

[HIGH] Deleção de Usuário sem Integridade Referencial
File: src/AppManager.js:131
Description:    O endpoint `DELETE /api/users/:id` remove o usuário mas não
              remove nem desvincula os registros em `enrollments` e
              `payments`, deixando dados órfãos no banco. A resposta
              inclusive admite isso explicitamente na mensagem de retorno.
Impact:      Relatórios financeiros e de matrículas passam a incluir
              dados de usuários inexistentes, comprometendo a integridade
              dos dados e podendo causar erros em futuras consultas.
Recommendation: Implementar deleção em cascata via `ON DELETE CASCADE` nas
              chaves estrangeiras, ou realizar a remoção em transação:
              deletar pagamentos → matrículas → usuário.

[HIGH] Camada de Model Ausente — Acesso ao Banco nos Handlers
File: src/AppManager.js:36
Description:    Todas as queries ao banco estão embutidas diretamente nos
              callbacks de rota, sem nenhuma camada de abstração de dados.
Impact:      Qualquer mudança no esquema do banco requer buscar e editar
              SQL em vários pontos do mesmo arquivo. Impossível trocar o
              banco de dados sem reescrever os handlers.
Recommendation: Criar módulos `models/User.js`, `models/Course.js`,
              `models/Enrollment.js` e `models/Payment.js`, cada um
              encapsulando as queries da sua entidade.

[HIGH] Estado Global Mutável — Cache e Variável de Receita
File: src/utils.js:9
Description:    As variáveis `globalCache` e `totalRevenue` são declaradas
              no escopo do módulo e compartilhadas entre todas as
              requisições da aplicação.
Impact:      Em ambiente com múltiplas requisições simultâneas, condições
              de corrida podem corromper o cache ou a contagem de receita.
              `totalRevenue` é exportada mas nunca atualizada nos handlers,
              tornando-a sempre 0 — dado silenciosamente incorreto.
Recommendation: Eliminar `globalCache` e `totalRevenue` globais. Cache deve
              ser por-requisição ou gerenciado por um serviço dedicado.
              Receita deve ser calculada via query ao banco.

[MEDIUM] Queries N+1 — Relatório Financeiro
File: src/AppManager.js:83
Description:    Para cada curso, o relatório busca suas matrículas; para
              cada matrícula, busca o usuário e o pagamento — resultando
              em 1 + N + N×2 queries para N matrículas por curso.
Impact:      Com 10 cursos e 20 alunos cada, o endpoint dispara ~401
              queries onde uma única query com JOINs resolveria. Em
              produção, o endpoint torna-se inoperante com volume real.
Recommendation: Substituir por uma única query com JOIN entre `courses`,
              `enrollments`, `users` e `payments`, agrupando os resultados
              em memória.

[MEDIUM] Validação de Entrada Ausente — Checkout
File: src/AppManager.js:28
Description:    O endpoint `/api/checkout` verifica apenas a presença dos
              campos (não nulos), sem validar tipos, formatos ou tamanhos:
              `c_id` não é verificado como inteiro, `eml` não é validado
              como email, `card` não tem verificação de formato.
Impact:      Entradas malformadas podem causar comportamento inesperado
              no banco ou na lógica de pagamento sem mensagem de erro
              clara para o cliente.
Recommendation: Adicionar validação de tipos e formatos antes de qualquer
              acesso ao banco: verificar que `c_id` é número inteiro
              positivo, `eml` contém `@`, `card` tem comprimento mínimo.

[LOW] Nomes de Variáveis sem Significado
File: src/AppManager.js:29
Description:    As variáveis `u`, `e`, `p`, `cid` e `cc` representam,
              respectivamente, nome de usuário, email, senha, ID do curso
              e número de cartão — nenhum desses significados é legível
              no código.
Impact:      Qualquer manutenção do handler de checkout requer que o
              desenvolvedor deduza o significado de cada abreviação
              antes de poder raciocinar sobre o código.
Recommendation: Renomear para `userName`, `email`, `password`, `courseId`
              e `cardNumber`.

[LOW] Strings Mágicas — Lógica de Aprovação de Cartão
File: src/AppManager.js:46
Description:    A regra de aprovação de pagamento `cc.startsWith("4")`
              encoda a detecção de cartão Visa como uma string mágica
              sem nenhuma constante ou comentário que explique a regra.
Impact:      Impossível entender ou alterar a lógica de aprovação sem
              conhecimento externo. Adicionar suporte a Mastercard
              (prefixo "5") exige caçar e entender o literal no código.
Recommendation: Extrair para constante nomeada: `const VISA_PREFIX = "4"`
              e mover a regra de aprovação para o `PaymentService`.

================================
Total: 11 findings
================================
```

---
**Generated on**: 2026-06-22
**Analyzer**: skill refactor-arch
**Project number**: 2

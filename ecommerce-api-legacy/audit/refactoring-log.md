# Refactoring Log — ecommerce-api-legacy

## [CRITICAL] Hardcoded Credentials
- Original file: src/utils.js : 1–6
- Target file:   src/config/env.js + .env
- Action: extracted
- Reason: Credenciais de DB, gateway de pagamento e SMTP movidas para variáveis de ambiente via dotenv. .env adicionado ao .gitignore.

## [CRITICAL] Armazenamento Inseguro de Senhas (badCrypto)
- Original file: src/utils.js : 17–23
- Target file:   src/controllers/CheckoutController.js + src/database/db.js
- Action: replaced
- Reason: Função badCrypto (base64 reversível) substituída por bcryptjs com fator de custo 12. Hash aplicado no checkout e no seed de inicialização.

## [CRITICAL] God Class — AppManager
- Original file: src/AppManager.js : 1–141
- Target file:   src/database/db.js, src/models/*.js, src/controllers/*.js, src/routes/index.js
- Action: extracted
- Reason: Classe única com 141 linhas fatiada em responsabilidades MVC separadas. AppManager.js removido.

## [HIGH] Lógica de Negócio em Route Handlers
- Original file: src/AppManager.js : 28–129
- Target file:   src/controllers/CheckoutController.js, src/controllers/FinancialController.js
- Action: extracted
- Reason: Toda lógica de domínio (validação, criação de usuário, processamento de pagamento, geração de relatório) movida para controllers dedicados.

## [HIGH] Ausência de Camada Model
- Original file: src/AppManager.js : 37–133
- Target file:   src/models/UserModel.js, src/models/CourseModel.js, src/models/EnrollmentModel.js, src/models/PaymentModel.js, src/models/AuditLogModel.js
- Action: extracted
- Reason: Todas as queries SQL encapsuladas em models por domínio com injeção de dependência do banco.

## [HIGH] Acoplamento Forte — Sem Injeção de Dependência
- Original file: src/AppManager.js : 7
- Target file:   src/routes/index.js, src/database/db.js
- Action: fixed
- Reason: Instância do banco criada em db.js e injetada em todos os models e controllers via parâmetro de construtor.

## [HIGH] Estado Global Mutável
- Original file: src/utils.js : 9–10
- Target file:   (removed)
- Action: removed
- Reason: globalCache e totalRevenue removidos. Cache de checkout eliminado (dado não exposto na API). totalRevenue era código morto.

## [MEDIUM] N+1 Queries no Relatório Financeiro
- Original file: src/AppManager.js : 89–128
- Target file:   src/models/EnrollmentModel.js (getFinancialReport), src/controllers/FinancialController.js
- Action: fixed
- Reason: Callbacks aninhados com queries individuais por curso/matrícula substituídos por um único JOIN abrangendo cursos, matrículas, usuários e pagamentos.

## [MEDIUM] Validação de Entrada Insuficiente
- Original file: src/AppManager.js : 35
- Target file:   src/controllers/CheckoutController.js
- Action: fixed
- Reason: Adicionadas validações de formato de e-mail (regex), courseId como inteiro positivo, cardNumber com mínimo 13 dígitos e senha obrigatória explícita (mínimo 6 caracteres) sem fallback silencioso.

## [MEDIUM] Dados Órfãos na Exclusão de Usuário
- Original file: src/AppManager.js : 131–137
- Target file:   src/controllers/UserController.js
- Action: fixed
- Reason: DELETE em cascata implementado: payments → enrollments → user. FOREIGN KEY constraints adicionados ao schema do banco.

## [LOW] Nomes de Variáveis sem Significado
- Original file: src/AppManager.js : 29–34
- Target file:   src/controllers/CheckoutController.js
- Action: renamed
- Reason: u→userName, e→email, p→password, cid→courseId, cc→cardNumber via desestruturação. self removido com uso consistente de arrow functions.

## [LOW] Valores Mágicos sem Constantes Nomeadas
- Original file: src/AppManager.js : 46
- Target file:   src/config/constants.js
- Action: extracted
- Reason: "4" extraído como VISA_BIN_PREFIX; "PAID"/"DENIED" agrupados em PAYMENT_STATUS object. Referenciados em todos os controllers.

## [LOW] Seed Data com Senha em Texto Claro
- Original file: src/AppManager.js : 18
- Target file:   src/database/db.js
- Action: fixed
- Reason: Senha do usuário seed '123' agora hasheada com bcrypt.hashSync antes da inserção.

## 1. Análise Manual 

**1.1** **Projeto:**  `code-smells-project`

**1.1.1. Problema 1**

- **Descrição:**  Acesso direto ao banco de dados no Controller, sem uso do  Model)
- **Localização:** `controllers.py::health_check()`, linhas 264–292
- **Trecho do código:**
```python
def health_check():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    ...
```
-  **Princípio violado :** Controllers não devem acessar a camada de dados diretamente. Todo acesso ao banco deve passar pelo Model.
- **Motivo da violação:**  O controller `health_check()` importa e usa `get_db()` diretamente para executar queries SQL. No MVC, o Controller não deve conhecer a implementação de persistência — isso é responsabilidade exclusiva do Model. Além disso, o response deste endpoint expõe dados sensíveis de infraestrutura (`secret_key`, `db_path`, `debug: true`), o que é uma falha de segurança adicional.
- **Severidade:** `HIGH`

---
**1.1.2. Problema 2** 

- **Descrição:** `models.py::relatorio_vendas()` exige modificação para cada novo nível de desconto
- **Localização:** `models.py`, linhas 256–261
- **Trecho do código:**
```python
desconto = 0
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

- **Princípio violado:** OCP — Open/Closed Principle - "Software entities should be open for extension, but closed for modification." (Bertrand Meyer / Robert C. Martin). 
- **Motivo da violação:** A lógica de desconto usa uma cadeia `if/elif` com valores e percentuais *hardcoded*. Para adicionar um novo nível (ex.: acima de R$ 50.000 → 15%), é necessário modificar a função existente, violando o OCP. O correto seria extrair os níveis para uma estrutura de dados configurável ou implementar uma estratégia (`DiscountStrategy`) que pode ser estendida **sem alterar o código** que calcula o relatório.
- **Severidade:** `MEDIUM`

---
**1.1.3. Problema 3**

- **Descrição:**  Problema de **N+1 queries** em `get_pedidos_usuario()` e `get_todos_pedidos()`
- **Localização:** `models.py` linhas 171–201,  e  linhas 203–233
- **Trecho do código:**
```python
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?")   # 1 query
    for row in rows:
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?")  # N queries
        for item in itens:
            cursor3.execute("SELECT nome FROM produtos WHERE id = ?")      # M queries
```

- **Princípio violado:** MVC — Model com implementação **ineficiente**
- **Motivo da violação:**  Para cada pedido retornado, são executadas N queries de itens e M queries de produtos adicionais (N+1 clássico). Para um usuário com 10 pedidos e 5 itens por pedido, isso gera 1 + 10 + 50 = 61 queries ao banco. No MVC correto, o Model deve ser eficiente: a solução é usar um `JOIN` único:
- **Severidade:** `MEDIUM`

---
**1.1.4. Problema 4**

- **Descrição:** Magic strings para status de pedido espalhadas pelo código
- **Localização:** `controllers.py` linhas 242, 247–250 — `models.py` linhas 148, 247, 251, 254
- **Trecho do código:**
```python
# controllers.py
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
    ...
if novo_status == "aprovado":
    print("NOTIFICAÇÃO: Pedido aprovado! Preparar envio.")
if novo_status == "cancelado":
    print("NOTIFICAÇÃO: Pedido cancelado. Devolver estoque.")

# models.py
cursor.execute("INSERT INTO pedidos ... VALUES (..., 'pendente', ...)")
cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
```
- **Princípio violadao** OCP — Open/Closed Principle
- **Motivo da violação:** Os valores de status são strings literais duplicadas em pelo menos 4 locais diferentes. Adicionar um novo status (ex.: `"devolvido"`) exige modificar múltiplos arquivos (`controllers.py`, `models.py`), violando OCP. 
- **Severidade:** `LOW`

---
**1.1.5. Problema 5**

- **Descrição:**  `print()` usado como sistema de logging
- **Localização:** `controllers.py` linhas 8, 57, 106, 161, 179, 209–210, 219 — `database.py` linha 56
- **Trecho do código:**
```python
# controllers.py
print("Listando " + str(len(produtos)) + " produtos")
print("Produto criado com ID: " + str(id))
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " ...")
print("ERRO CRITICO ao criar pedido: " + str(e))

# database.py
print("!!! BANCO DE DADOS RESETADO !!!")
```
- **Princípio violado:** SRP  — Single Responsibility Principle + boas práticas de observabilidade
- **Motivo da violação:** `print()` é usado em todo o código como substituto de um sistema de logging real. Isso viola o SRP porque o controller assume a responsabilidade de decidir como registrar eventos de sistema. Além disso, `print()` não oferece níveis de severidade (DEBUG, INFO, WARNING, ERROR), não pode ser redirecionado para arquivos ou sistemas externos (ex.: Sentry, Datadog) e não é thread-safe em produção. O correto seria usar o módulo `logging` do Python com um logger configurável, separando a responsabilidade de observabilidade dos controllers.
- **Severidade:** `LOW`

---
**1.2. Projeto:**  `ecommerce-api-legacy`

**1.2.1. Problema 1**

- **Descrição**: classe AppManager acumula as responsabilidades:
	- Inicialização e migração do banco de dados (`initDb`)
	- Definição e registro das rotas HTTP (`setupRoutes`)
	- Lógica de negócio (checkout, matrícula, pagamento, criação de usuário)
	- Geração de relatório financeiro
- **Localização:** `src/AppManager.js` — classe `AppManager` **inteira**
- **Princípio violado:** SRP  — Single Responsibility Principle
- **Motivo da violação:** Ausência de separação de camadas. Todo o código foi escrito em um **único objeto**, o que dificulta as manutenções evolutivas e corretivas, pois para qualquer alteração nesse código há o risco de regressões em funcionalidades não relacionadas e que não apresentavam erros.
 - **Severidade:** `CRITICAL`
 ---
**1.2.2 Problema 2**

- **Descrição:**  O Controller deve validar entrada e a View (resposta HTTP) não deve expor detalhes internos de implementação ou bugs.
- **Localização:** `src/AppManager.js`, linhas 131–137
- **Trecho do código:**
```js
app.delete('/api/users/:id', (req, res) => {
    let id = req.params.id;
    this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
    });
});
```
- **Princípio violado:**   Ausência de padronização e validação.  
- **Motivo da violação:**  Rota de deleção sem validação e com mensagem de bug exposta na View.  O handler não verifica se o usuário existe antes de deletar, não trata erros de banco (`err` é ignorado), e retorna uma mensagem que expõe um defeito de integridade referencial ao cliente final. Em MVC, a View (resposta) deve apresentar apenas informação relevante e segura; detalhes de implementação interna — especialmente bugs conhecidos — jamais devem ser expostos na camada de apresentação.
- **Severidade:** `MEDIUM`

---
**1.2.3. Problema 3**

- **Descrição:** Falta de **separação de camadas** por causa de vários callbacks aninhados, que dificulta a distinção das responsabilidades do **controller** e do **model**.
- **Localização:** `src/AppManager.js`, linhas 37–77 e 83–128
- **Trecho do código:**
```javascript
            this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [cid], (err, course) => {
                if (err || !course) return res.status(404).send("Curso não encontrado");

                this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
                    if (err) return res.status(500).send("Erro DB");

                    let processPaymentAndEnroll = (userId) => {

                        console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
                        let status = cc.startsWith("4") ? "PAID" : "DENIED";

                        if (status === "DENIED") return res.status(400).send("Pagamento recusado");

                        this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, cid], function(err) {
                            if (err) return res.status(500).send("Erro Matrícula");
                            let enrId = this.lastID;

                            self.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrId, course.price, status], function(err) {
                                if (err) return res.status(500).send("Erro Pagamento");

                                self.db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [`Checkout curso ${cid} por ${userId}`], (err) => {
                                    
                                    logAndCache(`last_checkout_${userId}`, course.title);
                                    res.status(200).json({ msg: "Sucesso", enrollment_id: enrId });
                                });
                            });
                        });
                    };

                    if (!user) {

                        let hash = badCrypto(p || "123456");
                        this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [u, e, hash], function(err) {
                            if (err) return res.status(500).send("Erro ao criar usuário");
                            processPaymentAndEnroll(this.lastID);
                        });
                    } else {
                        processPaymentAndEnroll(user.id);
                    }
                });
            });
```

- **Princípio violado:**  Falta de separação em camadas
- **Motivo da violação:** O handler de `/api/checkout` possui 5 níveis de callbacks aninhados (`db.get` → `db.get` → função interna → `db.run` → `db.run` → `db.run`). O handler de `/api/admin/financial-report` possui 4 níveis. Além de dificultar a leitura, esse padrão torna impossível distinguir onde termina a responsabilidade do Controller e onde começaria a do Model. Em MVC, cada camada deve ser identificável e substituível; aqui elas estão fundidas em uma cadeia de closures. O problema é primariamente de legibilidade e manutenção — não há falha de segurança ou quebra funcional direta associada ao aninhamento em si.
- **Severidade:** `MEDIUM`

---
**1.2.4. Problema 4**

- **Descrição:** Nomes de variáveis sem significado no handler de checkout
- **Localização:** `src/AppManager.js`, linhas 29–33
- **Trecho do código:**
```js
let u = req.body.usr;
let e = req.body.eml;
let p = req.body.pwd;
let cid = req.body.c_id;
let cc = req.body.card;
```
- **Princípio violado:** legibilidade
- **Motivo da violação:**  Nomes de variáveis sem semântica clara. Todas as variáveis que recebem os campos da requisição usam abreviações de 1–3 letras sem semântica clara (`u` para usuário, `e` para e-mail, `p` para senha, `cid` para course ID, `cc` para número do cartão). Ao longo do handler, `cc` aparece em verificações de pagamento, `e` é passada para queries SQL e `cid` é interpolada em strings de log — em nenhum momento o leitor sabe sem esforço o que cada variável representa. Nomes como `userName`, `email`, `password`, `courseId` e `cardNumber` eliminariam a ambiguidade sem nenhum custo de performance.
- **Severidade:** `LOW`

---
**1.2.5. Problema 5**

- **Descrição:** Uso de `const self = this` misturado com arrow functions no mesmo escopo
- **Localização:** `src/AppManager.js`, linha 26 e linhas 50–57
- **Trecho do código:**
```js
const self = this;   

// ... dentro do mesmo método, arrow functions já capturam `this` corretamente:
this.db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {  
    let enrId = this.lastID;
    self.db.run("INSERT INTO payments ...", ...);                           
    self.db.run("INSERT INTO audit_logs ...", ...);                         
});
```
- **Princípio violado:** legibilidade
- **Motivo da violação:**  O mesmo método ora usa `this.db`, ora usa `self.db`, sem critério — tornando desnecessariamente difícil saber a qual objeto cada chamada se refere, violando o princípio da menor surpresa.
- **Severidade:** `LOW`

---
**1.3. Projeto:**  `task-manager-api`

**1.3.1. Problema 1**

- **Descrição:** Credenciais hardcoded no `NotificationService`
- **Localização:** `services/notification_service.py`, linhas 8–10
- **Trecho do código:**
```python
self.email_host = 'smtp.gmail.com'
self.email_port = 587
self.email_user = 'taskmanager@gmail.com'
self.email_password = 'senha123'       # ← credencial hardcoded
```
- **Princípio violado:**  Single Responsibility Principle 
- **Motivo da violação:**  A classe `NotificationService` acumula duas responsabilidades distintas: (1) gerenciar a configuração de infraestrutura de email (host, porta, credenciais) e (2) executar o envio de notificações. O SRP determina que uma classe deve ter apenas uma responsabilidade. Adicionalmente, o código apresenta credencial e parâmetros de configuração hardcoded.
- **Severidade:**  CRITICAL

---
**1.3.2 Problema 2**

- **Descrição:**  Lógica de cálculo `overdue` duplicada em Controller, Model e Blueprint de relatórios
- **Localizações:**
	- `models/task.py:50–60` — método `is_overdue()` (correto, no Model)
	- `routes/task_routes.py:30–39` — duplicado inline em `get_tasks()`
	- `routes/task_routes.py:71–80` — duplicado inline em `get_task()`
	- `routes/user_routes.py:171–180` — duplicado inline em `get_user_tasks()`
	- `routes/task_routes.py:283–287` — duplicado inline em `task_stats()`
	- `routes/report_routes.py:33–37` — duplicado inline em `summary_report()`
- **Trecho do código:**
```python
# Mesma lógica repetida 5 vezes fora do Model:
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            # overdue = True
```
- **Camada violada:** Model / Controller 
- **Motivo da violação:**  No MVC, regras de domínio pertencem ao Model. O método `task.is_overdue()` existe e está correto, mas nenhum Controller o utiliza — todos reimplementam a mesma lógica inline. Isso viola o princípio de separação de responsabilidades do MVC: o Model possui o comportamento, mas o Controller ignora-o e reimplementa. Qualquer bug nessa lógica (ex: considerar fuso horário) exige correção em 6 lugares.
- **Severidade:**  MEDIUM

---
**1.3.3. Problema 3**

- **Descrição:**  Serialização duplicada e inconsistente entre Model e Controllers (View)
- **Localizações:**
	- `models/task.py:23–36` — `Task.to_dict()` define serialização canônica
	- `routes/task_routes.py:17–29` — controller monta dict manualmente com campos diferentes
	- `routes/user_routes.py:163–170` — controller monta dict manual sem `tags`, sem `category_id`
- **Trecho do código:**
```python
    for t in tasks:
        task_data = {}
        task_data['id'] = t.id
        task_data['title'] = t.title
        task_data['description'] = t.description
        task_data['status'] = t.status
        task_data['priority'] = t.priority
        task_data['created_at'] = str(t.created_at)
        task_data['due_date'] = str(t.due_date) if t.due_date else None
```
- **Camada violada:** Model / View 
- **Motivo da violação:**  O Model `Task` define `to_dict()` como método de serialização, mas `get_tasks()` ignora esse método e constrói seu próprio dicionário manualmente — com campos adicionais (`overdue`, `user_name`, `category_name`) e sem utilizar o método existente. `get_user_tasks()` em `user_routes.py` faz o mesmo, mas omite campos diferentes (`tags`, `category_id`, `updated_at`). O resultado são três representações distintas do mesmo recurso `Task` dependendo de qual endpoint é chamado, sem nenhuma padronização de schema para a View.
- **Severidade:**  MEDIUM

---
**1.3.4 Problema 4**

- **Descrição:** Constantes de domínio definidas mas nunca utilizadas (OCP / DRY)
- **Localização:** `utils/helpers.py`, linhas 110–116
- **Trecho do código:**
```python
VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'
```
- **Princípio violado:**  Open/Closed Principle  - OCP
- **Motivo da violação:**  As constantes foram declaradas com a intenção clara de centralizar valores de domínio, mas nenhum módulo as importa ou utiliza. Em `task_routes.py:110`, `task_routes.py:177`, `user_routes.py:71` e outros pontos, os mesmos literais (`'pending'`, `'in_progress'`, `4`, `200`) aparecem diretamente no código como *magic numbers/strings*. O OCP pressupõe que extensões de comportamento não exijam modificação em múltiplos pontos — o que só é possível se as constantes centralizadas forem efetivamente consumidas. A presença das constantes sem uso sugere que foram adicionadas como intenção, mas jamais aplicadas, deixando o problema em aberto. Também dificulta a leitura: o desenvolvedor que lê `helpers.py` acredita que os valores estão centralizados, mas na prática cada validação usa seu próprio literal.
- **Severidade:**  LOW

---
**1.3.5 Problema 5**

- **Descrição:** Nomes de variáveis sem significado e cláusulas `except` que não mostram o que houve, no Controller
- **Localizações:**
	- `routes/report_routes.py:24–28` — variáveis `p1`, `p2`, `p3`, `p4`, `p5`
	- `routes/task_routes.py:62` — `except:` sem tipo de exceção
	- `routes/task_routes.py:138` — `except:` sem tipo de exceção
	- `routes/user_routes.py:130` — `except:` sem tipo de exceção
	- `routes/report_routes.py:187` — `except:` sem tipo de exceção
- **Trecho do código:**
```python
# report_routes.py:24–28 — nomes sem semântica
p1 = Task.query.filter_by(priority=1).count()
p2 = Task.query.filter_by(priority=2).count()
p3 = Task.query.filter_by(priority=3).count()
p4 = Task.query.filter_by(priority=4).count()
p5 = Task.query.filter_by(priority=5).count()

# Múltiplos controllers — captura silenciosa de qualquer exceção
except:
    db.session.rollback()
    return jsonify({'error': 'Erro ao criar task'}), 500
```
- **Princípio violado:**  Nomes sem semântica + captura silenciosa de exceções
- **Motivo da violação:**  No MVC, os Controllers são a camada de orquestração mais lida pela equipe de desenvolvimento. Nomes como `p1`–`p5` não comunicam a semântica de domínio (`critical`, `high`, `medium`, `low`, `minimal`), forçando o leitor a cruzar o código com o dicionário de resposta JSON para entender o que cada variável representa. O padrão `except` sem especificar o tipo de exceção silencia erros inesperados — incluindo `KeyboardInterrupt`, `SystemExit` e erros de programação — tornando debugging extremamente difícil em produção. Erros de lógica passam despercebidos pois são tratados da mesma forma que erros de banco de dados esperados. Isso compromete a legibilidade e a rastreabilidade do Controller, afetando diretamente a manutenibilidade da camada de orquestração MVC.
- **Severidade:**  LOW

## 1. Análise Manual 

**1.1** **Projeto:**  `code-smells-project`

**1.1.1. Problema 1**

- **Descrição:**  Acesso direto ao banco de dados no Controller, sem uso do  Model)
- **Arquivo/linhas:** `controllers.py::health_check()`, linhas 264–292
- **Severidade:** `HIGH`
- **Regra MVC:** Controllers não devem acessar a camada de dados diretamente. Todo acesso ao banco deve passar pelo Model.

**Código problemático:**
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

**Motivo da violação:**
O controller `health_check()` importa e usa `get_db()` diretamente para executar queries SQL. No MVC, o Controller não deve conhecer a implementação de persistência — isso é responsabilidade exclusiva do Model. Além disso, o response deste endpoint expõe dados sensíveis de infraestrutura (`secret_key`, `db_path`, `debug: true`), o que é uma falha de segurança adicional.

---
**1.1.2. Problema 2** 

- **Descrição:** `models.py::relatorio_vendas()` exige modificação para cada novo nível de desconto
- **Princípio violado:** OCP — Open/Closed Principle
- **Arquivo/linhas:** `models.py`, linhas 256–261
- **Severidade:** `MEDIUM`

**Princípio:**
"Software entities should be open for extension, but closed for modification." (Bertrand Meyer / Robert C. Martin). 

**Código problemático:**
```python
desconto = 0
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

**Motivo da violação:**
A lógica de desconto usa uma cadeia `if/elif` com valores e percentuais *hardcoded*. Para adicionar um novo nível (ex.: acima de R$ 50.000 → 15%), é necessário modificar a função existente, violando o OCP. O correto seria extrair os níveis para uma estrutura de dados configurável ou implementar uma estratégia (`DiscountStrategy`) que pode ser estendida **sem alterar o código** que calcula o relatório.

---
**1.1.3. Problema 3**

**Descrição:**  Problema de **N+1 queries** em `get_pedidos_usuario()` e `get_todos_pedidos()`
**Princípio/Regra violada:** MVC — Model com implementação **ineficiente**
**Arquivo/linhas:** `models.py` linhas 171–201,  e  linhas 203–233
**Severidade:** `MEDIUM`

**Código problemático:**
```python
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?")   # 1 query
    for row in rows:
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?")  # N queries
        for item in itens:
            cursor3.execute("SELECT nome FROM produtos WHERE id = ?")      # M queries
```

**Motivo da violação:**
Para cada pedido retornado, são executadas N queries de itens e M queries de produtos adicionais (N+1 clássico). Para um usuário com 10 pedidos e 5 itens por pedido, isso gera 1 + 10 + 50 = 61 queries ao banco. No MVC correto, o Model deve ser eficiente: a solução é usar um `JOIN` único:

```sql
SELECT p.*, ip.*, pr.nome
FROM pedidos p
JOIN itens_pedido ip ON ip.pedido_id = p.id
JOIN produtos pr ON pr.id = ip.produto_id
WHERE p.usuario_id = ?
```


---
**1.1.4. Problema 4**

- **Descrição:** Magic strings para status de pedido espalhadas pelo código
- **Princípio/Regra violada:** OCP — Open/Closed Principle
- **Arquivo/linhas:** `controllers.py` linhas 242, 247–250 — `models.py` linhas 148, 247, 251, 254
- **Severidade:** `LOW`

**Código problemático:**
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

**Motivo da violação:**
Os valores de status são strings literais duplicadas em pelo menos 4 locais diferentes. Adicionar um novo status (ex.: `"devolvido"`) exige modificar múltiplos arquivos (`controllers.py`, `models.py`), violando OCP. A solução é centralizar os valores em um `Enum` ou constantes:

```python
class StatusPedido(str, Enum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
```

---
**1.1.5. Problema 5**

- **Descrição:**  `print()` usado como sistema de logging
- **Princípio/Regra violada:** SRP  — Single Responsibility Principle + boas práticas de observabilidade
- **Arquivo/linhas:** `controllers.py` linhas 8, 57, 106, 161, 179, 209–210, 219 — `database.py` linha 56
- **Severidade:** `LOW`

**Código problemático:**
```python
# controllers.py
print("Listando " + str(len(produtos)) + " produtos")
print("Produto criado com ID: " + str(id))
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " ...")
print("ERRO CRITICO ao criar pedido: " + str(e))

# database.py
print("!!! BANCO DE DADOS RESETADO !!!")
```

**Motivo da violação:**
`print()` é usado em todo o código como substituto de um sistema de logging real. Isso viola o SRP porque o controller assume a responsabilidade de decidir como registrar eventos de sistema. Além disso, `print()` não oferece níveis de severidade (DEBUG, INFO, WARNING, ERROR), não pode ser redirecionado para arquivos ou sistemas externos (ex.: Sentry, Datadog) e não é thread-safe em produção. O correto seria usar o módulo `logging` do Python com um logger configurável, separando a responsabilidade de observabilidade dos controllers.

---
**1.2. Projeto:**  `ecommerce-api-legacy`

**1.2.1. Problema 1**

- **Descrição**: classe AppManager acumula as responsabilidades:
	- Inicialização e migração do banco de dados (`initDb`)
	- Definição e registro das rotas HTTP (`setupRoutes`)
	- Lógica de negócio (checkout, matrícula, pagamento, criação de usuário)
	- Geração de relatório financeiro
- **Princípio/Regra violada:** SRP  — Single Responsibility Principle
- **Localização:** `src/AppManager.js` — classe `AppManager` inteira
- **Severidade:** `CRITICAL`

 **Motivo da violação:** Ausência de separação de camadas. Todo o código foi escrito em um **único objeto**, o que dificulta as manutenções evolutivas e corretivas, pois para qualquer alteração nesse código há o risco de regressões em funcionalidades não relacionadas e que não apresentavam erros.
 
 ---
**1.2.2 Problema 2**

- **Descrição:** Rota de deleção sem validação e com mensagem de bug exposta na View.  O handler não verifica se o usuário existe antes de deletar, não trata erros de banco (`err` é ignorado), e retorna uma mensagem que expõe um defeito de integridade referencial ao cliente final. Em MVC, a View (resposta) deve apresentar apenas informação relevante e segura; detalhes de implementação interna — especialmente bugs conhecidos — jamais devem ser expostos na camada de apresentação. A **ausência de validação de entrada** e o **tratamento incorreto de erros** enquadram-se na categoria de problemas de padronização e validação ausente nas rotas.
- **Regra MVC violada:** O Controller deve validar entrada e a View (resposta HTTP) não deve expor detalhes internos de implementação ou bugs.
- **Localização:** `src/AppManager.js`, linhas 131–137
- **Severidade:** `MEDIUM`

```js
app.delete('/api/users/:id', (req, res) => {
    let id = req.params.id;
    this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
    });
});
```

---
**1.2.3. Problema 3**

- **Descrição:** Falta de **separação de camadas** por causa de vários callbacks aninhados, que dificulta a distinção das responsabilidades do **controller** e do **model**.
- **Localização:** `src/AppManager.js`, linhas 37–77 e 83–128
- **Severidade:** `MEDIUM`

**Motivo da violação:** O handler de `/api/checkout` possui 5 níveis de callbacks aninhados (`db.get` → `db.get` → função interna → `db.run` → `db.run` → `db.run`). O handler de `/api/admin/financial-report` possui 4 níveis. Além de dificultar a leitura, esse padrão torna impossível distinguir onde termina a responsabilidade do Controller e onde começaria a do Model. Em MVC, cada camada deve ser identificável e substituível; aqui elas estão fundidas em uma cadeia de closures. O problema é primariamente de legibilidade e manutenção — não há falha de segurança ou quebra funcional direta associada ao aninhamento em si.

---
**1.2.4. Problema 4**

- **Descrição:** Nomes de variáveis sem significado no handler de checkout
- **Localização:** `src/AppManager.js`, linhas 29–33
```js
let u = req.body.usr;
let e = req.body.eml;
let p = req.body.pwd;
let cid = req.body.c_id;
let cc = req.body.card;
```
- **Severidade:** `LOW`

**Motivo da violação:**  Nomes de variáveis sem semântica clara.
Todas as variáveis que recebem os campos da requisição usam abreviações de 1–3 letras sem semântica clara (`u` para usuário, `e` para e-mail, `p` para senha, `cid` para course ID, `cc` para número do cartão). Ao longo do handler, `cc` aparece em verificações de pagamento, `e` é passada para queries SQL e `cid` é interpolada em strings de log — em nenhum momento o leitor sabe sem esforço o que cada variável representa. Nomes como `userName`, `email`, `password`, `courseId` e `cardNumber` eliminariam a ambiguidade sem nenhum custo de performance.

---
**1.2.5. Problema 5**

- **Descrição:** Uso de `const self = this` misturado com arrow functions no mesmo escopo
- **Localização:** `src/AppManager.js`, linha 26 e linhas 50–57
```js
const self = this;   

// ... dentro do mesmo método, arrow functions já capturam `this` corretamente:
this.db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {  
    let enrId = this.lastID;
    self.db.run("INSERT INTO payments ...", ...);                           
    self.db.run("INSERT INTO audit_logs ...", ...);                         
});
```
- **Severidade:** `LOW`

**Motivo da violação:**  O mesmo método ora usa `this.db`, ora usa `self.db`, sem critério — tornando desnecessariamente difícil saber a qual objeto cada chamada se refere, violando o princípio da menor surpresa.

---
**1.3. Projeto:**  `task-manager-api`

**1.3.1. Problema 1**

- **Descrição:** Credenciais hardcoded no `NotificationService`
- **Localização:** `services/notification_service.py`, linhas 8–10
```python
self.email_host = 'smtp.gmail.com'
self.email_port = 587
self.email_user = 'taskmanager@gmail.com'
self.email_password = 'senha123'       # ← credencial hardcoded
```
- **Princípio violado:**  Single Responsibility Principle 
- **Severidade:**  CRITICAL
- **Motivo da violação:**  A classe `NotificationService` acumula duas responsabilidades distintas: (1) gerenciar a configuração de infraestrutura de email (host, porta, credenciais) e (2) executar o envio de notificações. O SRP determina que uma classe deve ter apenas uma responsabilidade. Adicionalmente, o código apresenta credencial e parâmetros de configuração hardcoded.

---
**1.3.2 Problema 2**

- **Descrição:**  Lógica de cálculo `overdue` duplicada em Controller, Model e Blueprint de relatórios


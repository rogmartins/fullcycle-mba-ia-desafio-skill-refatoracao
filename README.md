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
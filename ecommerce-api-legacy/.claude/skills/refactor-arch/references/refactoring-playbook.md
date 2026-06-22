# Refactoring Playbook

Loaded in **Phase 3 (Refactoring)**, together with `mvc-patterns.md`. One
concrete transform per anti-pattern (see `anti-patterns.md` ids), each with a
**before / after** example. Examples are illustrative — adapt to the stack
detected in Phase 1.

---

## 1. Hardcoded credentials → env vars  (AP-01)

```python
# BEFORE
DB_PASSWORD = "admin123"
conn = connect(password="admin123")
```
```python
# AFTER
import os
DB_PASSWORD = os.environ["DB_PASSWORD"]
conn = connect(password=DB_PASSWORD)
```

---

## 2. SQL injection → parameterized query  (AP-02)

```python
# BEFORE
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
```
```python
# AFTER
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

## 3. God Class → MVC split  (AP-03)

```python
# BEFORE — app.py does routing + SQL + presentation
@app.route("/users")
def users():
    rows = db.execute("SELECT * FROM users").fetchall()
    return "".join(f"<li>{r['name']}</li>" for r in rows)
```
```python
# AFTER — models/user.py + controllers/users.py + views/
# models/user.py
class User:
    @staticmethod
    def all():
        return db.execute("SELECT * FROM users").fetchall()

# controllers/users.py
@app.route("/users")
def users():
    return render_template("users/index.html", users=User.all())
```

---

## 4. Business logic in controller → Model/Service  (AP-04)

```python
# BEFORE — controller computes the discount
def create_order(request):
    discount = 0.15 if request.user.total_orders > 10 else 0
    ...
```
```python
# AFTER — model owns the rule
class Order:
    @staticmethod
    def discount_for(user):
        return 0.15 if user.total_orders > 10 else 0

def create_order(request):
    discount = Order.discount_for(request.user)
```

---

## 5. No Model layer → introduce Model  (AP-05)

```python
# BEFORE — raw query inline in a route
@app.route("/products")
def products():
    return db.execute("SELECT * FROM products WHERE active = 1").fetchall()
```
```python
# AFTER — query lives on the Model
class Product:
    @staticmethod
    def active():
        return db.execute("SELECT * FROM products WHERE active = 1").fetchall()

@app.route("/products")
def products():
    return Product.active()
```

---

## 6. Tight coupling → dependency injection  (AP-06)

```python
# BEFORE — service builds its own dependency
class OrderService:
    def __init__(self):
        self.db = SqliteConnection("loja.db")
```
```python
# AFTER — dependency injected
class OrderService:
    def __init__(self, db):
        self.db = db

service = OrderService(db=current_connection)
```

---

## 7. N+1 queries → eager loading  (AP-08)

```python
# BEFORE — one query per order
orders = Order.all()
for o in orders:
    print(o.customer().name)   # query inside the loop
```
```python
# AFTER — single join / eager load
orders = Order.with_customers()   # SELECT ... JOIN customers ...
for o in orders:
    print(o.customer_name)
```

---

## 8. Missing validation → validation layer  (AP-09)

```python
# BEFORE — raw input straight to the DB
def create_user(request):
    db.execute("INSERT INTO users(email) VALUES(?)", (request.form["email"],))
```
```python
# AFTER — validate before persisting
def create_user(request):
    email = request.form.get("email", "").strip()
    if "@" not in email:
        abort(400, "invalid email")
    db.execute("INSERT INTO users(email) VALUES(?)", (email,))
```

---

## 9. Deprecated API → modern replacement  (AP-10)

```python
# BEFORE — deprecated API
from datetime import datetime
created = datetime.utcnow()
```
```python
# AFTER — supported replacement
from datetime import datetime, timezone
created = datetime.now(timezone.utc)
```

```js
// BEFORE — deprecated Buffer constructor
const buf = new Buffer(input);
```
```js
// AFTER
const buf = Buffer.from(input);
```

---

## 10. Magic numbers → named constants  (AP-11)

```python
# BEFORE
if status == 3:
    ship(order)
```
```python
# AFTER
STATUS_PAID = 3
if status == STATUS_PAID:
    ship(order)
```

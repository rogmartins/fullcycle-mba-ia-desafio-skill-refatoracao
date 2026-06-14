# Severity Scale

Used in Phase 1 to classify every finding before recording it.

---

## Levels

### CRITICAL
**Definition**: Immediate security risk, data exposure, or a structural violation so severe it invalidates the entire codebase.

**Apply when**:
- Credentials, passwords, API keys, or connection strings are hardcoded in source files
- SQL queries are built via string concatenation (SQL Injection vector)
- A single file concentrates database access, business logic, routing, and presentation (full God Class)

**Examples**:
```
DB_PASSWORD = "admin123"                       # hardcoded credential
query = "SELECT * FROM users WHERE id=" + id  # SQL injection
app.rb (800 lines, routes + SQL + HTML)        # God Class
```

---

### HIGH
**Definition**: Architectural violation that damages maintainability, testability, and scalability. No immediate security risk, but causes structural decay over time.

**Apply when**:
- Complex business logic lives inside a controller or view
- No Model layer exists; raw queries are scattered across the codebase
- Components are tightly coupled with no dependency injection
- Mutable global state is shared across components

**Examples**:
```python
# controller running domain logic
def create_order(request):
    discount = 0
    if request.user.total_orders > 10:
        discount = 0.15
    ...
```

---

### MEDIUM
**Definition**: Code quality problem that degrades performance or creates duplication without immediately breaking architecture.

**Apply when**:
- N+1 queries: a loop issues a database call at each iteration
- Logic is duplicated across controllers or same-layer files
- User input reaches the database without validation
- Middleware carries domain-level logic instead of infrastructure concerns

**Examples**:
```ruby
# N+1: one query per order
orders.each { |o| puts o.customer.name }

# duplication
def format_date_orders(d) = d.strftime("%d/%m/%Y")
def format_date_invoices(d) = d.strftime("%d/%m/%Y")
```

---

### LOW
**Definition**: Readability or style issue. Does not affect behaviour, security, or architecture.

**Apply when**:
- Magic numbers or strings without named constants
- Meaningless variable, function, or class names
- Outdated comments or commented-out dead code blocks

**Examples**:
```python
if status == 3:      # magic number — what is 3?
    ...

def do_stuff(x):    # meaningless name
    ...

# x = old_query()  # dead code
```

---

## Priority During Refactoring

```
CRITICAL → HIGH → MEDIUM → LOW
```

Always resolve higher-severity findings before lower ones to avoid invalidating work already done.

---

## Quick Reference Table

| Level    | Security risk | Arch impact | Performance | Readability |
|----------|:---:|:---:|:---:|:---:|
| CRITICAL | YES | YES | —   | —   |
| HIGH     | no  | YES | —   | —   |
| MEDIUM   | no  | no  | YES | —   |
| LOW      | no  | no  | no  | YES |

# Anti-Pattern Catalog

Loaded in **Phase 2 (Audit)**, together with `severity-scale.md`. Each entry has
a stable `id`, a severity, **detection signals** (what to grep/look for), and the
playbook transform that fixes it (see `refactoring-playbook.md`).

Severity definitions live in `severity-scale.md`. Distribution below:
CRITICAL × 3 · HIGH × 4 · MEDIUM × 3 · LOW × 3 (12 total).

---

## CRITICAL

### AP-01 — Hardcoded Credentials
- **Severity**: CRITICAL
- **Detection signals**: literal `password`, `secret`, `api_key`, `token`,
  connection strings (`postgres://user:pass@...`) assigned in source instead of
  read from environment variables.
- **Fix**: `refactoring-playbook.md` → *Hardcoded credentials → env vars*.

### AP-02 — SQL Injection (string-built query)
- **Severity**: CRITICAL
- **Detection signals**: SQL assembled with `+`, f-strings, template literals or
  `%`/`.format()` mixing user input directly into the query
  (`"... WHERE id=" + id`).
- **Fix**: → *SQL injection → parameterized query*.

### AP-03 — God Class / God File
- **Severity**: CRITICAL
- **Detection signals**: a single file concentrating routing **and** business
  logic **and** data access **and** presentation; usually > 200 lines.
- **Fix**: → *God Class → MVC split*.

---

## HIGH

### AP-04 — Business Logic in Controller/View
- **Severity**: HIGH
- **Detection signals**: domain calculations (discounts, totals, state machines)
  inside route handlers or templates.
- **Fix**: → *Business logic in controller → Model/Service*.

### AP-05 — Missing Model Layer
- **Severity**: HIGH
- **Detection signals**: raw queries scattered across controllers/routes; no
  `models/` layer owning data access.
- **Fix**: → *No Model layer → introduce Model*.

### AP-06 — Tight Coupling (no Dependency Injection)
- **Severity**: HIGH
- **Detection signals**: components instantiating their own dependencies
  (DB connection, services) inline; hard to test in isolation.
- **Fix**: → *Tight coupling → dependency injection*.

### AP-07 — Mutable Global State
- **Severity**: HIGH
- **Detection signals**: module-level mutable variables (caches, current user,
  config) read/written across components.
- **Fix**: → encapsulate in a Model/service; pass via DI (AP-06 transform).

---

## MEDIUM

### AP-08 — N+1 Queries
- **Severity**: MEDIUM
- **Detection signals**: a database call inside a loop iterating over a previous
  result set (`for o in orders: o.customer...`).
- **Fix**: → *N+1 queries → eager loading*.

### AP-09 — Missing Input Validation
- **Severity**: MEDIUM
- **Detection signals**: request parameters reaching the database or business
  logic without type/presence/format checks.
- **Fix**: → *Missing validation → validation layer*.

### AP-10 — Deprecated / Outdated API Usage
- **Severity**: MEDIUM
- **Detection signals** (language-specific):
  - Python: `datetime.utcnow()`, `imp`, `collections.Mapping`,
    `flask.Markup`, `werkzeug.url_encode`, `db.engine.execute()`.
  - Node.js: `new Buffer()`, `url.parse()`, `crypto.createCipher()`,
    `domain` module, callback-only `fs` APIs superseded by `fs/promises`.
  - General: functions/flags emitting `DeprecationWarning`, or marked
    `@deprecated` / "deprecated" in the dependency's release notes.
- **Fix**: → *Deprecated API → modern replacement*.

---

## LOW

### AP-11 — Magic Numbers / Strings
- **Severity**: LOW
- **Detection signals**: bare literals with domain meaning (`if status == 3`)
  without a named constant.
- **Fix**: → *Magic numbers → named constants*.

### AP-12 — Meaningless Names
- **Severity**: LOW
- **Detection signals**: variables/functions/classes named `data`, `tmp`, `x`,
  `do_stuff`, etc., that hide intent.
- **Fix**: rename for intent (see playbook constant/rename guidance).

### AP-13 — Dead Code / Outdated Comments
- **Severity**: LOW
- **Detection signals**: commented-out code blocks, unreachable code, stale
  comments contradicting the code.
- **Fix**: remove during the LOW pass of Phase 3.

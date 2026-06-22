# Project Analysis Heuristics

Loaded at the **start of Phase 1**. Use these heuristics to detect the stack
(language, framework, database) and to map the current architecture before any
audit or refactoring. Stay **technology-agnostic** — derive the stack from the
signals below, never assume it.

---

## 1. Language Detection

| Signal (file / extension) | Language |
|---------------------------|----------|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `*.py` | Python |
| `package.json`, `*.js`, `*.ts` | Node.js / JavaScript |
| `Gemfile`, `*.rb` | Ruby |
| `composer.json`, `*.php` | PHP |
| `go.mod`, `*.go` | Go |
| `pom.xml`, `build.gradle`, `*.java` | Java |

If multiple manifests exist, the primary language is the one matching the entry
point and the majority of source files.

---

## 2. Framework Detection

Inspect the dependency manifest and the entry point's imports.

| Signal | Framework |
|--------|-----------|
| `flask` in deps / `from flask import` | Python / Flask |
| `django` in deps / `manage.py` present | Python / Django |
| `fastapi` in deps / `from fastapi import` | Python / FastAPI |
| `express` in `package.json` / `require('express')` | Node.js / Express |
| `sinatra` in `Gemfile` | Ruby / Sinatra |
| `rails` in `Gemfile` / `config/application.rb` | Ruby on Rails |
| `laravel/framework` in `composer.json` | PHP / Laravel |
| `github.com/gin-gonic/gin` in `go.mod` | Go / Gin |
| no web framework found | plain stdlib app — apply the Universal Rules in `mvc-patterns.md` |

---

## 3. Database Detection

| Signal | Database / Access layer |
|--------|--------------------------|
| `sqlite3`, `*.db`, `*.sqlite` | SQLite |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2`, `mysql://` | MySQL |
| `sqlalchemy`, `sequelize`, `activerecord`, `eloquent` | ORM in use |
| raw `.execute(...)` / `db.query(...)` / string SQL | direct/raw driver (no ORM) |
| `mongoose`, `pymongo`, `mongodb://` | MongoDB |

Record **how** the database is accessed (ORM vs raw driver) — this drives the
Model-extraction strategy in Phase 3.

---

## 4. Architecture Mapping

1. **Entry point**: locate the main file (`app.py`, `index.js`, `application.rb`,
   `main.go`, `index.php`).
2. **Layer inventory**: for each source file, classify what it currently does —
   routing, business logic, data access, presentation, configuration. Note when a
   single file does several of these at once.
3. **Existing folders**: list directories that already imply layers
   (`models/`, `controllers/`, `routes/`, `services/`, `views/`).
4. **Cross-cutting concerns**: where credentials/config live, where (if anywhere)
   input validation happens, shared global state.
5. **Size signals**: flag files longer than 200 lines (God Class candidates) and
   compute the LOC total for the report header.

---

## 5. Analysis Summary (printed output)

At the end of Phase 1, print this block to the terminal:

```
================================
ARCHITECTURE ANALYSIS
================================
Project:      {project-name}
Language:     {language}
Framework:    {framework or "none (stdlib)"}
Database:     {database} ({ORM | raw driver})
Entry point:  {path}
Files:        {N} | ~{LOC} lines of code

Current layers detected:
- {folder/file} -> {responsibilities found}
...

Mixed-responsibility files (refactor candidates):
- {path} -> {e.g. routing + SQL + presentation}
================================
```

The mixed-responsibility files listed here are the primary targets to cross
against the anti-pattern catalog in Phase 2.

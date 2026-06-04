## 1. Análise Manual 

**1.1** **Projeto:**  `code-smells-project`

**Problema 1** 

**Descrição:** `controllers.py` depende diretamente de módulos concretos
**Princípio violado:** DIP — Dependency Inversion Principle
**Arquivo/linhas:** `controllers.py`, linhas 1–3
**Severidade:** `CRITICAL`

**Princípio:**
"High-level modules should not depend on low-level modules. Both should depend on abstractions." (Robert C. Martin). Módulos de alto nível (controllers, regras de negócio) não devem importar diretamente implementações concretas.

**Código problemático:**
```python
from flask import request, jsonify
import models        # acoplamento direto à implementação SQLite
from database import get_db  # acoplamento direto ao SQLite
```

**Motivo da violação:**
Os controllers importam diretamente `models` (implementação concreta de acesso a dados SQLite) e `database.get_db()`. Isso cria acoplamento rígido: trocar SQLite por PostgreSQL, adicionar cache ou mockar em testes unitários exige modificar os controllers. O correto seria introduzir uma camada de abstração — repositórios ou interfaces (ex.: `ProdutoRepository`) — e injetá-los nos controllers. Com DIP, o controller dependeria da abstração `IProdutoRepository`, não da implementação `models.py`.

---



2 MEDIUM
2 LOW
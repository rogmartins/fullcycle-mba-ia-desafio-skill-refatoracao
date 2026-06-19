# REFACTORED: [LOW] Constantes nomeadas no lugar de números/strings mágicos.

# Validação de produto (antes embutido em controllers.py:47-52)
NOME_MIN = 2
NOME_MAX = 200
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"

# Status de pedido (antes literais embutidos em controllers.py:242)
STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
STATUS_PADRAO = "pendente"

# Regras de desconto do relatório de vendas (antes números mágicos em models.py:257)
DESCONTO_FAIXAS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]

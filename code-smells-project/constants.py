# REFACTORED: constantes de domínio extraídas (corrige strings/números mágicos)

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

NOME_MIN = 2
NOME_MAX = 200

# Faixas de desconto sobre o faturamento bruto (limiar -> percentual)
FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]

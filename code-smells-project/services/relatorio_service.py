from models.pedido import relatorio_dados_brutos

# REFACTORED: named constants replace magic numbers for discount thresholds
DESCONTO_ALTO_LIMITE = 10_000
DESCONTO_ALTO_TAXA = 0.10
DESCONTO_MEDIO_LIMITE = 5_000
DESCONTO_MEDIO_TAXA = 0.05
DESCONTO_BAIXO_LIMITE = 1_000
DESCONTO_BAIXO_TAXA = 0.02


def calcular_desconto(faturamento):
    # REFACTORED: business rule extracted from data layer into dedicated service
    if faturamento > DESCONTO_ALTO_LIMITE:
        return faturamento * DESCONTO_ALTO_TAXA
    if faturamento > DESCONTO_MEDIO_LIMITE:
        return faturamento * DESCONTO_MEDIO_TAXA
    if faturamento > DESCONTO_BAIXO_LIMITE:
        return faturamento * DESCONTO_BAIXO_TAXA
    return 0


def relatorio_vendas():
    dados = relatorio_dados_brutos()
    faturamento = dados["faturamento_bruto"]
    total_pedidos = dados["total_pedidos"]
    desconto = calcular_desconto(faturamento)

    return {
        **dados,
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }

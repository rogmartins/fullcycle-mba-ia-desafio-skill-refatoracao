from constants import CATEGORIAS_VALIDAS, NOME_MAX, NOME_MIN

# REFACTORED: validação de produto centralizada (corrige duplicação entre
# criar_produto e atualizar_produto)


def validar_produto(dados):
    """Retorna uma mensagem de erro (str) ou None se válido."""
    if not dados:
        return "Dados inválidos"
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            return campo.capitalize() + " é obrigatório"

    nome = dados["nome"]
    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    if len(nome) < NOME_MIN:
        return "Nome muito curto"
    if len(nome) > NOME_MAX:
        return "Nome muito longo"

    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        return "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)
    return None

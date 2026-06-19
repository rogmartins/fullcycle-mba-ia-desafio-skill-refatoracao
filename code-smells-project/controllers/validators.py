# REFACTORED: [MEDIUM] Validação de produto unificada (antes duplicada em criar/atualizar).
import re

from constants import NOME_MIN, NOME_MAX, CATEGORIAS_VALIDAS, CATEGORIA_PADRAO

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_produto(dados, exigir_tamanho_nome=True):
    """Retorna (campos, erro). Se erro != None, é uma mensagem de validação."""
    if not dados:
        return None, "Dados inválidos"
    obrigatorios = {"nome": "Nome é obrigatório", "preco": "Preço é obrigatório", "estoque": "Estoque é obrigatório"}
    for campo, msg in obrigatorios.items():
        if campo not in dados:
            return None, msg

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if preco < 0:
        return None, "Preço não pode ser negativo"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    if exigir_tamanho_nome:
        if len(nome) < NOME_MIN:
            return None, "Nome muito curto"
        if len(nome) > NOME_MAX:
            return None, "Nome muito longo"
    if categoria not in CATEGORIAS_VALIDAS:
        return None, "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }, None


def email_valido(email):
    # REFACTORED: [MEDIUM] Validação de formato de email (antes ausente).
    return bool(EMAIL_RE.match(email or ""))

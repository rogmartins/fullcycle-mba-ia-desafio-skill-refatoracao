import logging
from flask import Blueprint, request, jsonify
from models.produto import (
    get_todos_produtos, get_produto_por_id, criar_produto as model_criar_produto,
    atualizar_produto as model_atualizar_produto, deletar_produto as model_deletar_produto,
    buscar_produtos as model_buscar_produtos, CATEGORIAS_VALIDAS,
)

logger = logging.getLogger(__name__)  # REFACTORED: structured logging replaces print()
produtos_bp = Blueprint("produtos", __name__)


def _validar_dados_produto(dados, require_nome=True):
    # REFACTORED: shared validation helper eliminates duplication between criar and atualizar
    if not dados:
        return "Dados inválidos"
    if require_nome and "nome" not in dados:
        return "Nome é obrigatório"
    if "preco" not in dados:
        return "Preço é obrigatório"
    if "estoque" not in dados:
        return "Estoque é obrigatório"

    nome = dados.get("nome", "")
    if require_nome:
        if len(nome) < 2:
            return "Nome muito curto"
        if len(nome) > 200:
            return "Nome muito longo"

    if dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if dados["estoque"] < 0:
        return "Estoque não pode ser negativo"

    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        return f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}"

    return None


@produtos_bp.route("", methods=["GET"])
def listar_produtos():
    try:
        produtos = get_todos_produtos()
        logger.info("Listando %d produtos", len(produtos))
        return jsonify({"dados": produtos, "sucesso": True}), 200
    except Exception as e:
        logger.error("Erro ao listar produtos: %s", e)
        return jsonify({"erro": str(e)}), 500


@produtos_bp.route("/busca", methods=["GET"])
def buscar_produtos():
    try:
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        if preco_min:
            preco_min = float(preco_min)
        if preco_max:
            preco_max = float(preco_max)

        resultados = model_buscar_produtos(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@produtos_bp.route("/<int:id>", methods=["GET"])
def buscar_produto(id):
    try:
        produto = get_produto_por_id(id)
        if produto:
            return jsonify({"dados": produto, "sucesso": True}), 200
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@produtos_bp.route("", methods=["POST"])
def criar_produto():
    try:
        dados = request.get_json()
        erro = _validar_dados_produto(dados, require_nome=True)
        if erro:
            return jsonify({"erro": erro}), 400

        id = model_criar_produto(
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )
        logger.info("Produto criado com ID: %d", id)
        return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201
    except Exception as e:
        logger.error("Erro ao criar produto: %s", e)
        return jsonify({"erro": str(e)}), 500


@produtos_bp.route("/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    try:
        if not get_produto_por_id(id):
            return jsonify({"erro": "Produto não encontrado"}), 404

        dados = request.get_json()
        erro = _validar_dados_produto(dados, require_nome=True)
        if erro:
            return jsonify({"erro": erro}), 400

        model_atualizar_produto(
            id,
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@produtos_bp.route("/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    try:
        if not get_produto_por_id(id):
            return jsonify({"erro": "Produto não encontrado"}), 404

        model_deletar_produto(id)
        logger.info("Produto %d deletado", id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

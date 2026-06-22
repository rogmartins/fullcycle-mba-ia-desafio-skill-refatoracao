from flask import jsonify, request

from models.produto import Produto
from services.validators import validar_produto

# REFACTORED: controller fino — recebe a requisição, chama o Model, responde


def listar_produtos():
    produtos = Produto.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = Produto.por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar_produto():
    dados = request.get_json()
    erro = validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    id = Produto.criar(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not Produto.por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json()
    erro = validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400

    Produto.atualizar(
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not Produto.por_id(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    Produto.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = Produto.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

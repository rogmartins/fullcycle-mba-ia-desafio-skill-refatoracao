from flask import Blueprint, jsonify
from services.relatorio_service import relatorio_vendas as service_relatorio_vendas

relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.route("/vendas", methods=["GET"])
def relatorio_vendas():
    try:
        relatorio = service_relatorio_vendas()  # REFACTORED: business rules delegated to service layer
        return jsonify({"dados": relatorio, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

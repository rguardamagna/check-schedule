from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
import os
from werkzeug.utils import secure_filename

from app import db
from app.models import Cheque
from app.services.cheque_service import (
    informe_para_fecha,
    informe_semanal,
    marcar_pagado,
    reabrir,
    _actualizar_vencidos,
)
from app.services.xlsx_service import procesar_xlsx
from app.utils.calendario import _cargar_feriados

api_bp = Blueprint("api", __name__)


@api_bp.route("/cheques", methods=["GET"])
@login_required
def listar_cheques():
    estado = request.args.get("estado")
    proveedor = request.args.get("proveedor")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    _actualizar_vencidos()
    query = Cheque.query

    if estado and estado != "todos":
        query = query.filter(Cheque.estado == estado)
    if proveedor:
        query = query.filter(Cheque.proveedor.ilike(f"%{proveedor}%"))
    if fecha_desde:
        query = query.filter(
            Cheque.fecha_vencimiento
            >= datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        )
    if fecha_hasta:
        query = query.filter(
            Cheque.fecha_vencimiento
            <= datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        )

    pagination = query.order_by(Cheque.fecha_vencimiento.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "items": [c.to_dict() for c in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
        }
    )


@api_bp.route("/cheques/<int:cheque_id>/pagar", methods=["POST"])
@login_required
def pagar(cheque_id):
    data = request.get_json(silent=True) or {}
    fecha_str = data.get("fecha_pago")
    fecha_pago = (
        datetime.strptime(fecha_str, "%Y-%m-%d").date() if fecha_str else date.today()
    )
    cheque = marcar_pagado(cheque_id, fecha_pago)
    return jsonify(
        {
            "id": cheque.id,
            "estado": cheque.estado,
            "fecha_pago": cheque.fecha_pago.isoformat(),
        }
    )


@api_bp.route("/cheques/<int:cheque_id>/reabrir", methods=["POST"])
@login_required
def api_reabrir(cheque_id):
    cheque = reabrir(cheque_id)
    return jsonify({"id": cheque.id, "estado": cheque.estado})


@api_bp.route("/informe", methods=["GET"])
@login_required
def informe():
    fecha_str = request.args.get("fecha", date.today().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato inválido. Use YYYY-MM-DD"}), 400
    return jsonify(informe_para_fecha(fecha))


@api_bp.route("/informe/semanal", methods=["GET"])
@login_required
def informe_semanal_api():
    fecha_str = request.args.get("fecha", date.today().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato inválido. Use YYYY-MM-DD"}), 400
    return jsonify(informe_semanal(fecha))


@api_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if current_user.role not in ("admin",):
        return jsonify({"error": "Solo admin puede subir archivos"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Archivo sin nombre"}), 400

    if not file.filename.endswith((".xlsx", ".xls")):
        return jsonify({"error": "Solo .xlsx"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        resultado = procesar_xlsx(filepath)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error al procesar: {str(e)}"}), 500
    finally:
        try:
            os.remove(filepath)
        except OSError:
            pass


@api_bp.route("/feriados", methods=["GET"])
@login_required
def listar_feriados():
    return jsonify({"feriados": sorted(list(_cargar_feriados()))})

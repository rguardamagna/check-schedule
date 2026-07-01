from datetime import date, timedelta
from app import db
from app.models import Cheque
from app.utils.calendario import es_habil, es_feriado, proximo_habil


def _actualizar_vencidos():
    hoy = date.today()
    corte = hoy - timedelta(days=31)
    Cheque.query.filter(
        Cheque.estado == "pendiente", Cheque.fecha_vencimiento <= corte
    ).update({"estado": "vencido"}, synchronize_session=False)
    db.session.commit()


def informe_para_fecha(fecha: date) -> dict:
    _actualizar_vencidos()

    if not es_habil(fecha):
        prox = proximo_habil(fecha)
        motivo = "Feriado" if not es_fin_semana_import(fecha) else "Fin de semana"
        return {
            "fecha": fecha.isoformat(),
            "es_inhabil": True,
            "motivo": motivo,
            "total_a_pagar": 0,
            "cantidad_cheques": 0,
            "proximo_vencimiento": _proximo_vencimiento(fecha),
            "proximo_habil": prox.isoformat(),
            "cheques": [],
        }

    cheques = Cheque.query.filter(
        Cheque.estado == "pendiente",
        Cheque.fecha_vencimiento <= fecha,
        Cheque.fecha_vencimiento >= fecha - timedelta(days=30),
    ).all()

    resultado = []
    total = 0
    for c in cheques:
        dias = (fecha - c.fecha_vencimiento).days
        if dias > 30:
            continue  # safety
        nota = (
            "Vence hoy"
            if dias == 0
            else f"Vence hace {dias} día{'s' if dias > 1 else ''}"
        )
        resultado.append(
            {
                "id": c.id,
                "proveedor": c.proveedor,
                "importe": float(c.importe),
                "fecha_vencimiento": c.fecha_vencimiento.isoformat(),
                "dias_desde_vencimiento": dias,
                "nota": nota,
                "estado": c.estado,
            }
        )
        total += float(c.importe)

    return {
        "fecha": fecha.isoformat(),
        "es_inhabil": False,
        "total_a_pagar": round(total, 2),
        "cantidad_cheques": len(resultado),
        "proximo_vencimiento": _proximo_vencimiento(fecha),
        "cheques": resultado,
    }


def informe_semanal(fecha: date) -> dict:
    dias = []
    total_semanal = 0
    total_cheques = 0
    for i in range(7):
        dia = fecha + timedelta(days=i)
        info = informe_para_fecha(dia)
        if not info["es_inhabil"]:
            total_semanal += info["total_a_pagar"]
            total_cheques += info["cantidad_cheques"]
        dias.append(info)

    return {
        "fecha_desde": fecha.isoformat(),
        "fecha_hasta": (fecha + timedelta(days=6)).isoformat(),
        "dias": dias,
        "total_semanal": round(total_semanal, 2),
        "total_cheques_semana": total_cheques,
    }


def marcar_pagado(cheque_id, fecha_pago=None):
    cheque = Cheque.query.get_or_404(cheque_id)
    cheque.estado = "pagado"
    cheque.fecha_pago = fecha_pago or date.today()
    db.session.commit()
    return cheque


def reabrir(cheque_id):
    cheque = Cheque.query.get_or_404(cheque_id)
    cheque.estado = "pendiente"
    cheque.fecha_pago = None
    db.session.commit()
    return cheque


def _proximo_vencimiento(fecha):
    prox = (
        Cheque.query.filter(
            Cheque.estado == "pendiente", Cheque.fecha_vencimiento > fecha
        )
        .order_by(Cheque.fecha_vencimiento.asc())
        .first()
    )
    return prox.fecha_vencimiento.isoformat() if prox else None


def es_fin_semana_import(fecha):
    from app.utils.calendario import es_fin_semana

    return es_fin_semana(fecha)

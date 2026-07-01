import json
from datetime import date, timedelta
from flask import current_app


def _cargar_feriados() -> set:
    path = current_app.config["FERIADOS_PATH"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("feriados", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def es_feriado(fecha: date) -> bool:
    return fecha.isoformat() in _cargar_feriados()


def es_fin_semana(fecha: date) -> bool:
    return fecha.weekday() >= 5


def es_habil(fecha: date) -> bool:
    return not es_feriado(fecha) and not es_fin_semana(fecha)


def proximo_habil(fecha: date) -> date:
    while not es_habil(fecha):
        fecha += timedelta(days=1)
    return fecha

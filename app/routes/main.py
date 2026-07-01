from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from datetime import date, datetime
import io

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    return render_template("dashboard.html")


@main_bp.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")


@main_bp.route("/informes")
@login_required
def informes():
    return render_template("informes.html")


@main_bp.route("/informes/pdf")
@login_required
def informe_pdf():
    fecha_str = request.args.get("fecha", date.today().isoformat())
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return "Fecha inválida", 400

    from app.services.cheque_service import informe_para_fecha

    data = informe_para_fecha(fecha)

    try:
        import pdfkit

        html = render_template("informe_pdf.html", data=data, fecha_emision=date.today().isoformat())
        pdf = pdfkit.from_string(html, False)
        return send_file(
            io.BytesIO(pdf),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"informe_{fecha_str}.pdf",
        )
    except (ImportError, OSError):
        # Fallback: render HTML page with print button
        return render_template("informes.html", print_fecha=fecha_str)

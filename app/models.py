from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


class Cheque(db.Model):
    __tablename__ = "cheques"

    id = db.Column(db.Integer, primary_key=True)
    proveedor = db.Column(db.String(200), nullable=False)
    importe = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    fecha_pago = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "proveedor", "importe", "fecha_vencimiento", name="uq_cheque"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "proveedor": self.proveedor,
            "importe": float(self.importe),
            "fecha_vencimiento": self.fecha_vencimiento.isoformat(),
            "estado": self.estado,
            "fecha_pago": self.fecha_pago.isoformat() if self.fecha_pago else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="visualizador")

    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from datetime import datetime

from extensions import db


class Experiencia(db.Model):
    __tablename__ = "experiencias_porti"

    id = db.Column(db.Integer, primary_key=True)

    nombre_cliente = db.Column(
        db.String(100),
        nullable=False
    )

    comentario = db.Column(
        db.Text,
        nullable=False
    )

    foto = db.Column(
        db.String(500),
        nullable=True
    )

    tipo_evento = db.Column(
        db.String(50),
        nullable=False
    )

    aprobada = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

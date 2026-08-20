from extensions import db


class Bebida(db.Model):

    __tablename__ = "bebidas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=False
    )

    imagen = db.Column(
        db.String(500),
        nullable=True
    )
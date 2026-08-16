import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# =====================================================
# BASE DE DATOS
# =====================================================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    raise RuntimeError(
        "No se encontró la variable DATABASE_URL"
    )


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
from models.experiencia import Experiencia


# =====================================================
# INICIO
# =====================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# =====================================================
# CASAMIENTOS
# =====================================================

@app.route("/casamientos")
def casamientos():
    return render_template("casamientos.html")


# =====================================================
# CUMPLEAÑOS
# =====================================================

@app.route("/cumpleanos")
def cumpleanos():
    return render_template("cumpleanos.html")


# =====================================================
# EJECUTAR
# =====================================================

with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True)
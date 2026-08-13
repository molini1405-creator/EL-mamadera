import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# =====================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =====================================================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Render puede entregar DATABASE_URL con postgres://
    # SQLAlchemy utiliza postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    # Mientras desarrollamos localmente
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://porti:porti123@localhost:5433/porti_db"
    )


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


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

if __name__ == "__main__":
    app.run(debug=True)
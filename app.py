import os

from flask import Flask, render_template, request
from extensions import db

import cloudinary
import cloudinary.uploader


app = Flask(__name__)
# =====================================================
# CLOUDINARY
# =====================================================

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

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

else:

    database_url = (
        "postgresql://postgres:postgres"
        "@localhost:5433/el-mamadera"
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


from models.experiencia import Experiencia


# =====================================================
# INICIO
# =====================================================

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/casamientos")
def casamientos():
    experiencias = Experiencia.query.filter_by(
        tipo_evento="casamiento",
        aprobada=True
    ).order_by(
        Experiencia.fecha.desc()
    ).all()

    return render_template(
        "casamientos.html",
        experiencias=experiencias
    )


@app.route("/cumpleanos")
def cumpleanos():
    experiencias = Experiencia.query.filter_by(
        tipo_evento="cumpleanos",
        aprobada=True
    ).order_by(
        Experiencia.fecha.desc()
    ).all()

    return render_template(
        "cumpleanos.html",
        experiencias=experiencias
    )

@app.route("/compartir/<tipo_evento>", methods=["GET", "POST"])
def compartir_experiencia(tipo_evento):

    if tipo_evento not in ["casamiento", "cumpleanos"]:
        return "Tipo de evento no válido", 404

    if request.method == "POST":

        nombre = request.form.get("nombre")
        comentario = request.form.get("comentario")
        foto = request.files.get("foto")

        if not nombre or not comentario or not foto:
            return "Todos los campos son obligatorios", 400

        try:

            # =====================================================
            # SUBIR FOTO A CLOUDINARY
            # =====================================================

            resultado = cloudinary.uploader.upload(
                foto,
                folder="el_mamadera/experiencias"
            )

            url_foto = resultado.get("secure_url")


            # =====================================================
            # GUARDAR EXPERIENCIA EN POSTGRESQL
            # =====================================================

            nueva_experiencia = Experiencia(
                nombre_cliente=nombre,
                comentario=comentario,
                foto=url_foto,
                tipo_evento=tipo_evento,
                aprobada=False
            )

            db.session.add(nueva_experiencia)
            db.session.commit()


            return """
                <h2>¡Gracias por compartir tu experiencia! 🥂</h2>
                <p>
                    Tu experiencia fue enviada correctamente
                    y será revisada antes de publicarse.
                </p>
                <a href="/">Volver al inicio</a>
            """


        except Exception as e:

            db.session.rollback()

            print("ERROR:", e)

            return "Ocurrió un error al enviar la experiencia.", 500


    return render_template(
        "compartir.html",
        tipo_evento=tipo_evento
    )

# =====================================================
# EJECUTAR
# =====================================================

with app.app_context():
    db.create_all()
    
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/admin")
def admin():

    pendientes = Experiencia.query.filter_by(
        aprobada=False
    ).order_by(
        Experiencia.fecha.desc()
    ).all()

    return render_template(
        "admin.html",
        pendientes=pendientes
    )


@app.route("/admin/aprobar/<int:id>", methods=["POST"])
def aprobar_experiencia(id):

    experiencia = Experiencia.query.get_or_404(id)

    experiencia.aprobada = True

    db.session.commit()

    return redirect("/admin")


@app.route("/admin/eliminar/<int:id>", methods=["POST"])
def eliminar_experiencia(id):

    experiencia = Experiencia.query.get_or_404(id)

    db.session.delete(experiencia)

    db.session.commit()

    return redirect("/admin")
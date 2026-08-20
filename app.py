import os

from flask import Flask, render_template, request, redirect
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


# =====================================================
# MODELOS
# =====================================================

from models.experiencia import Experiencia
from models.bebida import Bebida


# =====================================================
# INICIO
# =====================================================

@app.route("/")
def inicio():

    bebidas = Bebida.query.order_by(
        Bebida.id
    ).all()

    return render_template(
        "index.html",
        bebidas=bebidas
    )


# =====================================================
# CASAMIENTOS
# =====================================================

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


# =====================================================
# CUMPLEAÑOS
# =====================================================

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


# =====================================================
# COMPARTIR EXPERIENCIA
# =====================================================

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

            # =================================================
            # SUBIR FOTO A CLOUDINARY
            # =================================================

            resultado = cloudinary.uploader.upload(
                foto,
                folder="el_mamadera/experiencias"
            )

            url_foto = resultado.get("secure_url")


            # =================================================
            # GUARDAR EXPERIENCIA EN POSTGRESQL
            # =================================================

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
# ADMIN
# =====================================================

@app.route("/admin")
def admin():

    pendientes = Experiencia.query.filter_by(
        aprobada=False
    ).order_by(
        Experiencia.fecha.desc()
    ).all()

    bebidas = Bebida.query.order_by(
        Bebida.id
    ).all()

    return render_template(
        "admin.html",
        pendientes=pendientes,
        bebidas=bebidas
    )


# =====================================================
# AGREGAR BEBIDA
# =====================================================

@app.route("/admin/bebidas/agregar", methods=["GET", "POST"])
def agregar_bebida():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        categoria = request.form.get("categoria")
        foto = request.files.get("foto")

        if not nombre or not descripcion or not categoria:
            return "Todos los campos son obligatorios", 400

        try:

            url_foto = None

            if foto and foto.filename:

                resultado = cloudinary.uploader.upload(
                    foto,
                    folder="el_mamadera/bebidas"
                )

                url_foto = resultado.get("secure_url")

            nueva_bebida = Bebida(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                imagen=url_foto
            )

            db.session.add(nueva_bebida)
            db.session.commit()

            return redirect("/admin")

        except Exception as e:

            db.session.rollback()

            print("ERROR:", e)

            return "Ocurrió un error al agregar la bebida.", 500

    return render_template("agregar_bebida.html")

# =====================================================
# EDITAR BEBIDA
# =====================================================

@app.route("/admin/bebidas/editar/<int:id>", methods=["GET", "POST"])
def editar_bebida(id):

    bebida = Bebida.query.get_or_404(id)

    if request.method == "POST":

        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        categoria = request.form.get("categoria")
        foto = request.files.get("foto")

        if not nombre or not descripcion or not categoria:
            return "Todos los campos son obligatorios", 400

        try:

            bebida.nombre = nombre
            bebida.descripcion = descripcion
            bebida.categoria = categoria

            if foto and foto.filename:

                resultado = cloudinary.uploader.upload(
                    foto,
                    folder="el_mamadera/bebidas"
                )

                bebida.imagen = resultado.get("secure_url")

            db.session.commit()

            return redirect("/admin")

        except Exception as e:

            db.session.rollback()

            print("ERROR:", e)

            return "Ocurrió un error al editar la bebida.", 500

    return render_template(
        "editar_bebida.html",
        bebida=bebida
    )


# =====================================================
# ELIMINAR BEBIDA
# =====================================================

@app.route("/admin/bebidas/eliminar/<int:id>", methods=["POST"])
def eliminar_bebida(id):

    bebida = Bebida.query.get_or_404(id)

    db.session.delete(bebida)
    db.session.commit()

    return redirect("/admin")


# =====================================================
# CARGAR BEBIDAS INICIALES
# =====================================================

def cargar_bebidas_iniciales():

    if Bebida.query.count() > 0:
        return

    bebidas = [

        Bebida(
            nombre="Negroni",
            descripcion="Intenso y seco, con un equilibrio perfecto entre notas amargas y dulces.",
            categoria="cocteles",
            imagen="/static/img/tragos/negroni.jpg"
        ),

        Bebida(
            nombre="Aperol Spritz",
            descripcion="Ligero, refrescante y equilibrado entre lo dulce y lo amargo. Ideal como aperitivo.",
            categoria="cocteles aperitivos",
            imagen="/static/img/tragos/aperol-spritz.jpg"
        ),

        Bebida(
            nombre="Cuba Libre",
            descripcion="Intenso y cítrico, con un toque burbujeante. Ideal para comenzar la noche.",
            categoria="cocteles",
            imagen="/static/img/tragos/cuba-libre.jpg"
        ),

        Bebida(
            nombre="Espresso Martini",
            descripcion="Frío, cremoso y elegante, con el carácter intenso del café.",
            categoria="cocteles",
            imagen="/static/img/tragos/espresso-martini.jpg"
        ),

        Bebida(
            nombre="Fernet",
            descripcion="Intenso y refrescante, con el característico sabor amargo del fernet combinado con una bebida cola.",
            categoria="cocteles",
            imagen="/static/img/tragos/fernet.jpg"
        ),

        Bebida(
            nombre="Mojito",
            descripcion="Fresco y refrescante, con menta, lima y un toque de dulzor.",
            categoria="cocteles",
            imagen="/static/img/tragos/mojito.jpg"
        ),

        Bebida(
            nombre="Gin Tonic",
            descripcion="Elegante, fresco y aromático, con el equilibrio perfecto entre gin y agua tónica.",
            categoria="cocteles",
            imagen="/static/img/tragos/gin-tonic.jpg"
        ),

        Bebida(
            nombre="Gancia",
            descripcion="Aperitivo ligero, fresco y cítrico.",
            categoria="aperitivos",
            imagen="/static/img/tragos/gancia.jpg"
        ),

        Bebida(
            nombre="Cynar Julep",
            descripcion="Refrescante y herbáceo, combina el carácter amargo del Cynar con la frescura de la menta y el pomelo.",
            categoria="cocteles aperitivos",
            imagen="/static/img/tragos/cynar-julep.jpg"
        ),

        Bebida(
            nombre="Corona",
            descripcion="Lager mexicana, ligera y refrescante, ideal para disfrutar bien fría.",
            categoria="cervezas",
            imagen="/static/img/tragos/corona.jpg"
        ),

        Bebida(
            nombre="Heineken",
            descripcion="Lager de sabor equilibrado, fresca y con un carácter ligeramente amargo.",
            categoria="cervezas",
            imagen="/static/img/tragos/heineken.jpg"
        ),

        Bebida(
            nombre="Stella Artois",
            descripcion="Lager de perfil suave y equilibrado, con un final refrescante.",
            categoria="cervezas",
            imagen="/static/img/tragos/stella.jpg"
        ),

        Bebida(
            nombre="Corona 0.0",
            descripcion="Una alternativa sin alcohol, ligera y refrescante, ideal para disfrutar bien fría.",
            categoria="sin-alcohol",
            imagen="/static/img/tragos/corona-00.jpg"
        ),

        Bebida(
            nombre="Heineken 0.0",
            descripcion="Lager sin alcohol, refrescante y equilibrada, ideal para disfrutar en cualquier momento.",
            categoria="sin-alcohol",
            imagen="/static/img/tragos/heineken-00.jpg"
        ),

        Bebida(
            nombre="Stella Artois 0.0",
            descripcion="Alternativa sin alcohol, de perfil suave, equilibrado y refrescante.",
            categoria="sin-alcohol",
            imagen="/static/img/tragos/stella-00.jpg"
        ),

        Bebida(
            nombre="Gancia Sin Alcohol",
            descripcion="Aperitivo fresco y ligero, con notas cítricas y sin alcohol.",
            categoria="aperitivos sin-alcohol",
            imagen="/static/img/tragos/gancia-sin-alcohol.jpg"
        ),

        Bebida(
            nombre="Coca-Cola",
            descripcion="Clásica, refrescante y perfecta para acompañar cualquier momento del evento.",
            categoria="gaseosas",
            imagen="/static/img/tragos/coca-cola.jpg"
        ),

        Bebida(
            nombre="Sprite",
            descripcion="Refrescante, cítrica y con el toque justo de burbujas.",
            categoria="gaseosas",
            imagen="/static/img/tragos/sprite.jpg"
        ),

        Bebida(
            nombre="Naranja",
            descripcion="Dulce, frutal y refrescante, ideal para disfrutar bien fría.",
            categoria="gaseosas",
            imagen="/static/img/tragos/naranja.jpg"
        ),

        Bebida(
            nombre="Pomelo",
            descripcion="Fresca, cítrica y ligeramente amarga, ideal para acompañar cualquier celebración.",
            categoria="gaseosas",
            imagen="/static/img/tragos/pomelo.jpg"
        )
    ]

    db.session.add_all(bebidas)
    db.session.commit()


# =====================================================
# APROBAR EXPERIENCIA
# =====================================================

@app.route("/admin/aprobar/<int:id>", methods=["POST"])
def aprobar_experiencia(id):

    experiencia = Experiencia.query.get_or_404(id)

    experiencia.aprobada = True

    db.session.commit()

    return redirect("/admin")


# =====================================================
# ELIMINAR EXPERIENCIA
# =====================================================

@app.route("/admin/eliminar/<int:id>", methods=["POST"])
def eliminar_experiencia(id):

    experiencia = Experiencia.query.get_or_404(id)

    db.session.delete(experiencia)

    db.session.commit()

    return redirect("/admin")


# =====================================================
# CREAR TABLAS
# =====================================================

with app.app_context():

    db.create_all()

    cargar_bebidas_iniciales()


# =====================================================
# EJECUTAR
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
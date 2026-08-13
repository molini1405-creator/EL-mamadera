from flask import Flask, render_template

app = Flask(__name__)


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
# EJECUTAR APLICACIÓN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
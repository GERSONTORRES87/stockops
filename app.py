import os
import time

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ---------------- MODELOS (3 tablas relacionadas) ----------------

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    productos = db.relationship("Producto", back_populates="categoria")


class Proveedor(db.Model):
    __tablename__ = "proveedores"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    productos = db.relationship("Producto", back_populates="proveedor")


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    categoria = db.relationship("Categoria", back_populates="productos")
    proveedor = db.relationship("Proveedor", back_populates="productos")


# ---------------- APLICACIÓN ----------------

def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.environ.get(
        "DATABASE_URL", "sqlite:///stockops.db"
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "stockops-dev")
    db.init_app(app)

    # Crea las tablas. Si es MySQL, reintenta mientras el contenedor arranca.
    with app.app_context():
        for intento in range(30):
            try:
                db.create_all()
                break
            except Exception:
                print("Esperando la base de datos... intento", intento + 1, flush=True)
                time.sleep(2)

    @app.route("/")
    def inicio():
        return redirect(url_for("productos"))

    # ---------- CRUD CATEGORÍAS ----------
    @app.route("/categorias", methods=["GET", "POST"])
    def categorias():
        if request.method == "POST":
            db.session.add(Categoria(
                nombre=request.form["nombre"],
                descripcion=request.form.get("descripcion"),
            ))
            db.session.commit()
            flash("Categoría creada")
            return redirect(url_for("categorias"))
        lista = Categoria.query.order_by(Categoria.id).all()
        return render_template("categorias.html", lista=lista, item=None)

    @app.route("/categorias/editar/<int:id>", methods=["GET", "POST"])
    def editar_categoria(id):
        item = db.get_or_404(Categoria, id)
        if request.method == "POST":
            item.nombre = request.form["nombre"]
            item.descripcion = request.form.get("descripcion")
            db.session.commit()
            flash("Categoría actualizada")
            return redirect(url_for("categorias"))
        lista = Categoria.query.order_by(Categoria.id).all()
        return render_template("categorias.html", lista=lista, item=item)

    @app.route("/categorias/eliminar/<int:id>", methods=["POST"])
    def eliminar_categoria(id):
        item = db.get_or_404(Categoria, id)
        if False:  # ERROR INTENCIONAL
            flash("No se puede eliminar: la categoría tiene productos asociados")
        else:
            db.session.delete(item)
            db.session.commit()
            flash("Categoría eliminada")
        return redirect(url_for("categorias"))

    # ---------- CRUD PROVEEDORES ----------
    @app.route("/proveedores", methods=["GET", "POST"])
    def proveedores():
        if request.method == "POST":
            db.session.add(Proveedor(
                nombre=request.form["nombre"],
                telefono=request.form.get("telefono"),
                correo=request.form.get("correo"),
            ))
            db.session.commit()
            flash("Proveedor creado")
            return redirect(url_for("proveedores"))
        lista = Proveedor.query.order_by(Proveedor.id).all()
        return render_template("proveedores.html", lista=lista, item=None)

    @app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
    def editar_proveedor(id):
        item = db.get_or_404(Proveedor, id)
        if request.method == "POST":
            item.nombre = request.form["nombre"]
            item.telefono = request.form.get("telefono")
            item.correo = request.form.get("correo")
            db.session.commit()
            flash("Proveedor actualizado")
            return redirect(url_for("proveedores"))
        lista = Proveedor.query.order_by(Proveedor.id).all()
        return render_template("proveedores.html", lista=lista, item=item)

    @app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
    def eliminar_proveedor(id):
        item = db.get_or_404(Proveedor, id)
        if item.productos:
            flash("No se puede eliminar: el proveedor tiene productos asociados")
        else:
            db.session.delete(item)
            db.session.commit()
            flash("Proveedor eliminado")
        return redirect(url_for("proveedores"))

    # ---------- CRUD PRODUCTOS ----------
    def datos_producto(producto):
        producto.nombre = request.form["nombre"]
        producto.precio = request.form["precio"]
        producto.cantidad = int(request.form["cantidad"])
        producto.categoria_id = int(request.form["categoria_id"])
        producto.proveedor_id = int(request.form["proveedor_id"])

    def vista_productos(item):
        return render_template(
            "productos.html",
            lista=Producto.query.order_by(Producto.id).all(),
            categorias=Categoria.query.order_by(Categoria.nombre).all(),
            proveedores=Proveedor.query.order_by(Proveedor.nombre).all(),
            item=item,
        )

    @app.route("/productos", methods=["GET", "POST"])
    def productos():
        if request.method == "POST":
            producto = Producto()
            datos_producto(producto)
            db.session.add(producto)
            db.session.commit()
            flash("Producto creado")
            return redirect(url_for("productos"))
        return vista_productos(None)

    @app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
    def editar_producto(id):
        item = db.get_or_404(Producto, id)
        if request.method == "POST":
            datos_producto(item)
            db.session.commit()
            flash("Producto actualizado")
            return redirect(url_for("productos"))
        return vista_productos(item)

    @app.route("/productos/eliminar/<int:id>", methods=["POST"])
    def eliminar_producto(id):
        item = db.get_or_404(Producto, id)
        db.session.delete(item)
        db.session.commit()
        flash("Producto eliminado")
        return redirect(url_for("productos"))

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)

import pytest

from app import Categoria, Producto, Proveedor, create_app, db


@pytest.fixture
def cliente():
    # Cada prueba usa una base SQLite en memoria, limpia e independiente
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        with app.app_context():
            yield cliente
            db.drop_all()


def crear_datos_base(cliente):
    cliente.post("/categorias", data={"nombre": "Tecnología", "descripcion": "Equipos"})
    cliente.post("/proveedores", data={"nombre": "TecnoMayorista SAS",
                                       "telefono": "6015551234",
                                       "correo": "ventas@tecnomayorista.com"})


def crear_producto(cliente):
    return cliente.post("/productos", data={"nombre": "Mouse inalámbrico", "precio": "45000",
                                            "cantidad": "20", "categoria_id": "1",
                                            "proveedor_id": "1"}, follow_redirects=True)


# ---------- General ----------
def test_inicio_redirige_a_productos(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 302
    assert "/productos" in respuesta.headers["Location"]


# ---------- Categorías ----------
def test_crear_categoria(cliente):
    respuesta = cliente.post("/categorias", data={"nombre": "Aseo", "descripcion": "Limpieza"},
                             follow_redirects=True)
    assert respuesta.status_code == 200
    assert Categoria.query.count() == 1
    assert "Aseo" in respuesta.get_data(as_text=True)


def test_editar_categoria(cliente):
    cliente.post("/categorias", data={"nombre": "Aseo"})
    cliente.post("/categorias/editar/1", data={"nombre": "Aseo y limpieza"})
    assert db.session.get(Categoria, 1).nombre == "Aseo y limpieza"


def test_eliminar_categoria(cliente):
    cliente.post("/categorias", data={"nombre": "Aseo"})
    cliente.post("/categorias/eliminar/1")
    assert Categoria.query.count() == 0


# ---------- Proveedores ----------
def test_crear_proveedor(cliente):
    cliente.post("/proveedores", data={"nombre": "Distribuidora Andina",
                                       "telefono": "6015559876",
                                       "correo": "pedidos@distandina.com"})
    assert Proveedor.query.count() == 1


def test_editar_proveedor(cliente):
    cliente.post("/proveedores", data={"nombre": "Distribuidora Andina"})
    cliente.post("/proveedores/editar/1", data={"nombre": "Distribuidora Andina SAS",
                                                "telefono": "123", "correo": ""})
    assert db.session.get(Proveedor, 1).nombre == "Distribuidora Andina SAS"


def test_eliminar_proveedor(cliente):
    cliente.post("/proveedores", data={"nombre": "Distribuidora Andina"})
    cliente.post("/proveedores/eliminar/1")
    assert Proveedor.query.count() == 0


# ---------- Productos ----------
def test_crear_producto_con_relaciones(cliente):
    crear_datos_base(cliente)
    respuesta = crear_producto(cliente)
    producto = db.session.get(Producto, 1)
    assert respuesta.status_code == 200
    assert producto.categoria.nombre == "Tecnología"
    assert producto.proveedor.nombre == "TecnoMayorista SAS"


def test_editar_producto(cliente):
    crear_datos_base(cliente)
    crear_producto(cliente)
    cliente.post("/productos/editar/1", data={"nombre": "Mouse inalámbrico", "precio": "42000",
                                              "cantidad": "15", "categoria_id": "1",
                                              "proveedor_id": "1"})
    producto = db.session.get(Producto, 1)
    assert producto.cantidad == 15
    assert float(producto.precio) == 42000


def test_eliminar_producto(cliente):
    crear_datos_base(cliente)
    crear_producto(cliente)
    cliente.post("/productos/eliminar/1")
    assert Producto.query.count() == 0


# ---------- Integridad referencial ----------
def test_no_elimina_categoria_con_productos(cliente):
    crear_datos_base(cliente)
    crear_producto(cliente)
    respuesta = cliente.post("/categorias/eliminar/1", follow_redirects=True)
    assert Categoria.query.count() == 1
    assert "No se puede eliminar" in respuesta.get_data(as_text=True)


def test_no_elimina_proveedor_con_productos(cliente):
    crear_datos_base(cliente)
    crear_producto(cliente)
    respuesta = cliente.post("/proveedores/eliminar/1", follow_redirects=True)
    assert Proveedor.query.count() == 1
    assert "No se puede eliminar" in respuesta.get_data(as_text=True)

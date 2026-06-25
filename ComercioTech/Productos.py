from bson import ObjectId

# CREATE → Crear producto
def crear_producto(productos):
    sku = input("SKU (ej: PROD-001): ")
    nombre = input("Nombre: ")
    categoria = input("Categoría: ")
    precio = float(input("Precio: "))
    stock = int(input("Stock: "))

    # Características dinámicas (flexibles)
    caracteristicas = {}

    while True:
        agregar = input("¿Agregar característica? (s/n): ")
        if agregar.lower() != "s":
            break

        clave = input("Nombre de la característica: ")
        valor = input("Valor: ")

        caracteristicas[clave] = valor

    producto = {
        "sku": sku,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
        "caracteristicas": caracteristicas
    }

    productos.insert_one(producto)
    print("✅ Producto creado")


# READ → Listar productos
def listar_productos(productos):
    for p in productos.find():
        print(p)


# UPDATE → Actualizar producto usando SKU
def actualizar_producto(productos):
    sku = input("SKU del producto: ")
    nuevo_precio = float(input("Nuevo precio: "))

    productos.update_one(
        {"sku": sku},
        {"$set": {"precio": nuevo_precio}}
    )

    print("✅ Producto actualizado")


# DELETE → Eliminar producto usando SKU
def eliminar_producto(productos):
    sku = input("SKU del producto: ")

    productos.delete_one({"sku": sku})

    print("🗑️ Producto eliminado")
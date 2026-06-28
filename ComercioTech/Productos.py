from bson import ObjectId

def configurar_indices(productos):
    """Crea los índices necesarios para consultas eficientes y validaciones."""
    productos.create_index("sku", unique=True)
    productos.create_index("categoria")
    productos.create_index("nombre")
    print("✅ Índices configurados correctamente.")


# CREATE → Crear producto
def crear_producto(productos):
    while True:
        sku = input("SKU (ej: PROD-001): ").strip()
        if not sku:
            print("❌ El SKU no puede estar vacío.")
            continue
        
        # Validar si el SKU ya existe
        if productos.find_one({"sku": sku}):
            print(f"❌ El SKU '{sku}' ya está registrado. Intente con otro.")
            continue
        break

    while True:
        nombre = input("Nombre: ").strip()
        if nombre:
            break
        print("❌ El nombre no puede estar vacío.")

    while True:
        categoria = input("Categoría: ").strip()
        if categoria:
            break
        print("❌ La categoría no puede estar vacía.")

    while True:
        try:
            precio = float(input("Precio: "))
            if precio <= 0:
                print("❌ El precio debe ser mayor a 0.")
                continue
            break
        except ValueError:
            print("❌ Precio inválido. Ingrese un número (ej. 199.99).")

    while True:
        try:
            stock = int(input("Stock: "))
            if stock < 0:
                print("❌ El stock no puede ser negativo.")
                continue
            break
        except ValueError:
            print("❌ Stock inválido. Ingrese un número entero.")

    # Características dinámicas (flexibles)
    caracteristicas = {}
    print("\n--- Características Adicionales ---")
    print("Agregue atributos extra (ej: voltaje, peso, color).")
    while True:
        agregar = input("¿Agregar característica? (s/n): ").strip().lower()
        if agregar != "s":
            break

        clave = input("Nombre de la característica: ").strip()
        valor = input("Valor: ").strip()
        
        if not clave or not valor:
            print("❌ Clave y valor no pueden estar vacíos.")
            continue

        # Intentar inferir el tipo de dato para hacer consultas más eficientes después
        if valor.isdigit():
            valor_final = int(valor)
        else:
            try:
                valor_final = float(valor)
            except ValueError:
                valor_final = valor

        caracteristicas[clave] = valor_final

    producto = {
        "sku": sku,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
        "caracteristicas": caracteristicas
    }

    productos.insert_one(producto)
    print("✅ Producto creado exitosamente.")


# READ → Consultar productos (optimizado)
def consultar_productos(productos):
    print("\n--- Consultar Catálogo ---")
    print("1. Mostrar todos los productos")
    print("2. Buscar por Categoría")
    print("3. Buscar por SKU")
    print("4. Buscar por Nombre")
    
    opcion = input("Seleccione una opción: ").strip()
    
    filtro = {}
    if opcion == "2":
        cat = input("Ingrese la categoría: ").strip()
        # Búsqueda insensible a mayúsculas
        filtro = {"categoria": {"$regex": f"^{cat}$", "$options": "i"}}
    elif opcion == "3":
        sku = input("Ingrese el SKU: ").strip()
        filtro = {"sku": sku}
    elif opcion == "4":
        nom = input("Ingrese el Nombre: ").strip()
        # Búsqueda que contenga la palabra (insensible a mayúsculas)
        filtro = {"nombre": {"$regex": nom, "$options": "i"}}
    elif opcion != "1":
        print("❌ Opción inválida, mostrando todos los productos por defecto.")
        
    resultados = list(productos.find(filtro))
    
    if not resultados:
        print("⚠️ No se encontraron productos.")
        return
    
    print(f"\nSe encontraron {len(resultados)} producto(s):")
    for p in resultados:
        print(f"- [{p.get('sku')}] {p.get('nombre')} | Cat: {p.get('categoria')} | Precio: ${p.get('precio')} | Stock: {p.get('stock')}")
        if p.get('caracteristicas'):
            print(f"  Características: {p.get('caracteristicas')}")

# Mantener listar_productos por compatibilidad si se usaba en otro lado
def listar_productos(productos):
    consultar_productos(productos)


# UPDATE → Actualizar producto usando SKU
def actualizar_producto(productos):
    sku = input("SKU del producto a actualizar: ").strip()
    
    producto = productos.find_one({"sku": sku})
    if not producto:
        print(f"❌ No se encontró ningún producto con SKU: {sku}")
        return

    while True:
        try:
            nuevo_precio = float(input(f"Nuevo precio (Actual: {producto['precio']}): "))
            if nuevo_precio <= 0:
                print("❌ El precio debe ser mayor a 0.")
                continue
            break
        except ValueError:
            print("❌ Precio inválido.")

    productos.update_one(
        {"sku": sku},
        {"$set": {"precio": nuevo_precio}}
    )
    print("✅ Producto actualizado")


# DELETE → Eliminar producto usando SKU
def eliminar_producto(productos):
    sku = input("SKU del producto a eliminar: ").strip()
    
    producto = productos.find_one({"sku": sku})
    if not producto:
        print(f"❌ No se encontró ningún producto con SKU: {sku}")
        return
        
    confirmacion = input(f"¿Seguro que desea eliminar el producto '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmacion == 's':
        productos.delete_one({"sku": sku})
        print("🗑️ Producto eliminado")
    else:
        print("Operación cancelada.")


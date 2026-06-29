# ============================================================
# Productos.py — CRUD de Productos
# ComercioTech — Sistema de Gestión Comercial
# ============================================================

import re
from bson import ObjectId
from pymongo import ASCENDING


# ──────────────────────────────────────────────
# ÍNDICES — Configuración automática
# ──────────────────────────────────────────────

def configurar_indices(productos) -> None:
    """
    Crea los índices necesarios para consultas eficientes.
    Se puede llamar de forma segura múltiples veces (idempotente).
    Si un índice ya existe con las mismas opciones, MongoDB lo ignora.
    """
    try:
        productos.create_index([("sku", ASCENDING)], unique=True, name="idx_sku_unique")
    except Exception:
        pass  # Índice ya existe
    try:
        productos.create_index([("categoria", ASCENDING)], name="idx_categoria")
    except Exception:
        pass
    try:
        productos.create_index([("nombre", ASCENDING)], name="idx_nombre")
    except Exception:
        pass
    print("✅ Índices de productos configurados.")


# ──────────────────────────────────────────────
# Helper de presentación
# ──────────────────────────────────────────────

def _mostrar_producto(producto: dict) -> None:
    """Imprime la ficha de un producto de forma formateada."""
    print("\n" + "─" * 50)
    print(f"  SKU       : {producto.get('sku')}")
    print(f"  Nombre    : {producto.get('nombre')}")
    print(f"  Categoría : {producto.get('categoria')}")
    print(f"  Precio    : ${producto.get('precio', 0):,.2f}")
    print(f"  Stock     : {producto.get('stock', 0)} unidades")
    caract = producto.get('caracteristicas', {})
    if caract:
        print("  Características:")
        for k, v in caract.items():
            print(f"    • {k}: {v}")
    print("─" * 50)


# ──────────────────────────────────────────────
# CREATE → Registrar producto(s) en lote
# ──────────────────────────────────────────────

def crear_producto(productos) -> None:
    """
    Registra uno o más productos en la base de datos.
    Crea los índices automáticamente antes de insertar.
    """
    # Asegurar que los índices existen antes de cualquier inserción
    configurar_indices(productos)

    print("\n─── REGISTRAR NUEVO(S) PRODUCTO(S) ───")
    nuevos_productos = []

    while True:
        # SKU — obligatorio y único
        while True:
            sku = input("SKU (ej: PROD-001): ").strip().upper()
            if not sku:
                print("❌ El SKU no puede estar vacío.")
                continue
            if productos.find_one({"sku": sku}) or any(p['sku'] == sku for p in nuevos_productos):
                print(f"❌ El SKU '{sku}' ya está registrado.")
                continue
            break

        # Nombre — obligatorio
        while True:
            nombre = input("Nombre del producto: ").strip()
            if nombre:
                break
            print("❌ El nombre es obligatorio.")

        # Categoría — obligatoria
        while True:
            categoria = input("Categoría: ").strip()
            if categoria:
                break
            print("❌ La categoría es obligatoria.")

        # Precio — número positivo
        while True:
            try:
                precio_str = input("Precio: ").strip().replace(",", ".")
                precio = float(precio_str)
                if precio <= 0:
                    print("❌ El precio debe ser mayor a 0.")
                    continue
                break
            except ValueError:
                print("❌ Precio inválido. Ingrese un número (ej: 19.99).")

        # Stock — entero no negativo
        while True:
            try:
                stock = int(input("Stock inicial: "))
                if stock < 0:
                    print("❌ El stock no puede ser negativo.")
                    continue
                break
            except ValueError:
                print("❌ Stock inválido. Ingrese un número entero.")

        # Características dinámicas (atributos flexibles)
        caracteristicas = {}
        print("\n  [Características adicionales — ej: voltaje, peso, color]")
        while True:
            agregar = input("  ¿Agregar característica? (s/n): ").strip().lower()
            if agregar != "s":
                break
            clave = input("  Nombre del atributo: ").strip()
            valor = input("  Valor: ").strip()
            if not clave or not valor:
                print("  ❌ Atributo y valor no pueden estar vacíos.")
                continue
            # Inferir tipo de dato para consultas eficientes
            if valor.isdigit():
                valor_final = int(valor)
            else:
                try:
                    valor_final = float(valor.replace(",", "."))
                except ValueError:
                    valor_final = valor
            caracteristicas[clave] = valor_final

        producto = {
            "sku":            sku,
            "nombre":         nombre,
            "categoria":      categoria,
            "precio":         precio,
            "stock":          stock,
            "caracteristicas": caracteristicas
        }
        nuevos_productos.append(producto)
        print("✅ Producto añadido al lote temporal.")

        otro = input("¿Registrar otro producto? (s/n): ").strip().lower()
        if otro != 's':
            break

    if nuevos_productos:
        try:
            resultado = productos.insert_many(nuevos_productos, ordered=False)
            print(f"✅ {len(resultado.inserted_ids)} producto(s) guardado(s) exitosamente.")
        except Exception as e:
            print(f"❌ Error al guardar el lote: {e}")


# ──────────────────────────────────────────────
# READ → Consultar catálogo de productos
# ──────────────────────────────────────────────

def consultar_productos(productos) -> None:
    """Consulta productos con múltiples criterios de búsqueda."""
    print("\n─── CONSULTAR CATÁLOGO ───")
    print("1. Mostrar todos")
    print("2. Buscar por Categoría")
    print("3. Buscar por SKU")
    print("4. Buscar por Nombre")

    opcion = input("Opción: ").strip()
    filtro = {}

    if opcion == "2":
        cat = input("Categoría: ").strip()
        filtro = {"categoria": {"$regex": f"^{re.escape(cat)}$", "$options": "i"}}
    elif opcion == "3":
        sku = input("SKU: ").strip().upper()
        filtro = {"sku": sku}
    elif opcion == "4":
        nom = input("Nombre (o parte del nombre): ").strip()
        filtro = {"nombre": {"$regex": re.escape(nom), "$options": "i"}}
    elif opcion != "1":
        print("❌ Opción inválida, mostrando todos los productos.")

    resultados = list(productos.find(filtro).sort("nombre", 1))

    if not resultados:
        print("⚠️ No se encontraron productos con ese criterio.")
        return

    print(f"\n📦 {len(resultados)} producto(s) encontrado(s):")
    for p in resultados:
        _mostrar_producto(p)


# Alias de compatibilidad
def listar_productos(productos) -> None:
    consultar_productos(productos)


# ──────────────────────────────────────────────
# UPDATE → Actualizar producto (Multi-campo)
# ──────────────────────────────────────────────

def actualizar_producto(productos) -> None:
    """Actualiza campos individuales de un producto existente."""
    print("\n─── ACTUALIZAR PRODUCTO ───")
    sku = input("SKU del producto a actualizar: ").strip().upper()

    producto = productos.find_one({"sku": sku})
    if not producto:
        print(f"❌ No se encontró ningún producto con SKU: {sku}")
        return

    while True:
        print(f"\n  Editando: {producto.get('nombre')} (SKU: {producto.get('sku')})")
        print("  1. Actualizar Nombre")
        print("  2. Actualizar Categoría")
        print("  3. Actualizar Precio")
        print("  4. Actualizar Stock")
        print("  5. Agregar/Actualizar Característica")
        print("  0. Guardar y salir")
        opcion = input("  Opción: ").strip()

        if opcion == '0':
            print("✅ Cambios guardados.")
            break

        update_query = None

        if opcion == '1':
            while True:
                nuevo_valor = input("Nuevo nombre: ").strip()
                if nuevo_valor:
                    break
                print("❌ El nombre no puede estar vacío.")
            update_query = {"$set": {"nombre": nuevo_valor}}
            producto['nombre'] = nuevo_valor

        elif opcion == '2':
            while True:
                nuevo_valor = input("Nueva categoría: ").strip()
                if nuevo_valor:
                    break
                print("❌ La categoría no puede estar vacía.")
            update_query = {"$set": {"categoria": nuevo_valor}}
            producto['categoria'] = nuevo_valor

        elif opcion == '3':
            while True:
                try:
                    nuevo_valor = float(input(f"Nuevo precio (actual: ${producto['precio']:,.2f}): ").replace(",", "."))
                    if nuevo_valor <= 0:
                        print("❌ El precio debe ser mayor a 0.")
                        continue
                    break
                except ValueError:
                    print("❌ Precio inválido.")
            update_query = {"$set": {"precio": nuevo_valor}}
            producto['precio'] = nuevo_valor

        elif opcion == '4':
            while True:
                try:
                    nuevo_valor = int(input(f"Nuevo stock (actual: {producto['stock']}): "))
                    if nuevo_valor < 0:
                        print("❌ El stock no puede ser negativo.")
                        continue
                    break
                except ValueError:
                    print("❌ Stock inválido.")
            update_query = {"$set": {"stock": nuevo_valor}}
            producto['stock'] = nuevo_valor

        elif opcion == '5':
            clave = input("Nombre del atributo: ").strip()
            valor = input("Valor: ").strip()
            if not clave or not valor:
                print("❌ Atributo y valor no pueden estar vacíos.")
                continue
            if valor.isdigit():
                valor_final = int(valor)
            else:
                try:
                    valor_final = float(valor.replace(",", "."))
                except ValueError:
                    valor_final = valor
            update_query = {"$set": {f"caracteristicas.{clave}": valor_final}}

        else:
            print("❌ Opción inválida.")
            continue

        if update_query:
            productos.update_one({"_id": producto["_id"]}, update_query)
            print("🔄 Campo actualizado correctamente.")


# ──────────────────────────────────────────────
# DELETE → Eliminar producto (con protección)
# ──────────────────────────────────────────────

def eliminar_producto(productos, pedidos=None) -> None:
    """
    Elimina un producto. Si está referenciado en pedidos existentes,
    muestra una advertencia antes de proceder.

    Args:
        productos: Colección MongoDB de productos.
        pedidos  : Colección MongoDB de pedidos (para verificar dependencias).
    """
    print("\n─── ELIMINAR PRODUCTO ───")
    sku = input("SKU del producto a eliminar: ").strip().upper()

    producto = productos.find_one({"sku": sku})
    if not producto:
        print(f"❌ No se encontró ningún producto con SKU: {sku}")
        return

    # Verificar si el producto aparece en pedidos
    if pedidos is not None:
        en_pedidos = pedidos.count_documents({"productos.sku": sku})
        if en_pedidos > 0:
            print(f"⚠️  ADVERTENCIA: Este producto está incluido en {en_pedidos} pedido(s).")
            print("   Eliminar el producto no afectará los pedidos históricos.")
            confirm_extra = input("   ¿Desea continuar de todas formas? (s/n): ").strip().lower()
            if confirm_extra != 's':
                print("Operación cancelada.")
                return

    confirmacion = input(f"¿Seguro que desea eliminar '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmacion == 's':
        productos.delete_one({"sku": sku})
        print("🗑️  Producto eliminado exitosamente.")
    else:
        print("Operación cancelada.")

# ============================================================
# Pedidos.py — CRUD de Pedidos
# ComercioTech — Sistema de Gestión Comercial
# ============================================================
from datetime import datetime

# ──────────────────────────────────────────────
# Helper interno
# ──────────────────────────────────────────────

def _validar_fecha(fecha_str: str) -> bool:
    """Valida que la cadena tenga el formato YYYY-MM-DD."""
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ──────────────────────────────────────────────
# CREATE → Crear pedido (Snapshot completo)
# ──────────────────────────────────────────────

def crear_pedido(pedidos, clientes, productos) -> None:
    """
    Crea un nuevo pedido con snapshot del cliente y productos.
    Valida duplicados de número de pedido y descuenta el stock
    de cada producto al confirmar la operación.
    """
    print("\n─── CREAR NUEVO PEDIDO ───")

    # Número de pedido — obligatorio y único
    while True:
        numero = input("Número de pedido (ej: PED-001): ").strip().upper()
        if not numero:
            print("❌ El número de pedido es obligatorio.")
            continue
        if pedidos.find_one({"numeroPedido": numero}):
            print(f"❌ Ya existe un pedido con el número '{numero}'.")
            continue
        break

    # Fecha — por defecto hoy
    while True:
        fecha_input = input(f"Fecha (YYYY-MM-DD) [Enter = hoy {datetime.now().strftime('%Y-%m-%d')}]: ").strip()
        if not fecha_input:
            fecha = datetime.now().strftime("%Y-%m-%d")
            break
        if _validar_fecha(fecha_input):
            fecha = fecha_input
            break
        print("❌ Formato de fecha inválido. Use YYYY-MM-DD (ej: 2025-12-31).")

    # Cliente — snapshot completo para historial inmutable
    while True:
        rut = input("RUT del cliente: ").strip()
        if not rut:
            print("❌ El RUT es obligatorio.")
            continue
        cliente_db = clientes.find_one({"rut": rut})
        if cliente_db:
            break
        print("❌ Cliente no encontrado. Verifique el RUT o regístrelo primero.")

    cliente_snapshot = {
        "rut":        cliente_db.get("rut"),
        "nombre":     cliente_db.get("nombre"),
        "email":      cliente_db.get("email"),
        "telefono":   cliente_db.get("telefono"),
        "direcciones": cliente_db.get("direcciones", [])
    }

    # Productos — snapshot + validación de stock
    productos_lista = []
    total = 0

    while True:
        agregar = input("¿Agregar producto al pedido? (s/n): ").strip().lower()
        if agregar != "s":
            if not productos_lista:
                print("❌ El pedido debe tener al menos un producto.")
                continue
            break

        sku = input("  SKU del producto: ").strip().upper()
        producto_db = productos.find_one({"sku": sku})
        if not producto_db:
            print(f"  ❌ Producto con SKU '{sku}' no encontrado.")
            continue

        stock_disponible = producto_db.get("stock", 0)
        print(f"  → {producto_db.get('nombre')} | Precio: ${producto_db.get('precio', 0):,.2f} | Stock: {stock_disponible}")

        while True:
            try:
                cantidad = int(input(f"  Cantidad: "))
                if cantidad <= 0:
                    print("  ❌ La cantidad debe ser mayor a 0.")
                    continue
                if cantidad > stock_disponible:
                    print(f"  ❌ Stock insuficiente. Disponible: {stock_disponible}")
                    continue
                break
            except ValueError:
                print("  ❌ Cantidad inválida.")

        precio_actual = producto_db.get("precio", 0)
        subtotal = round(precio_actual * cantidad, 2)
        total = round(total + subtotal, 2)

        productos_lista.append({
            "sku":            producto_db.get("sku"),
            "nombre":         producto_db.get("nombre"),
            "categoria":      producto_db.get("categoria"),
            "precio_unitario": precio_actual,
            "cantidad":       cantidad,
            "subtotal":       subtotal,
            "caracteristicas": producto_db.get("caracteristicas", {})
        })
        print(f"  ✅ Agregado: {producto_db.get('nombre')} x{cantidad} — Subtotal: ${subtotal:,.2f}")

    # Estado de pago
    print("\nEstado de pago:")
    print("  1. Pendiente  2. Pagado  3. Anulado")
    estados_pago = {"1": "Pendiente", "2": "Pagado", "3": "Anulado"}
    op_pago = input("Opción [1]: ").strip()
    estado_pago = estados_pago.get(op_pago, "Pendiente")

    # Estado de despacho
    print("Estado de despacho:")
    print("  1. En preparación  2. Enviado  3. Entregado  4. Anulado")
    estados_despacho = {"1": "En preparación", "2": "Enviado", "3": "Entregado", "4": "Anulado"}
    op_despacho = input("Opción [1]: ").strip()
    estado_despacho = estados_despacho.get(op_despacho, "En preparación")

    pedido = {
        "numeroPedido":    numero,
        "cliente_id":      cliente_db["_id"],   # Referencia para consultas por cliente
        "fechaPedido":     fecha,
        "cliente":         cliente_snapshot,
        "productos":       productos_lista,
        "total":           total,
        "estadoPago":      estado_pago,
        "estadoDespacho":  estado_despacho,
        "creadoEn":        datetime.now().isoformat()
    }

    try:
        pedidos.insert_one(pedido)

        # Descontar stock de cada producto
        for item in productos_lista:
            productos.update_one(
                {"sku": item["sku"]},
                {"$inc": {"stock": -item["cantidad"]}}
            )

        print(f"\n✅ Pedido {numero} creado exitosamente.")
        print(f"   Cliente : {cliente_snapshot['nombre']}")
        print(f"   Productos: {len(productos_lista)} ítem(s)")
        print(f"   Total    : ${total:,.2f}")
        print(f"   Pago     : {estado_pago} | Despacho: {estado_despacho}")
    except Exception as e:
        print(f"❌ Error al guardar el pedido: {e}")


# ──────────────────────────────────────────────
# READ → Listar pedidos históricos
# ──────────────────────────────────────────────

def listar_pedidos(pedidos) -> None:
    """Lista todos los pedidos registrados, ordenados por fecha descendente."""
    print("\n─── HISTÓRICO DE PEDIDOS ───")
    lista = list(pedidos.find().sort("fechaPedido", -1))

    if not lista:
        print("⚠️ No hay pedidos registrados.")
        return

    print(f"\n📋 {len(lista)} pedido(s) encontrado(s):\n")
    for p in lista:
        print("═" * 50)
        print(f"  N° Pedido  : {p.get('numeroPedido')}")
        print(f"  Fecha      : {p.get('fechaPedido', 'N/A')}")
        print(f"  Pago       : {p.get('estadoPago', 'N/A')}  |  Despacho: {p.get('estadoDespacho', 'N/A')}")

        c = p.get('cliente', {})
        print(f"  Cliente    : {c.get('nombre', 'N/A')} (RUT: {c.get('rut', 'N/A')})")

        print("  Productos  :")
        for prod in p.get('productos', []):
            print(f"    • [{prod.get('sku')}] {prod.get('nombre')} "
                  f"x{prod.get('cantidad')} "
                  f"@ ${prod.get('precio_unitario', 0):,.2f} "
                  f"= ${prod.get('subtotal', 0):,.2f}")

        print(f"  Total      : ${p.get('total', 0):,.2f}")
    print("═" * 50)


# ──────────────────────────────────────────────
# UPDATE → Actualizar estado de un pedido
# ──────────────────────────────────────────────

def actualizar_estado_pedido(pedidos) -> None:
    """Actualiza el estado de pago y/o despacho de un pedido existente."""
    print("\n─── ACTUALIZAR ESTADO DE PEDIDO ───")
    numero = input("Número de pedido: ").strip().upper()

    pedido = pedidos.find_one({"numeroPedido": numero})
    if not pedido:
        print(f"❌ No se encontró el pedido N° {numero}.")
        return

    print(f"\n  Pedido: {numero}  |  Cliente: {pedido.get('cliente', {}).get('nombre', 'N/A')}")
    print(f"  Pago actual    : {pedido.get('estadoPago', 'N/A')}")
    print(f"  Despacho actual: {pedido.get('estadoDespacho', 'N/A')}")

    updates = {}

    print("\nNuevo estado de pago (Enter para mantener actual):")
    print("  1. Pendiente  2. Pagado  3. Anulado")
    estados_pago = {"1": "Pendiente", "2": "Pagado", "3": "Anulado"}
    op = input("Opción: ").strip()
    if op in estados_pago:
        updates["estadoPago"] = estados_pago[op]

    print("Nuevo estado de despacho (Enter para mantener actual):")
    print("  1. En preparación  2. Enviado  3. Entregado  4. Anulado")
    estados_despacho = {"1": "En preparación", "2": "Enviado", "3": "Entregado", "4": "Anulado"}
    op = input("Opción: ").strip()
    if op in estados_despacho:
        updates["estadoDespacho"] = estados_despacho[op]

    if updates:
        updates["actualizadoEn"] = datetime.now().isoformat()
        pedidos.update_one({"numeroPedido": numero}, {"$set": updates})
        print("🔄 Estado del pedido actualizado correctamente.")
    else:
        print("ℹ️  No se realizaron cambios.")


# ──────────────────────────────────────────────
# DELETE → Eliminar pedido (con confirmación y restauración de stock)
# ──────────────────────────────────────────────

def eliminar_pedido(pedidos, productos=None) -> None:
    """
    Elimina un pedido existente.
    Verifica que el pedido exista, solicita confirmación y,
    si se provee la colección de productos, restaura el stock.

    Args:
        pedidos  : Colección MongoDB de pedidos.
        productos: Colección MongoDB de productos (para restaurar stock).
    """
    print("\n─── ELIMINAR PEDIDO ───")
    numero = input("Número de pedido a eliminar: ").strip().upper()

    pedido = pedidos.find_one({"numeroPedido": numero})
    if not pedido:
        print(f"❌ No se encontró ningún pedido con el número '{numero}'.")
        return

    c = pedido.get('cliente', {})
    print(f"\n  Pedido N° {numero}")
    print(f"  Cliente: {c.get('nombre', 'N/A')} | Fecha: {pedido.get('fechaPedido', 'N/A')}")
    print(f"  Total  : ${pedido.get('total', 0):,.2f}")

    if productos is not None:
        print("  ⚠️  Nota: El stock de los productos será restaurado al eliminar.")

    confirmacion = input("\n¿Confirma la eliminación? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Operación cancelada.")
        return

    try:
        pedidos.delete_one({"numeroPedido": numero})

        # Restaurar stock de cada producto
        if productos is not None:
            for item in pedido.get("productos", []):
                productos.update_one(
                    {"sku": item.get("sku")},
                    {"$inc": {"stock": item.get("cantidad", 0)}}
                )
            print("📦 Stock restaurado correctamente.")

        print(f"🗑️  Pedido N° {numero} eliminado exitosamente.")
    except Exception as e:
        print(f"❌ Error al eliminar el pedido: {e}")
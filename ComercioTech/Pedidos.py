# CREATE → Crear pedido (Snapshot completo)
def crear_pedido(pedidos, clientes, productos):
    numero = input("Número de pedido: ").strip()
    fecha = input("Fecha (YYYY-MM-DD): ").strip()

    # Cliente (Snapshot Completo)
    rut = input("RUT cliente: ").strip()
    cliente_db = clientes.find_one({"rut": rut})
    if not cliente_db:
        print("❌ Cliente no encontrado. Registre al cliente primero.")
        return
    
    cliente_snapshot = {
        "rut": cliente_db.get("rut"),
        "nombre": cliente_db.get("nombre"),
        "email": cliente_db.get("email"),
        "telefono": cliente_db.get("telefono"),
        "direcciones": cliente_db.get("direcciones", [])
    }

    productos_lista = []
    total = 0

    # Productos (Snapshot Completo)
    while True:
        agregar = input("¿Agregar producto? (s/n): ").strip().lower()
        if agregar != "s":
            break

        sku = input("SKU: ").strip()
        producto_db = productos.find_one({"sku": sku})
        if not producto_db:
            print("❌ Producto no encontrado.")
            continue
            
        try:
            cantidad = int(input(f"Cantidad de '{producto_db.get('nombre')}': "))
            if cantidad <= 0:
                print("❌ La cantidad debe ser mayor a 0.")
                continue
        except ValueError:
            print("❌ Cantidad inválida.")
            continue
            
        precio_actual = producto_db.get("precio", 0)
        subtotal = precio_actual * cantidad
        total += subtotal

        producto_snapshot = {
            "sku": producto_db.get("sku"),
            "nombre": producto_db.get("nombre"),
            "categoria": producto_db.get("categoria"),
            "precio_unitario": precio_actual,
            "cantidad": cantidad,
            "subtotal": subtotal,
            "caracteristicas": producto_db.get("caracteristicas", {})
        }
        productos_lista.append(producto_snapshot)

    if not productos_lista:
        print("❌ El pedido debe tener al menos un producto.")
        return

    estado_pago = input("Estado de pago: ").strip()
    estado_despacho = input("Estado de despacho: ").strip()
    
    pedido = {
        "numeroPedido": numero,
        "cliente_id": cliente_db["_id"],  # Mantener referencia para consultar_pedidos_cliente
        "fechaPedido": fecha,
        "cliente": cliente_snapshot,
        "productos": productos_lista,
        "total": total,
        "estadoPago": estado_pago,
        "estadoDespacho": estado_despacho
    }

    pedidos.insert_one(pedido)
    print(f"✅ Pedido {numero} creado exitosamente.")


# READ → Listar pedidos (Consultar históricos sin alteración)
def listar_pedidos(pedidos):
    print("\n--- HISTÓRICO DE PEDIDOS ---")
    lista = list(pedidos.find())
    if not lista:
        print("No hay pedidos registrados.")
        return
        
    for p in lista:
        print(f"\nPedido N° {p.get('numeroPedido')}")
        print(f"Fecha: {p.get('fechaPedido')}")
        print(f"Estado de Pago: {p.get('estadoPago', 'N/A')} | Estado de Despacho: {p.get('estadoDespacho', 'N/A')}")
        
        c = p.get('cliente', {})
        print(f"Cliente: {c.get('nombre', 'N/A')} (RUT: {c.get('rut', 'N/A')})")
        
        print("Productos:")
        for prod in p.get('productos', []):
            print(f"  - [{prod.get('sku')}] {prod.get('nombre')} x{prod.get('cantidad')} | Precio: ${prod.get('precio_unitario')} | Subtotal: ${prod.get('subtotal')}")
            
        print(f"Total del pedido: ${p.get('total')}")
        print("-" * 40)


# DELETE → Eliminar pedido
def eliminar_pedido(pedidos):
    numero = input("Número de pedido: ")

    pedidos.delete_one({"numeroPedido": numero})

    print("🗑️ Pedido eliminado")
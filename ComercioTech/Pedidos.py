# CREATE → Crear pedido
def crear_pedido(pedidos):
    numero = input("Número de pedido: ")
    fecha = input("Fecha (YYYY-MM-DD): ")

    # Cliente embebido
    cliente = {
        "rut": input("RUT cliente: "),
        "nombre": input("Nombre cliente: ")
    }

    productos_lista = []
    total = 0

    # Agregar productos al pedido
    while True:
        agregar = input("¿Agregar producto? (s/n): ")
        if agregar.lower() != "s":
            break

        sku = input("SKU: ")
        nombre = input("Nombre producto: ")
        precio = float(input("Precio: "))
        cantidad = int(input("Cantidad: "))

        subtotal = precio * cantidad
        total += subtotal

        productos_lista.append({
            "sku": sku,
            "nombre": nombre,
            "precio": precio,
            "cantidad": cantidad
        })

    estado_pago = input("Estado de pago: ")
    estado_despacho = input("Estado de despacho: ")

    pedido = {
        "numeroPedido": numero,
        "fechaPedido": fecha,
        "cliente": cliente,
        "productos": productos_lista,
        "total": total,
        "estadoPago": estado_pago,
        "estadoDespacho": estado_despacho
    }

    pedidos.insert_one(pedido)
    print("✅ Pedido creado")


# READ → Listar pedidos
def listar_pedidos(pedidos):
    for p in pedidos.find():
        print(p)


# DELETE → Eliminar pedido
def eliminar_pedido(pedidos):
    numero = input("Número de pedido: ")

    pedidos.delete_one({"numeroPedido": numero})

    print("🗑️ Pedido eliminado")
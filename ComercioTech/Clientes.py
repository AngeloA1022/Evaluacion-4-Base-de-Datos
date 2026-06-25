from bson import ObjectId

# CREATE → Crear cliente
def crear_cliente(clientes):
    print("\n--- REGISTRAR NUEVO CLIENTE ---")
    rut = input("RUT: ").strip()
    nombre = input("Nombre: ").strip()
    email = input("Email: ").strip()
    telefono = input("Teléfono: ").strip()

    if not rut or not nombre:
        print("❌ El RUT y el Nombre son obligatorios.")
        return

    # Validar si el RUT ya existe
    if clientes.find_one({"rut": rut}):
        print(f"❌ Ya existe un cliente registrado con el RUT {rut}.")
        return

    # Lista de direcciones
    direcciones = []
    while True:
        agregar = input("¿Agregar dirección? (s/n): ").strip().lower()
        if agregar != "s":
            break

        direccion = {
            "calle": input("Calle: ").strip(),
            "ciudad": input("Ciudad: ").strip(),
            "region": input("Región: ").strip()
        }
        direcciones.append(direccion)

    cliente = {
        "rut": rut,
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "direcciones": direcciones
    }

    try:
        resultado = clientes.insert_one(cliente)
        print(f"✅ Cliente creado exitosamente. ID: {resultado.inserted_id}")
    except Exception as e:
        print(f"❌ Error al crear cliente: {e}")


# READ → Consultar datos de clientes
def consultar_cliente(clientes):
    print("\n--- CONSULTAR CLIENTES ---")
    opcion = input("1. Buscar por RUT\n2. Listar todos\nOpción: ").strip()

    if opcion == '1':
        rut = input("Ingrese el RUT del cliente: ").strip()
        cliente = clientes.find_one({"rut": rut})
        if cliente:
            _mostrar_cliente(cliente)
        else:
            print("❌ No se encontró un cliente con ese RUT.")
    elif opcion == '2':
        lista = list(clientes.find())
        if not lista:
            print("No hay clientes registrados.")
        else:
            for c in lista:
                _mostrar_cliente(c)
    else:
        print("❌ Opción inválida.")


def _mostrar_cliente(cliente):
    print("\n" + "-" * 40)
    print(f"ID: {cliente.get('_id')}")
    print(f"RUT: {cliente.get('rut')}")
    print(f"Nombre: {cliente.get('nombre')}")
    print(f"Email: {cliente.get('email', 'N/A')}")
    print(f"Teléfono: {cliente.get('telefono', 'N/A')}")
    
    direcciones = cliente.get('direcciones', [])
    if direcciones:
        print("Direcciones:")
        for idx, d in enumerate(direcciones, 1):
            print(f"  {idx}. {d.get('calle')}, {d.get('ciudad')}, {d.get('region')}")
    print("-" * 40)


# UPDATE → Actualizar información de cliente
def actualizar_cliente(clientes):
    print("\n--- ACTUALIZAR CLIENTE ---")
    rut = input("Ingrese el RUT del cliente a actualizar: ").strip()
    
    cliente = clientes.find_one({"rut": rut})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    print("¿Qué dato desea actualizar?")
    print("1. Nombre")
    print("2. Email")
    print("3. Teléfono")
    print("4. Agregar nueva dirección")
    opcion = input("Opción: ").strip()

    update_query = None
    if opcion == '1':
        nuevo_valor = input("Nuevo nombre: ").strip()
        update_query = {"$set": {"nombre": nuevo_valor}}
    elif opcion == '2':
        nuevo_valor = input("Nuevo email: ").strip()
        update_query = {"$set": {"email": nuevo_valor}}
    elif opcion == '3':
        nuevo_valor = input("Nuevo teléfono: ").strip()
        update_query = {"$set": {"telefono": nuevo_valor}}
    elif opcion == '4':
        nueva_dir = {
            "calle": input("Calle: ").strip(),
            "ciudad": input("Ciudad: ").strip(),
            "region": input("Región: ").strip()
        }
        update_query = {"$push": {"direcciones": nueva_dir}}
    else:
        print("❌ Opción inválida.")
        return

    if update_query:
        clientes.update_one({"_id": cliente["_id"]}, update_query)
        print("✅ Cliente actualizado exitosamente.")


# DELETE → Eliminar cliente
def eliminar_cliente(clientes):
    print("\n--- ELIMINAR CLIENTE ---")
    rut = input("RUT del cliente a eliminar: ").strip()

    resultado = clientes.delete_one({"rut": rut})
    
    if resultado.deleted_count > 0:
        print("🗑️ Cliente eliminado exitosamente.")
    else:
        print("❌ No se encontró ningún cliente con ese RUT.")


# ASOCIAR/CONSULTAR PEDIDOS DE CLIENTE
def consultar_pedidos_cliente(clientes, pedidos):
    print("\n--- CONSULTAR PEDIDOS DE UN CLIENTE ---")
    rut = input("Ingrese el RUT del cliente: ").strip()
    
    cliente = clientes.find_one({"rut": rut})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    cliente_id = cliente["_id"]
    # Buscamos en la colección de pedidos todos los que tengan este cliente_id
    pedidos_cliente = list(pedidos.find({"cliente_id": cliente_id}))
    
    if not pedidos_cliente:
        print(f"El cliente {cliente['nombre']} no tiene pedidos registrados.")
    else:
        print(f"\n--- Pedidos de {cliente['nombre']} ({len(pedidos_cliente)}) ---")
        for p in pedidos_cliente:
            print(f"ID Pedido: {p.get('_id')}")
            print(f"Fecha: {p.get('fecha_pedido', 'N/A')}")
            print(f"Estado: {p.get('estado', 'N/A')}")
            print(f"Total: ${p.get('total', 0)}")
            print("-" * 30)
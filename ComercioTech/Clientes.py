from bson import ObjectId

# CREATE → Crear cliente
def crear_cliente(clientes):
    rut = input("RUT: ")
    nombre = input("Nombre: ")
    email = input("Email: ")
    telefono = input("Teléfono: ")

    # Lista de direcciones (SIN código postal)
    direcciones = []

    while True:
        agregar = input("¿Agregar dirección? (s/n): ")
        if agregar.lower() != "s":
            break

        direccion = {
            "calle": input("Calle: "),
            "ciudad": input("Ciudad: "),
            "region": input("Región: ")
        }

        direcciones.append(direccion)

    cliente = {
        "rut": rut,
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "direcciones": direcciones
    }

    clientes.insert_one(cliente)
    print("✅ Cliente creado")


# READ → Listar clientes
def listar_clientes(clientes):
    for c in clientes.find():
        print(c)


# UPDATE → Actualizar cliente
def actualizar_cliente(clientes):
    id_cliente = input("ID del cliente: ")
    nuevo_email = input("Nuevo email: ")

    clientes.update_one(
        {"_id": ObjectId(id_cliente)},
        {"$set": {"email": nuevo_email}}
    )

    print("✅ Cliente actualizado")


# DELETE → Eliminar cliente
def eliminar_cliente(clientes):
    id_cliente = input("ID del cliente: ")

    clientes.delete_one({"_id": ObjectId(id_cliente)})

    print("🗑️ Cliente eliminado")
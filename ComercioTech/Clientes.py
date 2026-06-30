# ============================================================
# Clientes.py — CRUD de Clientes
# ComercioTech — Sistema de Gestión Comercial
# ============================================================
import re
from bson import ObjectId

# ──────────────────────────────────────────────
# Helpers de validación
# ──────────────────────────────────────────────

def _validar_email(email: str) -> bool:
    """Valida formato básico de email."""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(re.match(patron, email))

def _validar_telefono(telefono: str) -> bool:
    """Valida que el teléfono contenga solo dígitos, espacios, + o guiones."""
    return bool(re.match(r'^[\d\s\+\-]{7,15}$', telefono))

def _mostrar_cliente(cliente: dict) -> None:
    """Imprime la información de un cliente de forma formateada."""
    print("\n" + "─" * 45)
    print(f"  ID      : {cliente.get('_id')}")
    print(f"  RUT     : {cliente.get('rut')}")
    print(f"  Nombre  : {cliente.get('nombre')}")
    print(f"  Email   : {cliente.get('email', 'N/A')}")
    print(f"  Teléfono: {cliente.get('telefono', 'N/A')}")

    direcciones = cliente.get('direcciones', [])
    if direcciones:
        print("  Direcciones:")
        for idx, d in enumerate(direcciones, 1):
            print(f"    {idx}. {d.get('calle')}, {d.get('ciudad')}, {d.get('region')}")
    else:
        print("  Direcciones: Sin registrar")
    print("─" * 45)

# ──────────────────────────────────────────────
# CREATE → Registrar cliente(s) en lote
# ──────────────────────────────────────────────

def crear_cliente(clientes) -> None:
    """Registra uno o más clientes en la base de datos (soporte de lotes)."""
    print("\n─── REGISTRAR NUEVO(S) CLIENTE(S) ───")
    nuevos_clientes = []

    while True:
        # RUT — obligatorio y único
        while True:
            rut = input("RUT (ej: 12345678-9): ").strip()
            if not rut:
                print("❌ El RUT es obligatorio.")
                continue
            if clientes.find_one({"rut": rut}) or any(c['rut'] == rut for c in nuevos_clientes):
                print(f"❌ Ya existe un cliente con el RUT '{rut}'.")
                continue
            break

        # Nombre — obligatorio
        while True:
            nombre = input("Nombre completo: ").strip()
            if nombre:
                break
            print("❌ El nombre es obligatorio.")

        # Email — opcional, pero si se ingresa debe ser válido
        while True:
            email = input("Email (Enter para omitir): ").strip()
            if not email:
                break
            if _validar_email(email):
                break
            print("❌ Formato de email inválido (ej: usuario@dominio.com).")

        # Teléfono — opcional, pero si se ingresa debe ser válido
        while True:
            telefono = input("Teléfono (Enter para omitir): ").strip()
            if not telefono:
                break
            if _validar_telefono(telefono):
                break
            print("❌ Teléfono inválido. Use solo dígitos, +, - o espacios (7–15 caracteres).")

        # Direcciones — opcionales
        direcciones = []
        while True:
            agregar = input("¿Agregar dirección? (s/n): ").strip().lower()
            if agregar != "s":
                break
            calle   = input("  Calle  : ").strip()
            ciudad  = input("  Ciudad : ").strip()
            region  = input("  Región : ").strip()
            if calle and ciudad and region:
                direcciones.append({"calle": calle, "ciudad": ciudad, "region": region})
            else:
                print("⚠️ Dirección incompleta, no se agregó.")

        cliente = {
            "rut":        rut,
            "nombre":     nombre,
            "email":      email if email else None,
            "telefono":   telefono if telefono else None,
            "direcciones": direcciones
        }
        nuevos_clientes.append(cliente)
        print("✅ Cliente añadido al lote temporal.")

        otro = input("¿Registrar otro cliente? (s/n): ").strip().lower()
        if otro != 's':
            break

    if nuevos_clientes:
        try:
            resultado = clientes.insert_many(nuevos_clientes, ordered=False)
            print(f"✅ {len(resultado.inserted_ids)} cliente(s) guardado(s) exitosamente.")
        except Exception as e:
            print(f"❌ Error al guardar el lote: {e}")


# ──────────────────────────────────────────────
# READ → Consultar / Listar clientes
# ──────────────────────────────────────────────

def consultar_cliente(clientes) -> None:
    """Consulta uno o todos los clientes registrados."""
    print("\n─── CONSULTAR CLIENTES ───")
    print("1. Buscar por RUT")
    print("2. Listar todos")
    opcion = input("Opción: ").strip()

    if opcion == '1':
        rut = input("RUT del cliente: ").strip()
        cliente = clientes.find_one({"rut": rut})
        if cliente:
            _mostrar_cliente(cliente)
        else:
            print("❌ No se encontró ningún cliente con ese RUT.")

    elif opcion == '2':
        lista = list(clientes.find().sort("nombre", 1))
        if not lista:
            print("⚠️ No hay clientes registrados.")
        else:
            print(f"\n📋 {len(lista)} cliente(s) encontrado(s):")
            for c in lista:
                _mostrar_cliente(c)
    else:
        print("❌ Opción inválida.")


# ──────────────────────────────────────────────
# UPDATE → Actualizar datos de cliente
# ──────────────────────────────────────────────

def actualizar_cliente(clientes) -> None:
    """Actualiza campos individuales de un cliente existente."""
    print("\n─── ACTUALIZAR CLIENTE ───")
    rut = input("RUT del cliente a actualizar: ").strip()

    cliente = clientes.find_one({"rut": rut})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    while True:
        print(f"\n  Editando: {cliente.get('nombre')} (RUT: {cliente.get('rut')})")
        print("  1. Actualizar Nombre")
        print("  2. Actualizar Email")
        print("  3. Actualizar Teléfono")
        print("  4. Agregar nueva Dirección")
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
            cliente['nombre'] = nuevo_valor

        elif opcion == '2':
            while True:
                nuevo_valor = input("Nuevo email: ").strip()
                if not nuevo_valor or _validar_email(nuevo_valor):
                    break
                print("❌ Formato de email inválido.")
            update_query = {"$set": {"email": nuevo_valor if nuevo_valor else None}}
            cliente['email'] = nuevo_valor

        elif opcion == '3':
            while True:
                nuevo_valor = input("Nuevo teléfono: ").strip()
                if not nuevo_valor or _validar_telefono(nuevo_valor):
                    break
                print("❌ Teléfono inválido.")
            update_query = {"$set": {"telefono": nuevo_valor if nuevo_valor else None}}
            cliente['telefono'] = nuevo_valor

        elif opcion == '4':
            calle  = input("Calle  : ").strip()
            ciudad = input("Ciudad : ").strip()
            region = input("Región : ").strip()
            if not calle or not ciudad or not region:
                print("⚠️ Dirección incompleta, no se agregó.")
                continue
            nueva_dir = {"calle": calle, "ciudad": ciudad, "region": region}
            update_query = {"$push": {"direcciones": nueva_dir}}
        else:
            print("❌ Opción inválida.")
            continue

        if update_query:
            clientes.update_one({"_id": cliente["_id"]}, update_query)
            print("🔄 Campo actualizado correctamente.")


# ──────────────────────────────────────────────
# DELETE → Eliminar cliente (con protección)
# ──────────────────────────────────────────────

def eliminar_cliente(clientes, pedidos=None) -> None:
    """
    Elimina un cliente. Si tiene pedidos activos, muestra una advertencia
    y solicita confirmación adicional antes de proceder.

    Args:
        clientes: Colección MongoDB de clientes.
        pedidos : Colección MongoDB de pedidos (para verificar dependencias).
    """
    print("\n─── ELIMINAR CLIENTE ───")
    rut = input("RUT del cliente a eliminar: ").strip()

    cliente = clientes.find_one({"rut": rut})
    if not cliente:
        print("❌ No se encontró ningún cliente con ese RUT.")
        return

    # Verificar pedidos activos si se provee la colección
    if pedidos is not None:
        total_pedidos = pedidos.count_documents({"cliente_id": cliente["_id"]})
        if total_pedidos > 0:
            print(f"⚠️  ADVERTENCIA: Este cliente tiene {total_pedidos} pedido(s) registrado(s).")
            print("   Eliminar el cliente no borrará sus pedidos, pero sí su registro.")
            confirm_extra = input("   ¿Desea continuar de todas formas? (s/n): ").strip().lower()
            if confirm_extra != 's':
                print("Operación cancelada.")
                return

    confirmacion = input(f"¿Seguro que desea eliminar a '{cliente['nombre']}'? (s/n): ").strip().lower()
    if confirmacion == 's':
        clientes.delete_one({"rut": rut})
        print("🗑️  Cliente eliminado exitosamente.")
    else:
        print("Operación cancelada.")


# ──────────────────────────────────────────────
# EXTRA → Pedidos de un cliente
# ──────────────────────────────────────────────

def consultar_pedidos_cliente(clientes, pedidos) -> None:
    """Lista todos los pedidos asociados a un cliente específico."""
    print("\n─── PEDIDOS DE UN CLIENTE ───")
    rut = input("RUT del cliente: ").strip()

    cliente = clientes.find_one({"rut": rut})
    if not cliente:
        print("❌ Cliente no encontrado.")
        return

    pedidos_cliente = list(pedidos.find({"cliente_id": cliente["_id"]}).sort("fechaPedido", -1))

    if not pedidos_cliente:
        print(f"ℹ️  El cliente '{cliente['nombre']}' no tiene pedidos registrados.")
    else:
        print(f"\n📦 Pedidos de {cliente['nombre']} — {len(pedidos_cliente)} registro(s):")
        for p in pedidos_cliente:
            print(f"\n  N° {p.get('numeroPedido')} | Fecha: {p.get('fechaPedido', 'N/A')}")
            print(f"  Pago: {p.get('estadoPago', 'N/A')} | Despacho: {p.get('estadoDespacho', 'N/A')}")
            print(f"  Total: ${p.get('total', 0):,.2f}")
            print("  " + "─" * 40)
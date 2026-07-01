# ============================================================
# Menu.py — Controlador principal de ComercioTech
# Sistema de Gestión Comercial — MongoDB
# ============================================================

import sys
import io
import os

# Asegurar que Python encuentre los módulos del proyecto
# independientemente del directorio desde donde se ejecute
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

# Forzar encoding UTF-8 para soportar emojis en consola Windows
# IMPORTANTE: esto debe ir ANTES de cualquier import local
try:
    if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass  # En algunos entornos stdout no tiene buffer; se ignora el error

from Conexion import conectar, cerrar_conexion
from Clientes import (
    crear_cliente, consultar_cliente,
    actualizar_cliente, eliminar_cliente,
    consultar_pedidos_cliente
)
from Productos import (
    crear_producto, consultar_productos,
    actualizar_producto, eliminar_producto,
    configurar_indices
)
from Pedidos import (
    crear_pedido, listar_pedidos,
    actualizar_estado_pedido, eliminar_pedido
)


# ──────────────────────────────────────────────
# Inicializar conexión
# ──────────────────────────────────────────────

mongo_client, db = conectar()

if db is None:
    print("\n🚫 No se pudo iniciar el sistema. Verifique la conexión a MongoDB.")
    sys.exit(1)

# Colecciones
clientes  = db["clientes"]
productos = db["productos"]
pedidos   = db["pedidos"]


# ──────────────────────────────────────────────
# Menú — CLIENTES
# ──────────────────────────────────────────────

def menu_clientes():
    while True:
        print("\n" + "─" * 35)
        print("       GESTIÓN DE CLIENTES")
        print("─" * 35)
        print("  1. Registrar nuevo cliente")
        print("  2. Consultar / Listar clientes")
        print("  3. Actualizar datos de cliente")
        print("  4. Eliminar cliente")
        print("  5. Ver pedidos de un cliente")
        print("  0. Volver al menú principal")
        print("─" * 35)

        op = input("  Opción: ").strip()

        if op == "1":
            crear_cliente(clientes)
        elif op == "2":
            consultar_cliente(clientes)
        elif op == "3":
            actualizar_cliente(clientes)
        elif op == "4":
            eliminar_cliente(clientes, pedidos)       # Pasa pedidos para verificar dependencias
        elif op == "5":
            consultar_pedidos_cliente(clientes, pedidos)
        elif op == "0":
            break
        else:
            print("❌ Opción inválida.")


# ──────────────────────────────────────────────
# Menú — PRODUCTOS
# ──────────────────────────────────────────────
def menu_productos():
    while True:
        print("\n" + "─" * 35)
        print("       GESTIÓN DE PRODUCTOS")
        print("─" * 35)
        print("  1. Registrar nuevo producto")
        print("  2. Consultar / Listar productos")
        print("  3. Actualizar datos de producto")
        print("  4. Eliminar producto")
        print("  5. Configurar índices de BD")
        print("  0. Volver al menú principal")
        print("─" * 35)

        op = input("  Opción: ").strip()

        if op == "1":
            crear_producto(productos)
        elif op == "2":
            consultar_productos(productos)
        elif op == "3":
            actualizar_producto(productos)
        elif op == "4":
            eliminar_producto(productos, pedidos)     # Pasa pedidos para verificar dependencias
        elif op == "5":
            configurar_indices(productos)
        elif op == "0":
            break
        else:
            print("❌ Opción inválida.")

# ──────────────────────────────────────────────
# Menú — PEDIDOS
# ──────────────────────────────────────────────
def menu_pedidos():
    while True:
        print("\n" + "─" * 35)
        print("        GESTIÓN DE PEDIDOS")
        print("─" * 35)
        print("  1. Crear nuevo pedido")
        print("  2. Listar todos los pedidos")
        print("  3. Actualizar estado de pedido")
        print("  4. Eliminar pedido")
        print("  0. Volver al menú principal")
        print("─" * 35)

        op = input("  Opción: ").strip()

        if op == "1":
            crear_pedido(pedidos, clientes, productos)
        elif op == "2":
            listar_pedidos(pedidos)
        elif op == "3":
            actualizar_estado_pedido(pedidos)
        elif op == "4":
            eliminar_pedido(pedidos, productos)       # Pasa productos para restaurar stock
        elif op == "0":
            break
        else:
            print("❌ Opción inválida.")


# ──────────────────────────────────────────────
# Menú — PRINCIPAL
# ──────────────────────────────────────────────

def menu_principal():
    print("\n" + "═" * 40)
    print("   BIENVENIDO A COMERCIOTECH")
    print("   Sistema de Gestión Comercial")
    print("═" * 40)

    while True:
        print("\n" + "═" * 35)
        print("         MENÚ PRINCIPAL")
        print("═" * 35)
        print("  1. 👤  Clientes")
        print("  2. 📦  Productos")
        print("  3. 🛒  Pedidos")
        print("  0. 🚪  Salir")
        print("═" * 35)

        op = input("  Seleccione una opción: ").strip()

        if op == "1":
            menu_clientes()
        elif op == "2":
            menu_productos()
        elif op == "3":
            menu_pedidos()
        elif op == "0":
            print("\n👋 Cerrando sistema ComercioTech...")
            cerrar_conexion(mongo_client)
            print("✅ Hasta pronto.")
            break
        else:
            print("❌ Opción inválida.")


# ──────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────

if __name__ == "__main__":
    menu_principal()
from Conexion import conectar
from Clientes import *
from Productos import *
from Pedidos import *

# Conexión a la base de datos
db = conectar()

# Colecciones
clientes = db["clientes"]
productos = db["productos"]
pedidos = db["pedidos"]


# ===== MENÚ CLIENTES =====
def menu_clientes():
    while True:
        print("\n--- CLIENTES ---")
        print("1. Crear")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")

        op = input("Opción: ")

        if op == "1":
            crear_cliente(clientes)
        elif op == "2":
            listar_clientes(clientes)
        elif op == "3":
            actualizar_cliente(clientes)
        elif op == "4":
            eliminar_cliente(clientes)
        elif op == "0":
            break


# ===== MENÚ PRODUCTOS =====
def menu_productos():
    while True:
        print("\n--- PRODUCTOS ---")
        print("1. Crear")
        print("2. Listar")
        print("3. Actualizar")
        print("4. Eliminar")
        print("0. Volver")

        op = input("Opción: ")

        if op == "1":
            crear_producto(productos)
        elif op == "2":
            listar_productos(productos)
        elif op == "3":
            actualizar_producto(productos)
        elif op == "4":
            eliminar_producto(productos)
        elif op == "0":
            break


# ===== MENÚ PEDIDOS =====
def menu_pedidos():
    while True:
        print("\n--- PEDIDOS ---")
        print("1. Crear")
        print("2. Listar")
        print("3. Eliminar")
        print("0. Volver")

        op = input("Opción: ")

        if op == "1":
            crear_pedido(pedidos, clientes, productos)
        elif op == "2":
            listar_pedidos(pedidos)
        elif op == "3":
            eliminar_pedido(pedidos)
        elif op == "0":
            break


# ===== MENÚ PRINCIPAL =====
def menu_principal():
    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. Clientes")
        print("2. Productos")
        print("3. Pedidos")
        print("0. Salir")

        op = input("Seleccione una opción: ")

        if op == "1":
            menu_clientes()
        elif op == "2":
            menu_productos()
        elif op == "3":
            menu_pedidos()
        elif op == "0":
            print("👋 Saliendo del sistema...")
            break


# Ejecutar sistema
menu_principal()
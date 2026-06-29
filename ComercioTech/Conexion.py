# ============================================================
# Conexion.py — Módulo de conexión a MongoDB
# ComercioTech — Sistema de Gestión Comercial
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Parámetros de conexión
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME   = "ComercioTech"
TIMEOUT_MS = 3000  # 3 segundos máximo para conectar


def conectar():
    """
    Establece la conexión con MongoDB.
    Verifica la conectividad real mediante un ping antes de retornar.

    Returns:
        tuple (MongoClient, Database) si la conexión es exitosa.
        tuple (None, None) si ocurre un error.
    """
    try:
        # serverSelectionTimeoutMS evita bloqueo infinito si Mongo no responde
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=TIMEOUT_MS)

        # Verificar conectividad real con un ping al servidor
        client.admin.command("ping")

        db = client[DB_NAME]
        print("✅ Conectado a MongoDB — Base de datos:", DB_NAME)
        return client, db

    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("❌ Error: No se pudo conectar a MongoDB.")
        print("   Verifique que el servicio de MongoDB esté activo en localhost:27017")
        return None, None
    except Exception as e:
        print(f"❌ Error inesperado de conexión: {e}")
        return None, None


def cerrar_conexion(client):
    """
    Cierra la conexión con MongoDB de forma segura.

    Args:
        client (MongoClient): Instancia del cliente MongoDB a cerrar.
    """
    if client:
        client.close()
        print("🔒 Conexión a MongoDB cerrada correctamente.")
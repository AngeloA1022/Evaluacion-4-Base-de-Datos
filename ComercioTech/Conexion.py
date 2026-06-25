# Importamos la librería para conectarnos a MongoDB
from pymongo import MongoClient

def conectar():
    try:
        # Conexión al servidor local de MongoDB
        client = MongoClient("mongodb://localhost:27017/")

        # Seleccionamos la base de datos
        db = client["Comerciotech"]

        print("✅ Conectado a MongoDB")
        return db

    except Exception as e:
        print("❌ Error de conexión:", e)